"""
===============================================================================
GioOver2.5 - repair_ranking_outcomes.py
===============================================================================

SCOPO
-----
Bonifica gli storici ranking nei quali:

- HG e AG sono valorizzati;
- Over25 è vuoto;
- BTTS è vuoto.

Quando i gol sono disponibili, lo script calcola automaticamente:

- Over25:
    OK  se HG + AG >= 3
    KO  se HG + AG <= 2

- BTTS:
    SI  se HG > 0 e AG > 0
    NO  altrimenti

Lo script NON sovrascrive mai un valore già presente.

MODALITÀ
--------
Controllo senza modifiche:

    python -m gioover25.repair_ranking_outcomes --dry-run

Applicazione reale:

    python -m gioover25.repair_ranking_outcomes --apply

Ripristino dei backup:

    python -m gioover25.repair_ranking_outcomes --restore

PERCORSO PREDEFINITO
--------------------
    data/storico/ranking

Lo script cerca ricorsivamente:

    storico_ranking*.csv

BACKUP
------
Prima di modificare un file viene creato:

    nome_file.csv.bak

Il backup non viene sovrascritto se esiste già.

COMPORTAMENTO
-------------
Per ogni riga:

1. legge HG e AG;
2. verifica che entrambi siano numerici;
3. se Over25 è vuoto, lo calcola;
4. se BTTS è vuoto, lo calcola;
5. conserva tutte le altre colonne e tutti gli altri valori.

Lo script accetta anche file nei quali le colonne usano varianti comuni:

    HG / HomeGoals / home_goals
    AG / AwayGoals / away_goals
    Over25 / over25
    BTTS / btts

===============================================================================
"""

from __future__ import annotations

# argparse gestisce i parametri da riga di comando.
import argparse

# csv legge e riscrive i file separati da punto e virgola.
import csv

# shutil crea e ripristina i backup.
import shutil

# dataclass rende più chiaro il riepilogo delle modifiche per file.
from dataclasses import dataclass

# Path semplifica e rende sicura la gestione dei percorsi.
from pathlib import Path

# Optional descrive valori che possono essere assenti.
from typing import Optional


# =============================================================================
# CONFIGURAZIONE PREDEFINITA
# =============================================================================

# Cartella predefinita contenente gli storici ranking.
DEFAULT_ROOT = Path("data/storico/ranking")

# Pattern dei file da analizzare ricorsivamente.
DEFAULT_PATTERN = "storico_ranking*.csv"

# Valori considerati vuoti.
EMPTY_VALUES = {
    "",
    "nan",
    "none",
    "null",
    "n/a",
    "na",
    "-",
}

# Alias ammessi per le colonne necessarie.
COLUMN_ALIASES = {
    "home_goals": (
        "HG",
        "HomeGoals",
        "home_goals",
        "home_score",
    ),
    "away_goals": (
        "AG",
        "AwayGoals",
        "away_goals",
        "away_score",
    ),
    "over25": (
        "Over25",
        "over25",
        "OVER25",
    ),
    "btts": (
        "BTTS",
        "btts",
    ),
}


# =============================================================================
# STRUTTURA DEL RIEPILOGO
# =============================================================================

@dataclass
class FileReport:
    """
    Raccoglie le statistiche di bonifica di un singolo file.
    """

    path: Path

    # Numero totale di righe lette.
    rows_read: int = 0

    # Righe nelle quali HG e AG erano entrambi validi.
    rows_with_goals: int = 0

    # Celle Over25 valorizzate dallo script.
    over25_filled: int = 0

    # Celle BTTS valorizzate dallo script.
    btts_filled: int = 0

    # Righe effettivamente modificate.
    rows_changed: int = 0

    # Indica se il file è stato riscritto.
    file_changed: bool = False

    # Eventuale motivazione di esclusione.
    skipped_reason: str = ""


# =============================================================================
# FUNZIONI DI SUPPORTO
# =============================================================================

def normalize(value: object) -> str:
    """
    Converte qualsiasi valore in una stringa pulita.

    None diventa stringa vuota.
    """

    if value is None:
        return ""

    return str(value).strip()


def is_empty(value: object) -> bool:
    """
    Verifica se un valore deve essere considerato vuoto.
    """

    return normalize(value).casefold() in EMPTY_VALUES


def parse_goal(value: object) -> Optional[int]:
    """
    Converte HG o AG in numero intero.

    Accetta:
    - 1
    - "1"
    - "1.0"
    - "1,0"

    Restituisce None quando il valore non è utilizzabile.
    """

    raw = normalize(value).replace(",", ".")

    if not raw:
        return None

    try:
        numeric_value = float(raw)
    except ValueError:
        return None

    # I gol devono essere numeri interi non negativi.
    if numeric_value < 0 or not numeric_value.is_integer():
        return None

    return int(numeric_value)


