"""
===============================================================================
GioOver2.5 - Ricerca risultati duplicati con date differenti
===============================================================================

SCOPO
-----
Questo script analizza tutti i file CSV presenti nella cartella:

    data/storico/risultati/

e cerca casi in cui, all'interno dello stesso file di lega, risultano presenti
due o più partite con:

    1. stessa squadra di casa;
    2. stessa squadra in trasferta;
    3. stesso risultato finale, cioè stessi valori HG e AG;
    4. date differenti.

L'obiettivo è individuare possibili duplicazioni anomale causate, ad esempio,
da:

- import ripetuti della stessa partita con una data diversa;
- partite rinviate registrate sia con la vecchia sia con la nuova data;
- errori nella gestione della data della partita;
- inserimenti manuali duplicati;
- associazioni errate tra una partita prevista e un risultato storico.

FILE LETTI
----------
Lo script legge tutti i file:

    data/storico/risultati/*.csv

Ogni file dovrebbe rappresentare lo storico cumulativo dei risultati di una
singola lega.

Le colonne utilizzate per il controllo sono:

    Date oppure MatchDate
    Home
    Away
    HG
    AG

Per compatibilità con file creati in momenti diversi, lo script accetta sia:

    Date

sia:

    MatchDate

Se sono presenti entrambe, viene usata prima MatchDate.

CRITERIO DI CONFRONTO
---------------------
Due righe vengono considerate appartenenti allo stesso gruppo sospetto quando
hanno:

    stessa Home normalizzata
    stessa Away normalizzata
    stesso HG
    stesso AG

La normalizzazione dei nomi squadra:

- elimina spazi iniziali e finali;
- converte il testo in minuscolo;
- sostituisce sequenze multiple di spazi con un singolo spazio.

Il confronto non modifica i nomi originali presenti nei file.

Un gruppo viene segnalato soltanto se contiene almeno due date distinte.

Esempio segnalato:

    2026-07-05;Team A;Team B;2;1
    2026-07-12;Team A;Team B;2;1

Esempio non segnalato:

    2026-07-05;Team A;Team B;2;1
    2026-07-05;Team A;Team B;2;1

Il secondo caso è un duplicato sulla stessa data, ma non rientra nello scopo
specifico di questo script.

OUTPUT
------
Lo script produce:

1. un riepilogo a video;
2. un file CSV dettagliato:

    data/debug/duplicati_risultati_date_diverse.csv

Il report contiene una riga per ogni record coinvolto in un gruppo sospetto.

Le colonne del report sono:

    LeagueId
    SourceFile
    GroupId
    Home
    Away
    HG
    AG
    Date
    Round
    Season
    Notes
    GroupDates
    GroupOccurrences

SIGNIFICATO DI GroupId
----------------------
GroupId è un identificativo progressivo assegnato a ciascun gruppo sospetto.

Tutte le righe con lo stesso GroupId rappresentano:

    stessa squadra di casa
    stessa squadra trasferta
    stesso risultato
    date differenti

MODALITÀ D'USO
--------------
Eseguire dalla cartella principale del progetto:

    python -m gioover25.find_duplicate_results_different_dates

Lo script è in sola lettura rispetto agli storici risultati.

Non modifica, elimina o corregge alcun file in:

    data/storico/risultati/

L'unico file scritto è il report nella cartella data/debug/.

LIMITAZIONI
-----------
Lo script segnala casi sospetti, ma non stabilisce automaticamente se siano
errori reali.

Due squadre possono infatti affrontarsi più volte nella stessa stagione e
ottenere casualmente lo stesso risultato.

La verifica finale deve considerare almeno:

- stagione;
- round;
- formato del campionato;
- eventuali playoff;
- partite rinviate o ripetute;
- presenza di andata e ritorno;
- correttezza delle date.

===============================================================================
"""

import csv
from collections import defaultdict
from pathlib import Path


RESULTS_DIR = Path("data/storico/risultati")
REPORT_DIR = Path("data/debug")
REPORT_FILE = REPORT_DIR / "duplicati_risultati_date_diverse.csv"


REPORT_FIELDNAMES = [
    "LeagueId",
    "SourceFile",
    "GroupId",
    "Home",
    "Away",
    "HG",
    "AG",
    "Date",
    "Round",
    "Season",
    "Notes",
    "GroupDates",
    "GroupOccurrences",
]


def normalize_text(value: str) -> str:
    """
    Normalizza un valore testuale per confronti non sensibili a maiuscole,
    minuscole e spazi multipli.
    """
    return " ".join(
        str(value or "")
        .strip()
        .lower()
        .split()
    )


def get_match_date(row: dict) -> str:
    """
    Restituisce la data della partita.

    Per compatibilità usa prima MatchDate e, se assente o vuota, Date.
    """
    match_date = str(row.get("MatchDate", "")).strip()

    if match_date:
        return match_date

    return str(row.get("Date", "")).strip()


def get_result_value(value: str) -> str:
    """
    Normalizza un valore di risultato.

    Il risultato viene mantenuto come testo per evitare conversioni inutili,
    ma gli spazi vengono eliminati.
    """
    return str(value or "").strip()


def read_csv_rows(path: Path) -> tuple[list[str], list[dict]]:
    """
    Legge un file CSV separato da punto e virgola.
    """
    with path.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        reader = csv.DictReader(
            file,
            delimiter=";",
        )

        return (
            list(reader.fieldnames or []),
            list(reader),
        )


