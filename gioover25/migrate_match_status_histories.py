"""
===============================================================================
GioOver2.5 - migrate_match_status_histories.py
===============================================================================

SCOPO
-----
Aggiungere e bonificare la colonna MatchStatus in tutti gli storici ranking:

    data/storico/ranking/*/storico_ranking_*.csv

VALORI
------
- FINAL: HG e AG sono valorizzati;
- POSTPONED: prediction senza risultato corrispondente a una partita presente
  in data/storico/partite_posticipate.csv;
- SCHEDULED: prediction senza risultato e non presente nel registro rinviate;
- CANCELLED: preservato se già presente o specificato tramite override.

OVERRIDE MANUALI
----------------
Per casi storici già rimossi dal registro delle rinviate, è possibile creare:

    data/input_risultati/match_status_overrides.csv

Formato:

    Engine;LeagueId;PredictionDate;MatchDate;Home;Away;MatchStatus

PredictionDate dovrebbe essere valorizzata. Se lo stesso record storico è
presente più volte, l'override viene applicato a tutte le copie identiche.
La migrazione fallisce soltanto se non trova alcuna riga oppure se un override
senza PredictionDate individua più righe.

SICUREZZA
---------
- senza --apply: dry run;
- con --apply: crea backup e modifica i file solo se Errors=0;
- non elimina righe;
- non modifica risultati o driver.

USO
---
    python -m gioover25.migrate_match_status_histories
    python -m gioover25.migrate_match_status_histories --apply
===============================================================================
"""

from __future__ import annotations

import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

HISTORY_ROOT = Path("data/storico/ranking")
POSTPONED_FILE = Path("data/storico/partite_posticipate.csv")
OVERRIDES_FILE = Path("data/input_risultati/match_status_overrides.csv")
DEBUG_DIR = Path("data/debug/migrate_match_status")
BACKUP_DIR = Path("data/backup/migrate_match_status")
VALID_STATUSES = {"SCHEDULED", "POSTPONED", "FINAL", "CANCELLED"}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _team(value: Any) -> str:
    return " ".join(_text(value).casefold().split())


