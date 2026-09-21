"""Bonifica controllata dei duplicati risultati segnalati da append_results.

Uso:
    python -m analysis.clean_duplicate_results data/debug/duplicati_risultati_suspect.csv
    python -m analysis.clean_duplicate_results <file_suspect> --apply

Per sicurezza il default è dry-run. Con --apply viene creato un backup ZIP
prima di modificare qualsiasi storico.

La bonifica automatica riguarda SOLO il caso già verificato nel dataset:
ExistingDate=2026-07-01, NewDate=2026-06-26, differenza=5 giorni.
In questi casi la riga 01/07 è una copia spuria e viene rimossa se nello
storico esiste anche la corrispondente riga corretta del 26/06 con stessa
LeagueId/Home/Away/HG/AG.

Gli altri sospetti non vengono toccati: stesso risultato in date lontane può
essere un rematch reale.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

RESULTS_DIR = Path("data/storico/risultati")
BACKUP_DIR = Path("data/archive/duplicate_cleanup")

# Gruppo verificato: copie spurie create con data 01/07 anziché 26/06.
VERIFIED_BAD_DATE = "2026-07-01"
VERIFIED_GOOD_DATE = "2026-06-26"


def _text(value) -> str:
    return str(value or "").strip()


def _read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        return list(reader.fieldnames or []), list(reader)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def _fixture_key(row: dict) -> tuple[str, str, str, str]:
    return (
        _text(row.get("Home")).casefold(),
        _text(row.get("Away")).casefold(),
        _text(row.get("HG")),
        _text(row.get("AG")),
    )


def _verified_candidates(suspects: list[dict]) -> list[dict]:
    return [
        row for row in suspects
        if _text(row.get("ExistingDate")) == VERIFIED_BAD_DATE
        and _text(row.get("NewDate")) == VERIFIED_GOOD_DATE
        and _text(row.get("DaysDifference")) == "5"
    ]


def _history_path(league_id: str) -> Path:
    return RESULTS_DIR / f"{league_id}.csv"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("suspect_file", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, suspects = _read_csv(args.suspect_file)
    candidates = _verified_candidates(suspects)

    removals: dict[Path, list[dict]] = {}
    skipped: list[str] = []

    for suspect in candidates:
        league_id = _text(suspect.get("LeagueId"))
        path = _history_path(league_id)
        if not path.exists():
            skipped.append(f"{league_id}: storico non trovato")
            continue

        _, rows = _read_csv(path)
        key = _fixture_key(suspect)

        bad = [
            row for row in rows
            if _text(row.get("MatchDate")) == VERIFIED_BAD_DATE
            and _fixture_key(row) == key
        ]
        good = [
            row for row in rows
            if _text(row.get("MatchDate")) == VERIFIED_GOOD_DATE
            and _fixture_key(row) == key
        ]

        # Mai cancellare sulla sola base del report: richiediamo entrambe le
        # copie nello storico corrente.
        if len(bad) == 1 and len(good) == 1:
            removals.setdefault(path, []).append(bad[0])
        else:
            skipped.append(
                f"{league_id} | {suspect.get('Home')} - {suspect.get('Away')}: "
                f"01/07={len(bad)}, 26/06={len(good)}"
            )

    total = sum(len(rows) for rows in removals.values())
    print("BONIFICA DUPLICATI RISULTATI")
    print(f"Segnalazioni nel report: {len(suspects)}")
    print(f"Casi verificati 01/07 -> 26/06: {len(candidates)}")
    print(f"Righe eliminabili con doppia conferma nello storico: {total}")
    print(f"Storici coinvolti: {len(removals)}")
    print(f"Casi non modificati: {len(skipped)}")

    if not args.apply:
        print("\nDRY-RUN: nessun file modificato. Usa --apply per applicare.")
        for path, rows in sorted(removals.items(), key=lambda item: str(item[0])):
            for row in rows:
                print(
                    f"  REMOVE {path}: {row.get('MatchDate')} | "
                    f"{row.get('Home')} - {row.get('Away')} "
                    f"{row.get('HG')}-{row.get('AG')}"
                )
        return

    if not removals:
        print("Nessuna modifica necessaria.")
        return

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"duplicate_cleanup_{stamp}.zip"

    with ZipFile(backup, "w", ZIP_DEFLATED) as archive:
        for path in removals:
            archive.write(path, arcname=str(path))

    for path, bad_rows in removals.items():
        fieldnames, rows = _read_csv(path)
        bad_ids = {id(row) for row in bad_rows}
        # I dict sono stati letti in una chiamata precedente: confronto quindi
        # tramite data+fixture, non tramite identità oggetto.
        bad_keys = {
            (_text(row.get("MatchDate")), _fixture_key(row))
            for row in bad_rows
        }
        cleaned = [
            row for row in rows
            if (_text(row.get("MatchDate")), _fixture_key(row)) not in bad_keys
        ]
        _write_csv(path, fieldnames, cleaned)

    print(f"Backup: {backup}")
    print(f"Righe eliminate: {total}")
    print("Bonifica completata.")


if __name__ == "__main__":
    main()
