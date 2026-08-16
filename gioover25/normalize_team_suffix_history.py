"""
Bonifica del pregresso GioOver2.5: suffisso squadra ``II`` -> ``2``.

La regola viene applicata esclusivamente alle colonne che rappresentano nomi
squadra e soltanto quando ``II`` (o ``Ⅱ``) è il token finale del nome.

Dry-run:
    python -m gioover25.normalize_team_suffix_history

Applicazione:
    python -m gioover25.normalize_team_suffix_history --apply

Il dry-run crea sempre:
    data/debug/team_suffix_ii_to_2_report.csv

In modalità --apply, prima di modificare ogni CSV viene creato un backup:
    <nomefile>.bak_ii_to_2
"""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path

from .team_names import canonicalize_team_display_name


ROOTS = (
    Path("data/storico"),
    Path("data/input_partite"),
    Path("data/input_risultati"),
    Path("data/output_ranking"),
)

TEAM_COLUMNS = {
    "Home",
    "Away",
    "Team",
    "Squadra",
}

REPORT_FILE = Path(
    "data/debug/team_suffix_ii_to_2_report.csv"
)


def _detect_delimiter(path: Path) -> str:
    sample = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )[:4096]

    try:
        return csv.Sniffer().sniff(
            sample,
            delimiters=";,\t,",
        ).delimiter
    except csv.Error:
        return ";"


def _process_file(
    path: Path,
    *,
    apply: bool,
) -> list[dict]:
    delimiter = _detect_delimiter(path)

    with path.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as handle:
        reader = csv.DictReader(
            handle,
            delimiter=delimiter,
        )

        fieldnames = list(
            reader.fieldnames or []
        )

        target_columns = [
            column
            for column in fieldnames
            if column in TEAM_COLUMNS
        ]

        if not target_columns:
            return []

        rows = list(reader)

    changes = []

    for row_number, row in enumerate(
        rows,
        start=2,
    ):
        for column in target_columns:
            old = str(
                row.get(column, "")
            )

            new = canonicalize_team_display_name(
                old
            )

            if new == old:
                continue

            changes.append(
                {
                    "File": str(path),
                    "Row": row_number,
                    "Column": column,
                    "Old": old,
                    "New": new,
                }
            )

            row[column] = new

    if changes and apply:
        backup = Path(
            str(path) + ".bak_ii_to_2"
        )

        if not backup.exists():
            shutil.copy2(
                path,
                backup,
            )

        with path.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
                delimiter=delimiter,
                extrasaction="ignore",
            )

            writer.writeheader()
            writer.writerows(rows)

    return changes


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Bonifica i nomi squadra con suffisso II nella forma canonica 2."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Applica realmente le modifiche. Senza flag esegue solo dry-run.",
    )

    args = parser.parse_args()

    all_changes = []
    files_scanned = 0
    files_changed = 0
    seen = set()

    for root in ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*.csv"):
            resolved = path.resolve()

            if resolved in seen:
                continue

            seen.add(resolved)
            files_scanned += 1

            changes = _process_file(
                path,
                apply=args.apply,
            )

            if changes:
                files_changed += 1
                all_changes.extend(changes)

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with REPORT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "File",
                "Row",
                "Column",
                "Old",
                "New",
            ],
            delimiter=";",
        )

        writer.writeheader()
        writer.writerows(all_changes)

    print(
        f"Modalità: {'APPLY' if args.apply else 'DRY-RUN'}"
    )
    print(
        f"CSV analizzati: {files_scanned}"
    )
    print(
        f"CSV con modifiche: {files_changed}"
    )
    print(
        f"Nomi normalizzati/da normalizzare: {len(all_changes)}"
    )
    print(
        f"Report: {REPORT_FILE}"
    )

    if not args.apply:
        print()
        print(
            "Nessun file è stato modificato. "
            "Controlla il report e poi rilancia con --apply."
        )


if __name__ == "__main__":
    main()