def _read_csv(path: Path) -> tuple[list[dict], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        return list(reader), list(reader.fieldnames or [])


def _write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def _postponed_index() -> dict[tuple[str, str, str], list[dict]]:
    if not POSTPONED_FILE.exists():
        return {}

    rows, _ = _read_csv(POSTPONED_FILE)
    index = {}
    for row in rows:
        key = (
            _text(row.get("LeagueId")),
            _team(row.get("Home")),
            _team(row.get("Away")),
        )
        index.setdefault(key, []).append(row)
    return index


def _is_postponed(row: dict, index: dict) -> bool:
    key = (
        _text(row.get("LeagueId")),
        _team(row.get("Home")),
        _team(row.get("Away")),
    )
    candidates = index.get(key, [])
    if not candidates:
        return False

    row_round = _text(row.get("Round"))
    for candidate in candidates:
        postponed_round = _text(candidate.get("Round"))
        if row_round and postponed_round and row_round != postponed_round:
            continue
        return True
    return False


def _default_status(row: dict, postponed: dict) -> str:
    existing = _text(row.get("MatchStatus")).upper()
    if existing in {"POSTPONED", "CANCELLED"}:
        return existing

    if _text(row.get("HG")) != "" and _text(row.get("AG")) != "":
        return "FINAL"

    if _is_postponed(row, postponed):
        return "POSTPONED"

    return "SCHEDULED"


def _load_overrides() -> list[dict]:
    if not OVERRIDES_FILE.exists():
        return []
    rows, _ = _read_csv(OVERRIDES_FILE)
    return rows


def _override_matches(row: dict, override: dict, engine: str) -> bool:
    if _text(override.get("Engine")) and _text(override.get("Engine")) != engine:
        return False
    for field in ("LeagueId", "PredictionDate", "MatchDate"):
        wanted = _text(override.get(field))
        if wanted and _text(row.get(field)) != wanted:
            return False
    if _text(override.get("Home")) and _team(row.get("Home")) != _team(override.get("Home")):
        return False
    if _text(override.get("Away")) and _team(row.get("Away")) != _team(override.get("Away")):
        return False
    return True


def _backup(path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = BACKUP_DIR / timestamp / path.relative_to(HISTORY_ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Bonifica MatchStatus in tutti gli storici ranking.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    history_files = sorted(HISTORY_ROOT.glob("*/storico_ranking_*.csv"))
    postponed = _postponed_index()
    overrides = _load_overrides()
    errors = []
    changes = []
    file_data = {}

    for path in history_files:
        engine = path.parent.name
        rows, fields = _read_csv(path)
        if "MatchStatus" not in fields:
            insert_at = fields.index("Band") + 1 if "Band" in fields else len(fields)
            fields.insert(insert_at, "MatchStatus")

        for row_number, row in enumerate(rows, start=2):
            new_status = _default_status(row, postponed)
            old_status = _text(row.get("MatchStatus")).upper()
            if old_status != new_status:
                changes.append({
                    "Engine": engine,
                    "File": str(path),
                    "Row": row_number,
                    "LeagueId": row.get("LeagueId", ""),
                    "PredictionDate": row.get("PredictionDate", ""),
                    "MatchDate": row.get("MatchDate", ""),
                    "Home": row.get("Home", ""),
                    "Away": row.get("Away", ""),
                    "OldStatus": old_status,
                    "NewStatus": new_status,
                    "Reason": "AUTO",
                })
                row["MatchStatus"] = new_status

        file_data[path] = (rows, fields)

    for override_number, override in enumerate(overrides, start=2):
        status = _text(override.get("MatchStatus")).upper()
        if status not in VALID_STATUSES:
            errors.append({"OverrideRow": override_number, "Error": "INVALID_STATUS", "Details": status})
            continue

        matches = []
        for path, (rows, _fields) in file_data.items():
            engine = path.parent.name
            for row_index, row in enumerate(rows):
                if _override_matches(row, override, engine):
                    matches.append((path, engine, row_index, row))

        if len(matches) == 0:
            errors.append({
                "OverrideRow": override_number,
                "Error": "OVERRIDE_NOT_FOUND",
                "Details": "0",
            })
            continue

        # Un override con PredictionDate esplicita identifica una prediction
        # storica precisa. Se la stessa prediction è duplicata nello storico,
        # lo stato viene applicato a tutte le copie identiche invece di
        # interrompere la migrazione.
        if len(matches) > 1 and not _text(override.get("PredictionDate")):
            errors.append({
                "OverrideRow": override_number,
                "Error": "OVERRIDE_NOT_UNIQUE_WITHOUT_PREDICTION_DATE",
                "Details": str(len(matches)),
            })
            continue

        for path, engine, row_index, row in matches:
            old_status = _text(row.get("MatchStatus")).upper()

            if old_status == status:
                continue

            row["MatchStatus"] = status

            changes.append({
                "Engine": engine,
                "File": str(path),
                "Row": row_index + 2,
                "LeagueId": row.get("LeagueId", ""),
                "PredictionDate": row.get("PredictionDate", ""),
                "MatchDate": row.get("MatchDate", ""),
                "Home": row.get("Home", ""),
                "Away": row.get("Away", ""),
                "OldStatus": old_status,
                "NewStatus": status,
                "Reason": (
                    "OVERRIDE_MULTIPLE_IDENTICAL"
                    if len(matches) > 1
                    else "OVERRIDE"
                ),
            })

    summary = [{
        "Mode": "APPLY" if args.apply else "DRY_RUN",
        "HistoryFiles": len(history_files),
        "Changes": len(changes),
        "Overrides": len(overrides),
        "Errors": len(errors),
        "Result": "SUCCESS" if not errors else "FAILED",
    }]

    _write_csv(DEBUG_DIR / "match_status_summary.csv", summary,
               ["Mode", "HistoryFiles", "Changes", "Overrides", "Errors", "Result"])
    _write_csv(DEBUG_DIR / "match_status_changes.csv", changes,
               ["Engine", "File", "Row", "LeagueId", "PredictionDate", "MatchDate", "Home", "Away", "OldStatus", "NewStatus", "Reason"])
    _write_csv(DEBUG_DIR / "match_status_errors.csv", errors,
               ["OverrideRow", "Error", "Details"])

    print(f"Modalità: {'APPLY' if args.apply else 'DRY RUN'}")
    print(f"Storici trovati: {len(history_files)}")
    print(f"Modifiche: {len(changes)}")
    print(f"Override: {len(overrides)}")
    print(f"Errori: {len(errors)}")
    print(f"Esito: {'SUCCESS' if not errors else 'FAILED'}")
    print(f"Report: {DEBUG_DIR.resolve()}")

    if errors:
        print("Nessun file modificato.")
        return 1

    if not args.apply:
        print("Dry run completato. Per applicare aggiungere --apply.")
        return 0

    for path, (rows, fields) in file_data.items():
        _backup(path)
        _write_csv(path, rows, fields)

    print("Migrazione MatchStatus applicata a tutti gli storici.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