def resolve_column(
    fieldnames: list[str],
    logical_name: str,
) -> Optional[str]:
    """
    Individua il nome reale della colonna nel CSV.

    Il confronto ignora maiuscole e minuscole.
    """

    lookup = {
        name.casefold(): name
        for name in fieldnames
        if name
    }

    for alias in COLUMN_ALIASES[logical_name]:

        real_name = lookup.get(
            alias.casefold()
        )

        if real_name:
            return real_name

    return None


def detect_delimiter(path: Path) -> str:
    """
    Individua il delimitatore del file.

    Il progetto usa normalmente ";", ma il rilevamento evita errori su file
    storici eventualmente separati da virgola o tabulazione.
    """

    sample = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )[:4096]

    try:
        return csv.Sniffer().sniff(
            sample,
            delimiters=";,\t",
        ).delimiter
    except csv.Error:
        return ";"


def calculate_over25(
    home_goals: int,
    away_goals: int,
) -> str:
    """
    Calcola l'esito Over 2.5 nel formato usato dagli storici ranking.

    OK = almeno 3 gol totali.
    KO = al massimo 2 gol totali.
    """

    total_goals = home_goals + away_goals

    return "OK" if total_goals >= 3 else "KO"


def calculate_btts(
    home_goals: int,
    away_goals: int,
) -> str:
    """
    Calcola il BTTS.

    SI = entrambe le squadre hanno segnato.
    NO = almeno una squadra non ha segnato.
    """

    return "SI" if home_goals > 0 and away_goals > 0 else "NO"


def find_csv_files(
    root: Path,
    pattern: str,
) -> list[Path]:
    """
    Cerca i file CSV da bonificare.

    Se root è già un file, analizza direttamente quel file.
    """

    if root.is_file():

        if root.suffix.lower() == ".csv":
            return [root]

        return []

    return sorted(
        path
        for path in root.rglob(pattern)
        if path.is_file()
    )


# =============================================================================
# BONIFICA DI UN SINGOLO FILE
# =============================================================================

def process_file(
    path: Path,
    apply: bool,
) -> FileReport:
    """
    Analizza ed eventualmente corregge un singolo storico ranking.

    In modalità dry-run:
    - calcola cosa cambierebbe;
    - non crea backup;
    - non riscrive il file.

    In modalità apply:
    - crea il backup;
    - riscrive il CSV solo se sono state trovate modifiche.
    """

    report = FileReport(
        path=path
    )

    delimiter = detect_delimiter(
        path
    )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:

        reader = csv.DictReader(
            handle,
            delimiter=delimiter,
        )

        fieldnames = reader.fieldnames or []

        if not fieldnames:
            report.skipped_reason = "header assente"
            return report

        # Risolve i nomi reali delle quattro colonne necessarie.
        home_goals_column = resolve_column(
            fieldnames,
            "home_goals",
        )

        away_goals_column = resolve_column(
            fieldnames,
            "away_goals",
        )

        over25_column = resolve_column(
            fieldnames,
            "over25",
        )

        btts_column = resolve_column(
            fieldnames,
            "btts",
        )

        missing_columns = []

        if not home_goals_column:
            missing_columns.append("HG")

        if not away_goals_column:
            missing_columns.append("AG")

        if not over25_column:
            missing_columns.append("Over25")

        if not btts_column:
            missing_columns.append("BTTS")

        if missing_columns:

            report.skipped_reason = (
                "colonne mancanti: "
                + ", ".join(missing_columns)
            )

            return report

        rows = list(reader)

    report.rows_read = len(rows)

    # Analizza ogni riga conservando tutti i campi originali.
    for row in rows:

        home_goals = parse_goal(
            row.get(home_goals_column)
        )

        away_goals = parse_goal(
            row.get(away_goals_column)
        )

        # Senza entrambi i risultati numerici non è possibile calcolare nulla.
        if home_goals is None or away_goals is None:
            continue

        report.rows_with_goals += 1

        row_changed = False

        # Compila Over25 soltanto quando è realmente vuoto.
        if is_empty(
            row.get(over25_column)
        ):

            row[over25_column] = calculate_over25(
                home_goals,
                away_goals,
            )

            report.over25_filled += 1
            row_changed = True

        # Compila BTTS soltanto quando è realmente vuoto.
        if is_empty(
            row.get(btts_column)
        ):

            row[btts_column] = calculate_btts(
                home_goals,
                away_goals,
            )

            report.btts_filled += 1
            row_changed = True

        if row_changed:
            report.rows_changed += 1

    report.file_changed = report.rows_changed > 0

    # In dry-run termina qui senza toccare il file.
    if not apply or not report.file_changed:
        return report

    # Il backup usa l'estensione:
    # storico_ranking_v25.csv.bak
    backup_path = path.with_suffix(
        path.suffix + ".bak"
    )

    # Non sovrascrive un backup già esistente.
    if not backup_path.exists():

        shutil.copy2(
            path,
            backup_path,
        )

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as handle:

        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter=delimiter,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)

    return report


