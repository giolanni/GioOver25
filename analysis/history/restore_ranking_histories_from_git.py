"""Restore truncated ranking histories by merging healthy Git snapshots.

The September 5, 2026 ranking commit accidentally removed the CSV headers and
truncated several histories.  Later writes interpreted the first data row as a
header, so simply checking out either the old or current files loses data.

This command merges:

* the last pre-truncation snapshot;
* the headerless bridge snapshot containing the September 5 rankings;
* valid rows from the current working tree (September 6 onward).

Exact fixtures are deduplicated using the same identity used by
``ranking_history``.  Prediction fields from the old history are preserved;
newer snapshots may update result/status fields and fill missing metadata.
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import re
import subprocess
import tempfile
from collections import OrderedDict
from datetime import date, datetime
from pathlib import Path

from gioover25.ranking_history import BASE_FIELDNAMES
from gioover25.team_names import normalize_team_name


RANKING_ROOT = Path("data/storico/ranking")
DEFAULT_BASE_COMMIT = "6ccc4d64a69788b5728a42ca1ae365b411395612"
DEFAULT_BRIDGE_COMMIT = "7053374648af41e29bcf0caba0743e6aeee94345"
DEFAULT_CURRENT_COMMIT = "HEAD"
EXTRA_FIELDNAMES = [
    "Outcome",
    "HomeSourceLeagueId",
    "AwaySourceLeagueId",
    "CompetitionGroup",
]
FIELDNAMES = BASE_FIELDNAMES + EXTRA_FIELDNAMES
RESULT_FIELDS = ["HG", "AG", "Goals", "Over25", "BTTS", "Outcome"]
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DMY_DATE = re.compile(r"^\d{2}/\d{2}/\d{4}$")


def _git_blob(commit: str, path: Path) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path.as_posix()}"],
        check=True,
        capture_output=True,
    )
    return result.stdout.decode("utf-8-sig")


def _csv_records(text: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(text), delimiter=";"))


def _header_from_snapshot(text: str) -> list[str]:
    for record in _csv_records(text):
        if record and record[0].lstrip("\ufeff") == "PredictionDate":
            return [value.lstrip("\ufeff") for value in record]
    raise ValueError("Intestazione PredictionDate non trovata")


def _normalize_row(row: dict[str, str]) -> dict[str, str]:
    normalized = {field: str(row.get(field, "") or "") for field in FIELDNAMES}
    for field in ("PredictionDate", "MatchDate"):
        value = normalized[field].strip()
        if DMY_DATE.fullmatch(value):
            normalized[field] = datetime.strptime(value, "%d/%m/%Y").date().isoformat()
    if not normalized["Outcome"]:
        normalized["Outcome"] = normalized["Over25"]
    return normalized


def _parse_snapshot(text: str, header: list[str]) -> list[dict[str, str]]:
    """Read valid physical data rows, ignoring conflict markers and headers."""
    rows = []
    for record in _csv_records(text):
        if not record:
            continue
        first = record[0].lstrip("\ufeff").strip()
        if not (ISO_DATE.fullmatch(first) or DMY_DATE.fullmatch(first)):
            continue
        values = record[: len(header)]
        values.extend([""] * (len(header) - len(values)))
        row = dict(zip(header, values))
        rows.append(_normalize_row(row))
    return rows


def _parse_current(text: str) -> list[dict[str, str]]:
    """Extract only rows stored in the canonical prefix of a malformed file."""
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    rows = []
    for raw in reader:
        prediction_date = str(raw.get("PredictionDate", "") or "").strip()
        if not ISO_DATE.fullmatch(prediction_date):
            continue
        rows.append(_normalize_row(raw))
    return rows


def _text(value: str) -> str:
    return str(value or "").strip()


def _key(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    league_id = _text(row["LeagueId"])
    match_date = _text(row["MatchDate"])
    prediction_date = _text(row["PredictionDate"])
    home = normalize_team_name(league_id, row["Home"])
    away = normalize_team_name(league_id, row["Away"])
    if match_date:
        return ("MATCH_DATE", league_id, match_date, home, away)
    return ("PREDICTION_DATE", league_id, prediction_date, home, away)


def _has_result(row: dict[str, str]) -> bool:
    return bool(_text(row["HG"]) and _text(row["AG"]))


def _near_duplicate_key(
    merged: OrderedDict[tuple, dict[str, str]],
    fixture_index: dict[tuple[str, str, str], list[tuple]],
    row: dict[str, str],
) -> tuple | None:
    match_date = _text(row["MatchDate"])
    if not match_date:
        return None

    candidate_date = date.fromisoformat(match_date)
    league_id = _text(row["LeagueId"])
    home = normalize_team_name(league_id, row["Home"])
    away = normalize_team_name(league_id, row["Away"])

    for key in fixture_index.get((league_id, home, away), []):
        existing = merged[key]
        existing_date_text = _text(existing["MatchDate"])
        if not existing_date_text:
            continue
        if _text(existing["LeagueId"]) != league_id:
            continue
        if normalize_team_name(league_id, existing["Home"]) != home:
            continue
        if normalize_team_name(league_id, existing["Away"]) != away:
            continue
        existing_date = date.fromisoformat(existing_date_text)
        if abs((candidate_date - existing_date).days) >= 3:
            continue

        # Never collapse two completed fixtures with discordant scores.
        if (
            _has_result(existing)
            and _has_result(row)
            and (existing["HG"], existing["AG"]) != (row["HG"], row["AG"])
        ):
            continue
        return key
    return None


def _merge_newer(existing: dict[str, str], newer: dict[str, str]) -> None:
    """Preserve the original prediction and overlay newer factual information."""
    if _has_result(newer):
        for field in RESULT_FIELDS:
            existing[field] = newer[field]
        existing["MatchStatus"] = "FINAL"
    elif not _has_result(existing):
        status = _text(newer["MatchStatus"]).upper()
        if status in {"FINAL", "POSTPONED"}:
            existing["MatchStatus"] = status

    for field in FIELDNAMES:
        if not _text(existing[field]) and _text(newer[field]):
            existing[field] = newer[field]

    if not existing["Outcome"]:
        existing["Outcome"] = existing["Over25"]


def _deduplicate(
    sources: list[list[dict[str, str]]],
) -> tuple[list[dict[str, str]], int, int, list[tuple]]:
    merged: OrderedDict[tuple, dict[str, str]] = OrderedDict()
    fixture_index: dict[tuple[str, str, str], list[tuple]] = {}
    duplicate_count = 0
    near_duplicate_count = 0
    result_conflicts = []

    for source_index, rows in enumerate(sources):
        for row in rows:
            key = _key(row)
            existing = merged.get(key)
            if existing is None:
                near_key = None
                if source_index > 0:
                    near_key = _near_duplicate_key(merged, fixture_index, row)
                if near_key is None:
                    merged[key] = dict(row)
                    league_id = _text(row["LeagueId"])
                    fixture_key = (
                        league_id,
                        normalize_team_name(league_id, row["Home"]),
                        normalize_team_name(league_id, row["Away"]),
                    )
                    fixture_index.setdefault(fixture_key, []).append(key)
                    continue

                near_duplicate_count += 1
                existing = merged[near_key]
                if _has_result(row) and not _has_result(existing):
                    existing["MatchDate"] = row["MatchDate"]
                    league_id = _text(existing["LeagueId"])
                    fixture_key = (
                        league_id,
                        normalize_team_name(league_id, existing["Home"]),
                        normalize_team_name(league_id, existing["Away"]),
                    )
                    replacement_key = _key(existing)
                    del merged[near_key]
                    merged[replacement_key] = existing
                    fixture_keys = fixture_index[fixture_key]
                    fixture_keys[fixture_keys.index(near_key)] = replacement_key

            duplicate_count += 1
            if (
                _has_result(existing)
                and _has_result(row)
                and (existing["HG"], existing["AG"]) != (row["HG"], row["AG"])
            ):
                result_conflicts.append(
                    (key, existing["HG"], existing["AG"], row["HG"], row["AG"])
                )
                continue
            _merge_newer(existing, row)

    rows = list(merged.values())
    rows.sort(
        key=lambda row: (
            _text(row["PredictionDate"]),
            _text(row["MatchDate"]),
            _text(row["LeagueId"]),
            _text(row["Home"]),
            _text(row["Away"]),
        )
    )
    return rows, duplicate_count, near_duplicate_count, result_conflicts


def _write(path: Path, rows: list[dict[str, str]]) -> None:
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8-sig",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            writer = csv.DictWriter(
                handle,
                fieldnames=FIELDNAMES,
                delimiter=";",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def restore_engine(
    path: Path,
    base_commit: str,
    bridge_commit: str,
    current_commit: str,
    apply_changes: bool,
) -> dict[str, int | str]:
    base_text = _git_blob(base_commit, path)
    header = _header_from_snapshot(base_text)
    base_rows = _parse_snapshot(base_text, header)
    bridge_rows = _parse_snapshot(_git_blob(bridge_commit, path), header)
    current_rows = _parse_current(_git_blob(current_commit, path))
    rows, duplicates, near_duplicates, conflicts = _deduplicate(
        [base_rows, bridge_rows, current_rows]
    )

    if conflicts:
        raise RuntimeError(
            f"{path}: {len(conflicts)} conflitti HG/AG; primo conflitto: "
            f"{conflicts[0]}"
        )
    if len(rows) < len(base_rows):
        raise RuntimeError(
            f"{path}: il ripristino ridurrebbe {len(base_rows)} righe a {len(rows)}"
        )
    if apply_changes:
        _write(path, rows)

    return {
        "engine": path.parent.name,
        "base": len(base_rows),
        "bridge": len(bridge_rows),
        "current": len(current_rows),
        "duplicates": duplicates,
        "near_duplicates": near_duplicates,
        "restored": len(rows),
        "added": len(rows) - len(base_rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-commit", default=DEFAULT_BASE_COMMIT)
    parser.add_argument("--bridge-commit", default=DEFAULT_BRIDGE_COMMIT)
    parser.add_argument("--current-commit", default=DEFAULT_CURRENT_COMMIT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    paths = sorted(RANKING_ROOT.glob("*/storico_ranking_*.csv"))
    if not paths:
        raise SystemExit("Nessuno storico ranking trovato")

    print(
        "Engine;Base;Bridge;Current;Duplicates;NearDuplicates;Restored;Added"
    )
    for path in paths:
        stats = restore_engine(
            path,
            base_commit=args.base_commit,
            bridge_commit=args.bridge_commit,
            current_commit=args.current_commit,
            apply_changes=args.apply,
        )
        print(
            "{engine};{base};{bridge};{current};{duplicates};"
            "{near_duplicates};{restored};{added}".format(**stats)
        )

    if not args.apply:
        print("Dry run: usare --apply per scrivere i file ricostruiti.")


if __name__ == "__main__":
    main()
