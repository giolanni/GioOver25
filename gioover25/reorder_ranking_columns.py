"""
===============================================================================
GioOver2.5 - reorder_ranking_columns.py
===============================================================================

Riordina le colonne dei ranking senza modificare alcun contenuto.

Modalità:

    python -m gioover25.reorder_ranking_columns --dry-run
    python -m gioover25.reorder_ranking_columns --apply

Per ogni file viene creato automaticamente:

    storico_ranking_xxx.csv.bak

===============================================================================
"""

from pathlib import Path
import argparse
import csv
import shutil

ROOTS = [
    Path("data/storico/ranking"),
    Path("data/output_ranking"),
]

CANONICAL_COLUMNS = [

    # operative
    "MatchDate",
    "LeagueId",
    "Home",
    "Away",
    "Score",
    "Band",
    "Round",

    # stato
    "MatchStatus",

    # risultato
    "HG",
    "AG",
    "Goals",
    "Over25",
    "BTTS",

    # prediction
    "PredictionDate",

    # motivazione
    "Reason",

    # drivers
    "RankingGapScore",
    "HomeAttackScore",
    "AwayAttackScore",
    "HomeDefenseWeaknessScore",
    "AwayDefenseWeaknessScore",
    "HomeLast10OverScore",
    "AwayLast10OverScore",
    "HomeVenueOverScore",
    "AwayVenueOverScore",
    "BTTSProfileScore",

    # metadati
    "AlgorithmVersion",
]


def build_fieldnames(existing):

    ordered = [c for c in CANONICAL_COLUMNS if c in existing]

    for c in existing:
        if c not in ordered:
            ordered.append(c)

    return ordered

def find_csv_files():

    files = []

    for root in ROOTS:

        if not root.exists():
            continue

        files.extend(
            root.rglob("*.csv")
        )

    return sorted(files)

def process_file(path: Path, apply: bool):

    with path.open(
        newline="",
        encoding="utf-8-sig",
    ) as f:

        reader = csv.DictReader(
            f,
            delimiter=";",
        )

        rows = list(reader)

        current = reader.fieldnames or []

    new_order = build_fieldnames(current)

    if current == new_order:
        print(f"OK      {path}")
        return False

    print(f"REORDER {path}")

    if not apply:
        return True

    backup = path.with_suffix(path.suffix + ".bak")

    if not backup.exists():
        shutil.copy2(path, backup)

    with path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=new_order,
            delimiter=";",
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)

    return True

def restore_backups():

    backups = []

    for root in ROOTS:

        if not root.exists():
            continue

        backups.extend(
            root.rglob("*.csv.bak")
        )

    backups = sorted(backups)

    if not backups:
        print("Nessun backup trovato.")
        return

    restored = 0

    for backup in backups:

        destination = Path(
            str(backup)[:-4]
        )

        shutil.copy2(
            backup,
            destination,
        )

        print(f"RESTORE {destination}")

        restored += 1

    print()
    print(f"File ripristinati : {restored}")


def main():

    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    group.add_argument("--restore", action="store_true")

    args = parser.parse_args()

    if args.restore:
        restore_backups()
        return

    files = find_csv_files()

    if not files:
        print("Nessun ranking trovato.")
        return

    changed = 0

    for file in files:

        if process_file(
            file,
            apply=args.apply,
        ):
            changed += 1

    print()

    print(f"File analizzati : {len(files)}")
    print(f"File modificati : {changed}")

    if args.dry_run:
        print("\nDRY RUN completato.")
    else:
        print("\nAPPLY completato.")


if __name__ == "__main__":
    main()