# =============================================================================
# RIPRISTINO DEI BACKUP
# =============================================================================

def restore_backups(
    root: Path,
) -> int:
    """
    Ripristina tutti i file .csv.bak presenti sotto root.

    Il backup resta disponibile anche dopo il ripristino.
    """

    if root.is_file():

        candidate = root.with_suffix(
            root.suffix + ".bak"
        )

        backups = (
            [candidate]
            if candidate.exists()
            else []
        )

    else:

        backups = sorted(
            path
            for path in root.rglob("*.csv.bak")
            if path.is_file()
        )

    if not backups:

        print("Nessun backup trovato.")
        return 0

    restored = 0

    for backup_path in backups:

        # Rimuove solamente il suffisso finale ".bak".
        destination = Path(
            str(backup_path)[:-4]
        )

        shutil.copy2(
            backup_path,
            destination,
        )

        print(
            f"RESTORE {destination}"
        )

        restored += 1

    print()
    print(
        f"File ripristinati: {restored}"
    )

    return restored


# =============================================================================
# OUTPUT DEL REPORT
# =============================================================================

def print_file_report(
    report: FileReport,
    apply: bool,
) -> None:
    """
    Stampa una riga di riepilogo per ciascun file.
    """

    if report.skipped_reason:

        print(
            f"SKIP    {report.path} "
            f"({report.skipped_reason})"
        )

        return

    if not report.file_changed:

        print(
            f"OK      {report.path}"
        )

        return

    action = (
        "UPDATE"
        if apply
        else "WOULD UPDATE"
    )

    print(
        f"{action:<12} {report.path} | "
        f"righe={report.rows_changed} | "
        f"Over25={report.over25_filled} | "
        f"BTTS={report.btts_filled}"
    )


# =============================================================================
# ARGOMENTI DA RIGA DI COMANDO
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    """
    Costruisce il parser dei parametri.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Bonifica Over25 e BTTS negli storici ranking usando HG e AG."
        )
    )

    group = parser.add_mutually_exclusive_group(
        required=True
    )

    group.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra le modifiche senza riscrivere i file.",
    )

    group.add_argument(
        "--apply",
        action="store_true",
        help="Applica le modifiche creando i backup.",
    )

    group.add_argument(
        "--restore",
        action="store_true",
        help="Ripristina i file dai backup .bak.",
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help=(
            "Cartella o singolo file da analizzare. "
            "Default: data/storico/ranking"
        ),
    )

    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help=(
            "Pattern dei file da cercare ricorsivamente. "
            "Default: storico_ranking*.csv"
        ),
    )

    return parser


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    """
    Punto di ingresso dello script.
    """

    parser = build_parser()

    args = parser.parse_args()

    root = args.root

    if not root.exists():

        print(
            f"Percorso non trovato: {root}"
        )

        return 2

    if args.restore:

        restore_backups(
            root
        )

        return 0

    files = find_csv_files(
        root,
        args.pattern,
    )

    if not files:

        print(
            f"Nessun file trovato in {root} "
            f"con pattern {args.pattern}"
        )

        return 3

    reports = []

    for path in files:

        report = process_file(
            path=path,
            apply=args.apply,
        )

        reports.append(
            report
        )

        print_file_report(
            report,
            apply=args.apply,
        )

    files_changed = sum(
        report.file_changed
        for report in reports
    )

    files_skipped = sum(
        bool(report.skipped_reason)
        for report in reports
    )

    rows_changed = sum(
        report.rows_changed
        for report in reports
    )

    over25_filled = sum(
        report.over25_filled
        for report in reports
    )

    btts_filled = sum(
        report.btts_filled
        for report in reports
    )

    print()
    print("=== REPORT BONIFICA RANKING ===")
    print(
        f"File analizzati       : {len(reports)}"
    )
    print(
        f"File modificati       : {files_changed}"
    )
    print(
        f"File saltati          : {files_skipped}"
    )
    print(
        f"Righe modificate      : {rows_changed}"
    )
    print(
        f"Over25 valorizzati    : {over25_filled}"
    )
    print(
        f"BTTS valorizzati      : {btts_filled}"
    )

    if args.dry_run:

        print()
        print(
            "DRY RUN completato: nessun file è stato modificato."
        )

    else:

        print()
        print(
            "APPLY completato: i file modificati hanno un backup .bak."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
