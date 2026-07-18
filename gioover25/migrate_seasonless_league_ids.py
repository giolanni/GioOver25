"""
===============================================================================
GioOver2.5 - migrate_seasonless_league_ids.py
===============================================================================

Rende i LeagueId indipendenti dalla stagione e bonifica i CSV pregressi.

Esempio:
    Norway_Eliteserien_2026 -> Norway_Eliteserien

La migrazione:
- rimuove la colonna Season dai CSV;
- aggiorna LeagueId, *SourceLeagueId e CompetitionGroup;
- rinomina i file il cui nome coincide con un vecchio LeagueId;
- ignora .git, cartelle backup e file .bak;
- crea backup .bak prima delle modifiche;
- blocca APPLY in presenza di collisioni.

Uso:
    python -m gioover25.migrate_seasonless_league_ids --dry-run
    python -m gioover25.migrate_seasonless_league_ids --apply
===============================================================================
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

REGISTRY_FILE = Path("data/league_registry.csv")
YEAR_SUFFIX = re.compile(r"_(?:19|20)\d{2}$")
EXCLUDED_DIR_NAMES = {".git", "backup", "backups", "archive", "__pycache__"}


@dataclass
class MigrationReport:
    csv_scanned: int = 0
    csv_changed: int = 0
    rows_changed: int = 0
    season_columns_removed: int = 0
    files_renamed: int = 0
    skipped: list[str] = field(default_factory=list)


def seasonless(value: str) -> str:
    """Rimuove un solo suffisso annuale terminale, se presente."""
    return YEAR_SUFFIX.sub("", str(value or "").strip())


def _is_excluded(path: Path) -> bool:
    return any(part.lower() in EXCLUDED_DIR_NAMES for part in path.parts) or path.name.endswith(".bak")


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        if not reader.fieldnames:
            raise ValueError("header assente")
        return list(reader.fieldnames), list(reader)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def _backup(path: Path) -> Path:
    backup = path.with_suffix(path.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(path, backup)
    return backup


def load_registry_mapping() -> tuple[dict[str, str], list[dict[str, str]], list[str]]:
    if not REGISTRY_FILE.exists():
        raise FileNotFoundError(f"Registry non trovato: {REGISTRY_FILE}")

    fieldnames, rows = _read_csv(REGISTRY_FILE)
    if "LeagueId" not in fieldnames:
        raise ValueError("league_registry.csv privo della colonna LeagueId")

    mapping: dict[str, str] = {}
    collisions: dict[str, list[str]] = {}

    for row in rows:
        old = str(row.get("LeagueId", "")).strip()
        if not old:
            continue
        new = seasonless(old)
        mapping[old] = new
        collisions.setdefault(new, []).append(old)

    errors = []
    for new, old_values in collisions.items():
        unique = sorted(set(old_values))
        if len(unique) > 1:
            errors.append(f"Collisione LeagueId: {unique} -> {new}")

    return mapping, rows, errors


def _mapped_value(field_name: str, value: str, mapping: dict[str, str]) -> str:
    text = str(value or "").strip()
    normalized_field = field_name.casefold()

    if normalized_field == "competitiongroup":
        return seasonless(text)

    if normalized_field == "leagueid" or normalized_field.endswith("sourceleagueid"):
        return mapping.get(text, seasonless(text))

    return value


def migrate_csv(path: Path, mapping: dict[str, str], apply: bool, report: MigrationReport) -> None:
    report.csv_scanned += 1

    try:
        fieldnames, rows = _read_csv(path)
    except (UnicodeDecodeError, csv.Error, ValueError) as exc:
        report.skipped.append(f"{path}: {exc}")
        return

    new_fieldnames = [name for name in fieldnames if name != "Season"]
    changed = new_fieldnames != fieldnames
    if "Season" in fieldnames:
        report.season_columns_removed += 1

    changed_rows = 0
    new_rows: list[dict[str, str]] = []

    for row in rows:
        new_row: dict[str, str] = {}
        row_changed = False

        for field_name in new_fieldnames:
            old_value = row.get(field_name, "")
            new_value = _mapped_value(field_name, old_value, mapping)
            new_row[field_name] = new_value
            if new_value != old_value:
                row_changed = True

        if row_changed or "Season" in fieldnames:
            changed_rows += 1
            changed = True

        new_rows.append(new_row)

    if not changed:
        return

    report.csv_changed += 1
    report.rows_changed += changed_rows
    print(f"{'APPLY' if apply else 'CHANGE'} CSV {path}")

    if apply:
        _backup(path)
        _write_csv(path, new_fieldnames, new_rows)


def find_csv_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.csv")
        if path.is_file() and not _is_excluded(path)
    )


def build_rename_plan(root: Path, mapping: dict[str, str]) -> tuple[list[tuple[Path, Path]], list[str]]:
    plan: list[tuple[Path, Path]] = []
    errors: list[str] = []

    for path in root.rglob("*.csv"):
        if not path.is_file() or _is_excluded(path):
            continue

        old_stem = path.stem
        if old_stem not in mapping:
            continue

        target = path.with_name(mapping[old_stem] + path.suffix)
        if target == path:
            continue
        if target.exists():
            errors.append(f"Collisione file: {path} -> {target} (destinazione esistente)")
            continue
        plan.append((path, target))

    return sorted(plan), errors


def apply_renames(plan: list[tuple[Path, Path]], apply: bool, report: MigrationReport) -> None:
    for source, target in plan:
        print(f"{'RENAME' if apply else 'WOULD RENAME'} {source} -> {target}")
        if apply:
            _backup(source)
            source.rename(target)
        report.files_renamed += 1


def print_report(report: MigrationReport, dry_run: bool) -> None:
    print("\n=== REPORT MIGRAZIONE ===")
    print(f"CSV analizzati             : {report.csv_scanned}")
    print(f"CSV da modificare/modificati: {report.csv_changed}")
    print(f"Righe interessate          : {report.rows_changed}")
    print(f"Colonne Season rimosse     : {report.season_columns_removed}")
    print(f"File da rinominare/rinominati: {report.files_renamed}")
    print(f"File saltati               : {len(report.skipped)}")
    if report.skipped:
        for item in report.skipped:
            print(f"  SKIP {item}")
    print("\nDRY RUN completato." if dry_run else "\nAPPLY completato.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rende i LeagueId indipendenti dalla stagione e bonifica i CSV."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--root",
        default=".",
        help="Radice del progetto (default: directory corrente)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    global REGISTRY_FILE
    REGISTRY_FILE = root / "data/league_registry.csv"

    mapping, _, registry_errors = load_registry_mapping()
    rename_plan, rename_errors = build_rename_plan(root, mapping)
    errors = registry_errors + rename_errors

    if errors:
        print("Migrazione bloccata per evitare perdita di dati:")
        for error in errors:
            print(f"  ERROR {error}")
        raise SystemExit(2)

    report = MigrationReport()
    apply = args.apply

    for csv_path in find_csv_files(root):
        migrate_csv(csv_path, mapping, apply, report)

    apply_renames(rename_plan, apply, report)
    print_report(report, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
