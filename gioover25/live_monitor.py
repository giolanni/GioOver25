"""Read-only LIVE snapshot store and prediction evaluation for GioOver2.5.

This first-stage module accepts verified provider snapshots as CSV input.
It never writes official results or ranking histories.
"""
from __future__ import annotations

import argparse
import csv
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ("MatchDate", "LeagueId", "Home", "Away", "MatchId", "Minute",
          "HG", "AG", "Status", "LastUpdate")
KEY = ("LeagueId", "MatchDate", "Home", "Away")
FINAL = {"FINAL", "FT", "FINALE", "FINISHED"}
RUNNING = {"LIVE", "1H", "2H", "HT", "ET", "PEN"}
PENDING = {"SCHEDULED", "NS", "NOT_STARTED"}
OTHER = {"POSTPONED", "CANCELLED", "NOT_FOUND", "UNKNOWN"}
STATUSES = FINAL | RUNNING | PENDING | OTHER


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        missing = set(FIELDS) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Missing fields: {', '.join(sorted(missing))}")
        return list(reader)


def normalize(row):
    r = {k: str(row.get(k, "") or "").strip() for k in FIELDS}
    if not all(r[k] for k in KEY):
        raise ValueError("Incomplete match identity")
    try:
        datetime.strptime(r["MatchDate"], "%Y-%m-%d")
        datetime.fromisoformat(r["LastUpdate"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid MatchDate/LastUpdate") from exc
    r["Status"] = r["Status"].upper()
    if r["Status"] not in STATUSES:
        raise ValueError("Unsupported status: " + r["Status"])
    if r["HG"] or r["AG"]:
        if not r["HG"] or not r["AG"]:
            raise ValueError("Incomplete score")
        if not r["HG"].isdigit() or not r["AG"].isdigit():
            raise ValueError("Invalid score")
    if r["Status"] in FINAL | RUNNING and not (r["HG"] and r["AG"]):
        raise ValueError("Score required for running/finished match")
    return r


def save_snapshot(source: Path, destination: Path):
    """Atomic replacement; reject conflicting duplicate fixtures."""
    incoming = read_csv(source)
    rows = {}
    for index, raw in enumerate(incoming, start=2):
        try:
            row = normalize(raw)
        except ValueError as exc:
            raise ValueError(f"Line {index}: {exc}") from exc
        key = tuple(row[k].casefold() for k in KEY)
        if key in rows and rows[key] != row:
            raise ValueError(f"Conflicting duplicate at line {index}")
        rows[key] = row
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8-sig", newline="",
                                         dir=destination.parent, delete=False) as handle:
            tmp = Path(handle.name)
            writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter=";")
            writer.writeheader()
            writer.writerows(rows.values())
        os.replace(tmp, destination)
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()
    return len(rows)


def evaluate(status, hg, ag, market="Over25"):
    """LIVE goals reached => OK; KO is possible only at full time."""
    status = status.upper()
    if status not in FINAL | RUNNING or hg in ("", None) or ag in ("", None):
        return "UNKNOWN"
    goals = int(hg) + int(ag)
    won = (int(hg) > 0 and int(ag) > 0) if market.upper() == "BTTS" else (
        goals >= 2 if market.upper() == "OVER15" else goals >= 3)
    if won:
        return "OK"
    return "KO" if status in FINAL else "PENDING"


def snapshot_index(path: Path):
    if not path.exists():
        return {}
    return {tuple(r[k].casefold() for k in KEY): r for r in map(normalize, read_csv(path))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-csv", type=Path, required=True,
                        help="Verified external live snapshot with canonical fixture keys")
    parser.add_argument("--output", type=Path,
                        default=Path("data/live/partite_live.csv"))
    args = parser.parse_args()
    count = save_snapshot(args.import_csv, args.output)
    print(f"[LIVE] Imported {count} unique matches into {args.output}")
    print("[LIVE] Official result histories unchanged")


if __name__ == "__main__":
    main()