def validate_required_columns(
    path: Path,
    fieldnames: list[str],
) -> list[str]:
    """
    Verifica la presenza delle colonne necessarie.

    La data può essere rappresentata da Date oppure MatchDate.
    """
    missing = []

    for field in ["Home", "Away", "HG", "AG"]:
        if field not in fieldnames:
            missing.append(field)

    if (
        "Date" not in fieldnames
        and "MatchDate" not in fieldnames
    ):
        missing.append("Date/MatchDate")

    return missing


def build_group_key(
    row: dict,
) -> tuple[str, str, str, str]:
    """
    Costruisce la chiave di raggruppamento:

        Home + Away + HG + AG
    """
    return (
        normalize_text(row.get("Home", "")),
        normalize_text(row.get("Away", "")),
        get_result_value(row.get("HG", "")),
        get_result_value(row.get("AG", "")),
    )


def find_suspicious_groups(
    rows: list[dict],
) -> list[tuple[tuple[str, str, str, str], list[dict]]]:
    """
    Raggruppa le righe per casa, trasferta e risultato.

    Restituisce solo i gruppi che hanno almeno due date distinte.
    """
    groups: dict[
        tuple[str, str, str, str],
        list[dict],
    ] = defaultdict(list)

    for row in rows:
        home = normalize_text(row.get("Home", ""))
        away = normalize_text(row.get("Away", ""))
        hg = get_result_value(row.get("HG", ""))
        ag = get_result_value(row.get("AG", ""))
        match_date = get_match_date(row)

        if not home or not away:
            continue

        if hg == "" or ag == "":
            continue

        if not match_date:
            continue

        key = build_group_key(row)
        groups[key].append(row)

    suspicious = []

    for key, group_rows in groups.items():
        distinct_dates = {
            get_match_date(row)
            for row in group_rows
            if get_match_date(row)
        }

        if len(distinct_dates) >= 2:
            suspicious.append(
                (
                    key,
                    group_rows,
                )
            )

    return suspicious


def build_report_rows() -> tuple[list[dict], dict[str, int]]:
    """
    Analizza tutti i file risultati e costruisce le righe del report.
    """
    report_rows = []

    counters = {
        "files_scanned": 0,
        "files_skipped": 0,
        "rows_scanned": 0,
        "suspicious_groups": 0,
        "suspicious_rows": 0,
    }

    group_id = 0

    result_files = sorted(
        RESULTS_DIR.glob("*.csv")
    )

    for result_file in result_files:
        counters["files_scanned"] += 1

        fieldnames, rows = read_csv_rows(
            result_file
        )

        missing = validate_required_columns(
            result_file,
            fieldnames,
        )

        if missing:
            counters["files_skipped"] += 1

            print(
                f"SALTATO: {result_file.name} "
                f"- colonne mancanti: {', '.join(missing)}"
            )

            continue

        counters["rows_scanned"] += len(rows)

        suspicious_groups = find_suspicious_groups(
            rows
        )

        if not suspicious_groups:
            continue

        league_id = result_file.stem

        for key, group_rows in suspicious_groups:
            group_id += 1
            counters["suspicious_groups"] += 1
            counters["suspicious_rows"] += len(
                group_rows
            )

            home_key, away_key, hg, ag = key

            distinct_dates = sorted(
                {
                    get_match_date(row)
                    for row in group_rows
                    if get_match_date(row)
                }
            )

            group_dates = " | ".join(
                distinct_dates
            )

            for row in sorted(
                group_rows,
                key=lambda item: get_match_date(item),
            ):
                report_rows.append(
                    {
                        "LeagueId": league_id,
                        "SourceFile": result_file.name,
                        "GroupId": group_id,
                        "Home": row.get(
                            "Home",
                            home_key,
                        ),
                        "Away": row.get(
                            "Away",
                            away_key,
                        ),
                        "HG": hg,
                        "AG": ag,
                        "Date": get_match_date(row),
                        "Round": row.get(
                            "Round",
                            "",
                        ),
                        "Season": row.get(
                            "Season",
                            "",
                        ),
                        "Notes": row.get(
                            "Notes",
                            "",
                        ),
                        "GroupDates": group_dates,
                        "GroupOccurrences": len(
                            group_rows
                        ),
                    }
                )

    return report_rows, counters


def write_report(rows: list[dict]) -> None:
    """
    Scrive il report CSV nella cartella data/debug.
    """
    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with REPORT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=REPORT_FIELDNAMES,
            delimiter=";",
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if not RESULTS_DIR.exists():
        raise FileNotFoundError(
            "Cartella storico risultati non trovata: "
            f"{RESULTS_DIR}"
        )

    report_rows, counters = build_report_rows()

    write_report(report_rows)

    print()
    print("Controllo completato.")
    print(
        f"File analizzati: "
        f"{counters['files_scanned']}"
    )
    print(
        f"File saltati: "
        f"{counters['files_skipped']}"
    )
    print(
        f"Righe analizzate: "
        f"{counters['rows_scanned']}"
    )
    print(
        f"Gruppi sospetti: "
        f"{counters['suspicious_groups']}"
    )
    print(
        f"Righe coinvolte: "
        f"{counters['suspicious_rows']}"
    )
    print(f"Report: {REPORT_FILE}")

    if not report_rows:
        print(
            "Nessun caso con stessa casa, stessa trasferta, "
            "stesso risultato e date differenti."
        )


if __name__ == "__main__":
    main()