"""Bonifica fisica dei nomi squadra usando il dizionario canonico.

Anteprima senza modifiche:
    python -m gioover25.normalize_team_names

Applicazione con backup:
    python -m gioover25.normalize_team_names --apply

Il report viene scritto in ``data/debug/team_name_normalization_report.csv``.
I backup vengono raccolti in ``data/backup/team_names/<timestamp>/``.

La bonifica e' volutamente retroattiva: oltre agli input correnti attraversa
storico risultati, classifiche calcolate, storico ranking/ranking-risultati e
output ranking. In questo modo la stessa tipologica viene applicata sia ai
dati futuri sia a tutto il pregresso gia' persistito.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path

from .standings import generate_current_standings_file
from .team_names import canonicalize_team_display_name


RESULTS_DIR = Path("data/storico/risultati")
STANDINGS_DIR = Path("data/storico/classifiche_calcolate")
RANKING_HISTORY_DIR = Path("data/storico/ranking")
# Compatibilita' con eventuali checkout/archivi che usano il nome storico
# "ranking-risultati". Se la directory non esiste viene semplicemente saltata.
RANKING_RESULTS_DIR = Path("data/storico/ranking-risultati")

ROOTS = (
    RESULTS_DIR,
    STANDINGS_DIR,
    RANKING_HISTORY_DIR,
    RANKING_RESULTS_DIR,
    Path("data/input_partite"),
    Path("data/input_risultati"),
    Path("data/output_ranking"),
)

REPORT_FILE = Path("data/debug/team_name_normalization_report.csv")
BACKUP_BASE_DIR = Path("data/backup/team_names")

TEAM_COLUMNS = {"Home", "Away", "Team", "Squadra"}


def _detect_delimiter(path: Path) -> str:
    sample = path.read_text(encoding="utf-8-sig", errors="replace")[:4096]
    try:
        return csv.Sniffer().sniff(sample, delimiters=";,\t").delimiter
    except csv.Error:
        return ";"


def _league_id(path: Path, row: dict) -> str:
    league_id = str(row.get("LeagueId", "")).strip()
    if league_id:
        return league_id

    if path.parent.name in {"risultati", "classifiche_calcolate"}:
        return path.stem

    return ""


def _backup_file(path: Path, backup_root: Path) -> Path:
    try:
        relative_path = path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        relative_path = Path(path.parent.name) / path.name

    destination = backup_root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    return destination


def _process_file(
    path: Path,
    *,
    apply: bool,
    backup_root: Path | None = None,
) -> list[dict]:
    delimiter = _detect_delimiter(path)

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        fieldnames = list(reader.fieldnames or [])
        target_columns = [name for name in fieldnames if name in TEAM_COLUMNS]

        if not target_columns:
            return []

        rows = list(reader)

    changes: list[dict] = []

    for row_number, row in enumerate(rows, start=2):
        league_id = _league_id(path, row)
        if not league_id:
            continue

        for column in target_columns:
            old = str(row.get(column, ""))
            new = canonicalize_team_display_name(old, league_id)

            if new == old:
                continue

            changes.append(
                {
                    "File": str(path),
                    "Row": row_number,
                    "LeagueId": league_id,
                    "Column": column,
                    "Old": old,
                    "New": new,
                }
            )
            row[column] = new

    if changes and apply:
        if backup_root is None:
            raise ValueError("backup_root obbligatorio in modalita apply")

        _backup_file(path, backup_root)
        with path.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
                delimiter=delimiter,
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(rows)

    return changes


def _regenerate_standings(
    league_ids: set[str],
    *,
    backup_root: Path,
) -> int:
    regenerated = 0

    for league_id in sorted(league_ids):
        results_file = RESULTS_DIR / f"{league_id}.csv"
        standings_file = STANDINGS_DIR / f"{league_id}.csv"

        if not results_file.exists():
            continue

        # La classifica viene comunque rigenerata dai risultati gia'
        # canonicalizzati, anche se era stata bonificata direttamente poco
        # prima: il risultato finale resta deterministico e idempotente.
        if standings_file.exists():
            _backup_file(standings_file, backup_root)

        generate_current_standings_file(results_file, standings_file)
        regenerated += 1

    return regenerated


def _write_report(changes: list[dict]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_FILE.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["File", "Row", "LeagueId", "Column", "Old", "New"],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(changes)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Bonifica retroattivamente i nomi squadra usando "
            "team_name_dictionary.csv."
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Applica le modifiche. Senza flag esegue soltanto il dry-run.",
    )
    args = parser.parse_args()

    backup_root = None
    if args.apply:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_root = BACKUP_BASE_DIR / timestamp

    all_changes: list[dict] = []
    changed_result_leagues: set[str] = set()
    files_scanned = 0
    files_changed = 0
    seen: set[Path] = set()

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
                backup_root=backup_root,
            )

            if not changes:
                continue

            files_changed += 1
            all_changes.extend(changes)

            if path.parent == RESULTS_DIR:
                changed_result_leagues.add(path.stem)

    standings_regenerated = 0
    if args.apply and backup_root is not None:
        standings_regenerated = _regenerate_standings(
            changed_result_leagues,
            backup_root=backup_root,
        )

    _write_report(all_changes)

    print(f"Modalita: {'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"CSV analizzati: {files_scanned}")
    print(f"CSV con modifiche: {files_changed}")
    print(f"Nomi normalizzati/da normalizzare: {len(all_changes)}")
    print(f"Classifiche rigenerate: {standings_regenerated}")
    print(f"Report: {REPORT_FILE}")

    if backup_root is not None:
        print(f"Backup: {backup_root}")
    else:
        print("Nessun file modificato: controlla il report e usa --apply.")


if __name__ == "__main__":
    main()
