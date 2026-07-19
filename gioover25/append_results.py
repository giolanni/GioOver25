"""
===============================================================================
GioOver2.5 - Importazione e aggiornamento dei risultati
===============================================================================

SCOPO
-----
Questo script importa i risultati contenuti in un file CSV, aggiorna gli
storici cumulativi delle singole leghe, rigenera le classifiche correnti,
aggiorna MatchStatus e risultati negli storici ranking e ricostruisce la mappa statistica
Over 2.5 delle leghe.

Lo script gestisce inoltre:

1. partite rinviate o posticipate;
2. archiviazione del file di input elaborato;
3. controllo di possibili duplicati con:
   - stessa squadra di casa;
   - stessa squadra in trasferta;
   - stesso risultato HG/AG;
   - data differente.

FORMATO DEL FILE DI INPUT
-------------------------
Il file normalmente utilizzato è:

    data/input_risultati/risultati.csv

Header previsto:

    LeagueId;Round;MatchDate;Home;Away;HG;AG;Status;Notes

Esempio di partita conclusa:

    Finland_Ykkonen;15;2026-07-12;KPV;TPV;2;1;FINALE;

Esempio di partita rinviata:

    Australia_NPLACT;18;2026-07-12;Canberra Olympic;Tigers FC;;;RINVIATA;

STATUS SUPPORTATI
-----------------
    FINALE
    RINVIATA
    POSTICIPATA

Se Status è vuoto ma HG e AG sono presenti, la riga viene considerata FINALE.

GESTIONE DELLE PARTITE RINVIATE
-------------------------------
Le partite rinviate o posticipate non vengono inserite negli storici risultati
e quindi non entrano nelle classifiche.

Vengono registrate in:

    data/storico/partite_posticipate.csv

Quando successivamente arriva un risultato finale con:

    stessa LeagueId
    stessa Home
    stessa Away

la partita viene rimossa dal registro delle posticipate e viene importata con
la nuova MatchDate.

GESTIONE DEI POSSIBILI DUPLICATI
--------------------------------
Prima di aggiungere un nuovo risultato, lo script cerca nello storico della
lega partite con:

    stessa Home
    stessa Away
    stesso HG
    stesso AG
    data differente

Caso A - differenza inferiore a 5 giorni
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Se la differenza assoluta tra le date è compresa tra 1 e 4 giorni, il sistema
considera il nuovo record come una correzione della data.

La partita esistente viene aggiornata con:

    nuova MatchDate
    nuovo Round, se disponibile
    nuove Notes, se non vuote

La nuova riga non viene aggiunta come seconda partita.

Caso B - differenza uguale o superiore a 5 giorni
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Il sistema non decide automaticamente che si tratti di un errore, perché le
stesse squadre possono affrontarsi più volte e ottenere lo stesso risultato.

La nuova partita viene quindi importata normalmente e il caso viene registrato
nel file:

    data/debug/duplicati_risultati_suspect.csv

Il report serve per una verifica manuale successiva.

ARCHIVIAZIONE DEL FILE DI INPUT
-------------------------------
Dopo un'importazione conclusa senza errori, il file di input viene copiato in:

    data/input_risultati/storico/

con un nome del tipo:

    risultati_20260712_15304512.csv

Il file originale non viene spostato né cancellato.

FILE LETTI
----------
    data/input_risultati/risultati.csv
    data/storico/risultati/*.csv
    data/storico/partite_posticipate.csv
    data/storico/ranking/*/storico_ranking_*.csv

FILE SCRITTI
------------
    data/storico/risultati/<LeagueId>.csv
    data/storico/classifiche_calcolate/<LeagueId>.csv
    data/storico/partite_posticipate.csv
    data/debug/duplicati_risultati_suspect.csv
    data/input_risultati/storico/risultati_YYYYMMDD_XXXXXXXX.csv

MODALITÀ D'USO
--------------
Dalla cartella principale del progetto:

    python -m gioover25.append_results data/input_risultati/risultati.csv

LIMITAZIONI
-----------
Il controllo dei duplicati usa stessa lega, stesse squadre e stesso risultato.

Un caso con differenza di almeno 5 giorni viene soltanto segnalato: non viene
eliminato né corretto automaticamente.

===============================================================================
"""

import argparse
import csv
import shutil
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
import subprocess
import sys

from .history import MatchResult, read_results_file, write_results_file
from .registry import get_league_info
from .standings import generate_current_standings_file
from .ranking_history import (
    sync_postponed_statuses_all_engines,
    update_finished_matches,
)
from gioover25.league_over_map import rebuild_league_over_map
from gioover25.engines.factory import get_available_engines



INPUT_REQUIRED_COLUMNS = {
    "LeagueId",
    "Round",
    "MatchDate",
    "Home",
    "Away",
    "HG",
    "AG",
}

RESULTS_DIR = Path("data/storico/risultati")
STANDINGS_DIR = Path("data/storico/classifiche_calcolate")

INPUT_RESULTS_ARCHIVE_DIR = Path(
    "data/input_risultati/storico"
)

POSTPONED_FILE = Path(
    "data/storico/partite_posticipate.csv"
)

DEBUG_DIR = Path("data/debug")

SUSPECT_DUPLICATES_FILE = (
    DEBUG_DIR
    / "duplicati_risultati_suspect.csv"
)

POSTPONED_FIELDNAMES = [
    "LeagueId",
    "Round",
    "MatchDate",
    "Home",
    "Away",
    "Status",
    "Notes",
]

SUSPECT_DUPLICATES_FIELDNAMES = [
    "DetectedAt",
    "LeagueId",
    "ExistingDate",
    "NewDate",
    "DaysDifference",
    "Home",
    "Away",
    "HG",
    "AG",
    "ExistingRound",
    "NewRound",
    "ExistingNotes",
    "NewNotes",
    "SourceInputFile",
    "Status",
]

POSTPONED_STATUSES = {
    "RINVIATA",
    "POSTICIPATA",
}

CLOSE_DUPLICATE_MAX_DAYS = 4


def _optional_int(value: str) -> int | None:
    raw = str(value or "").strip()

    if raw == "":
        return None

    return int(raw)


def _normalize(value: str) -> str:
    return " ".join(
        str(value or "")
        .strip()
        .lower()
        .split()
    )


def _parse_match_date(value) -> date | None:
    raw = str(value or "").strip()

    if not raw:
        return None

    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _match_key(
    match: MatchResult,
) -> tuple[str, str, str]:
    return (
        str(match.date).strip(),
        _normalize(match.home),
        _normalize(match.away),
    )


def _postponed_key(
    league_id: str,
    home: str,
    away: str,
) -> tuple[str, str, str]:
    return (
        league_id.strip(),
        _normalize(home),
        _normalize(away),
    )


def _same_teams_and_result(
    first: MatchResult,
    second: MatchResult,
) -> bool:
    return (
        _normalize(first.home)
        == _normalize(second.home)
        and _normalize(first.away)
        == _normalize(second.away)
        and first.home_goals
        == second.home_goals
        and first.away_goals
        == second.away_goals
    )


def _find_same_result_matches(
    new_match: MatchResult,
    existing_matches: list[MatchResult],
) -> list[tuple[MatchResult, int]]:
    new_date = _parse_match_date(
        new_match.date
    )

    if new_date is None:
        return []

    candidates = []

    for existing in existing_matches:
        if not _same_teams_and_result(
            existing,
            new_match,
        ):
            continue

        existing_date = _parse_match_date(
            existing.date
        )

        if existing_date is None:
            continue

        days_difference = abs(
            (new_date - existing_date).days
        )

        if days_difference == 0:
            continue

        candidates.append(
            (
                existing,
                days_difference,
            )
        )

    candidates.sort(
        key=lambda item: item[1]
    )

    return candidates


def _build_suspect_row(
    *,
    league_id: str,
    existing_match: MatchResult,
    new_match: MatchResult,
    days_difference: int,
    input_file: str | Path,
) -> dict:
    return {
        "DetectedAt": datetime.now().isoformat(
            timespec="seconds"
        ),
        "LeagueId": league_id,
        "ExistingDate": str(
            existing_match.date
        ).strip(),
        "NewDate": str(
            new_match.date
        ).strip(),
        "DaysDifference": str(
            days_difference
        ),
        "Home": new_match.home,
        "Away": new_match.away,
        "HG": str(
            new_match.home_goals
        ),
        "AG": str(
            new_match.away_goals
        ),
        "ExistingRound": str(
            existing_match.round
        ),
        "NewRound": str(
            new_match.round
        ),
        "ExistingNotes": str(
            existing_match.notes or ""
        ),
        "NewNotes": str(
            new_match.notes or ""
        ),
        "SourceInputFile": str(
            input_file
        ),
        "Status": "DA_VERIFICARE",
    }


def _suspect_key(
    row: dict,
) -> tuple[str, str, str, str, str, str, str]:
    return (
        str(
            row.get("LeagueId", "")
        ).strip(),
        _normalize(
            row.get("Home", "")
        ),
        _normalize(
            row.get("Away", "")
        ),
        str(
            row.get("HG", "")
        ).strip(),
        str(
            row.get("AG", "")
        ).strip(),
        str(
            row.get("ExistingDate", "")
        ).strip(),
        str(
            row.get("NewDate", "")
        ).strip(),
    )


def _append_suspect_rows(
    rows: list[dict],
) -> int:
    if not rows:
        return 0

    DEBUG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    existing_rows = []

    if SUSPECT_DUPLICATES_FILE.exists():
        with SUSPECT_DUPLICATES_FILE.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as file:
            existing_rows = list(
                csv.DictReader(
                    file,
                    delimiter=";",
                )
            )

    existing_keys = {
        _suspect_key(row)
        for row in existing_rows
    }

    added = 0

    for row in rows:
        key = _suspect_key(row)

        if key in existing_keys:
            continue

        existing_rows.append(row)
        existing_keys.add(key)
        added += 1

    with SUSPECT_DUPLICATES_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=(
                SUSPECT_DUPLICATES_FIELDNAMES
            ),
            delimiter=";",
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(existing_rows)

    return added


def _resolve_round(
    row: dict,
    existing_matches: list[MatchResult],
) -> int:
    raw_round = str(
        row.get("Round", "")
    ).strip()

    if raw_round and raw_round != "?":
        return int(raw_round)

    home = _normalize(
        row.get("Home", "")
    )

    away = _normalize(
        row.get("Away", "")
    )

    home_last_round = max(
        [
            match.round
            for match in existing_matches
            if (
                _normalize(match.home) == home
                or _normalize(match.away) == home
            )
        ],
        default=0,
    )

    away_last_round = max(
        [
            match.round
            for match in existing_matches
            if (
                _normalize(match.home) == away
                or _normalize(match.away) == away
            )
        ],
        default=0,
    )

    return max(
        home_last_round,
        away_last_round,
    ) + 1


def _parse_round(value) -> int:
    raw = str(value or "").strip()

    if raw == "" or raw == "?":
        return 0

    if (
        raw.isdigit()
        and len(raw) == 8
        and raw.startswith("20")
    ):
        return 0

    return int(raw)


def _read_postponed() -> list[dict]:
    if not POSTPONED_FILE.exists():
        return []

    with POSTPONED_FILE.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        return list(
            csv.DictReader(
                file,
                delimiter=";",
            )
        )


def _write_postponed(
    rows: list[dict],
) -> None:
    POSTPONED_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with POSTPONED_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=POSTPONED_FIELDNAMES,
            delimiter=";",
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


def _register_postponed(
    postponed_rows: list[dict],
    row: dict,
) -> bool:
    key = _postponed_key(
        row["LeagueId"],
        row["Home"],
        row["Away"],
    )

    for existing in postponed_rows:
        existing_key = _postponed_key(
            existing.get(
                "LeagueId",
                "",
            ),
            existing.get(
                "Home",
                "",
            ),
            existing.get(
                "Away",
                "",
            ),
        )

        if existing_key != key:
            continue

        existing["Round"] = row.get(
            "Round",
            "",
        )
        existing["MatchDate"] = row.get(
            "MatchDate",
            "",
        )
        existing["Status"] = row.get(
            "Status",
            "RINVIATA",
        )
        existing["Notes"] = row.get(
            "Notes",
            "",
        )

        return False

    postponed_rows.append(
        {
            "LeagueId": row.get(
                "LeagueId",
                "",
            ),
            "Round": row.get(
                "Round",
                "",
            ),
            "MatchDate": row.get(
                "MatchDate",
                "",
            ),
            "Home": row.get(
                "Home",
                "",
            ),
            "Away": row.get(
                "Away",
                "",
            ),
            "Status": row.get(
                "Status",
                "RINVIATA",
            ),
            "Notes": row.get(
                "Notes",
                "",
            ),
        }
    )

    return True

def _remove_postponed_if_present(
    postponed_rows: list[dict],
    league_id: str,
    home: str,
    away: str,
) -> bool:
    target_key = _postponed_key(
        league_id,
        home,
        away,
    )

    for index, existing in enumerate(
        postponed_rows
    ):
        existing_key = _postponed_key(
            existing.get(
                "LeagueId",
                "",
            ),
            existing.get(
                "Home",
                "",
            ),
            existing.get(
                "Away",
                "",
            ),
        )

        if existing_key != target_key:
            continue

        postponed_rows.pop(index)
        return True

    return False


def archive_input_results(
    input_file: str | Path,
) -> Path:
    source = Path(input_file)

    if not source.exists():
        raise FileNotFoundError(
            "File risultati da archiviare "
            f"non trovato: {source}"
        )

    INPUT_RESULTS_ARCHIVE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    now = datetime.now()

    date_part = now.strftime(
        "%Y%m%d"
    )

    timestamp_part = now.strftime(
        "%H%M%S%f"
    )[:8]

    archive_file = (
        INPUT_RESULTS_ARCHIVE_DIR
        / (
            f"risultati_{date_part}_"
            f"{timestamp_part}.csv"
        )
    )

    counter = 1

    while archive_file.exists():
        archive_file = (
            INPUT_RESULTS_ARCHIVE_DIR
            / (
                f"risultati_{date_part}_"
                f"{timestamp_part}_{counter}.csv"
            )
        )

        counter += 1

    shutil.copy2(
        source,
        archive_file,
    )

    return archive_file


def read_input_results(
    path: str | Path,
) -> tuple[
    dict[str, list[MatchResult]],
    list[dict],
    int,
]:
    input_path = Path(path)

    if not input_path.exists():
        raise FileNotFoundError(
            "File input risultati non trovato: "
            f"{input_path}"
        )

    grouped: dict[
        str,
        list[MatchResult],
    ] = defaultdict(list)

    postponed_rows = _read_postponed()
    postponed_registered = 0

    with input_path.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        reader = csv.DictReader(
            file,
            delimiter=";",
        )

        missing = (
            INPUT_REQUIRED_COLUMNS
            - set(reader.fieldnames or [])
        )

        if missing:
            raise ValueError(
                "File input risultati non valido. "
                "Mancano le colonne: "
                + ", ".join(
                    sorted(missing)
                )
            )

        for row in reader:
            league_id = row[
                "LeagueId"
            ].strip()

            league_info = get_league_info(
                league_id
            )

            status = str(
                row.get(
                    "Status",
                    "",
                )
            ).strip().upper()

            hg = _optional_int(
                row.get(
                    "HG",
                    "",
                )
            )

            ag = _optional_int(
                row.get(
                    "AG",
                    "",
                )
            )

            if (
                status == ""
                and hg is not None
                and ag is not None
            ):
                status = "FINALE"

            if status in POSTPONED_STATUSES:
                row["Status"] = status

                inserted = _register_postponed(
                    postponed_rows,
                    row,
                )

                if inserted:
                    postponed_registered += 1

                continue

            if status != "FINALE":
                raise ValueError(
                    f"Status non valido per "
                    f"{league_id} | "
                    f"{row['Home']} - "
                    f"{row['Away']}: "
                    f"{status or '<vuoto>'}"
                )

            if hg is None or ag is None:
                raise ValueError(
                    f"Risultato mancante per "
                    f"{league_id} | "
                    f"{row['Home']} - "
                    f"{row['Away']}"
                )

            match_date = str(
                row.get(
                    "MatchDate",
                    "",
                )
            ).strip()

            if _parse_match_date(
                match_date
            ) is None:
                raise ValueError(
                    f"MatchDate non valida per "
                    f"{league_id} | "
                    f"{row['Home']} - "
                    f"{row['Away']}: "
                    f"{match_date or '<vuota>'}"
                )

            _remove_postponed_if_present(
                postponed_rows,
                league_id,
                row["Home"],
                row["Away"],
            )

            match = MatchResult(
                country=league_info.country,
                league=league_info.league,
                round=_parse_round(
                    row.get(
                        "Round"
                    )
                ),
                date=match_date,
                home=row[
                    "Home"
                ].strip(),
                away=row[
                    "Away"
                ].strip(),
                home_goals=hg,
                away_goals=ag,
                notes=row.get(
                    "Notes",
                    "",
                ).strip(),
            )

            grouped[
                league_id
            ].append(match)

    return (
        grouped,
        postponed_rows,
        postponed_registered,
    )


def append_results(
    input_file: str | Path,
) -> None:
    (
        grouped_matches,
        postponed_rows,
        postponed_registered,
    ) = read_input_results(
        input_file
    )

    total_added = 0
    total_duplicates = 0
    total_dates_updated = 0

    suspect_rows = []

    for league_id, new_matches in (
        grouped_matches.items()
    ):
        results_file = (
            RESULTS_DIR
            / f"{league_id}.csv"
        )

        standings_file = (
            STANDINGS_DIR
            / f"{league_id}.csv"
        )

        if results_file.exists():
            existing_matches = read_results_file(
                results_file
            )
        else:
            existing_matches = []

        existing_keys = {
            _match_key(match)
            for match in existing_matches
        }

        added = []
        duplicates = 0
        dates_updated = 0

        for match in new_matches:
            if match.round == 0:
                fake_row = {
                    "Round": "?",
                    "Home": match.home,
                    "Away": match.away,
                }

                match.round = _resolve_round(
                    fake_row,
                    existing_matches + added,
                )

            key = _match_key(match)

            if key in existing_keys:
                duplicates += 1
                continue

            same_result_matches = (
                _find_same_result_matches(
                    new_match=match,
                    existing_matches=(
                        existing_matches
                        + added
                    ),
                )
            )

            close_match = next(
                (
                    candidate
                    for candidate
                    in same_result_matches
                    if (
                        candidate[1]
                        <= CLOSE_DUPLICATE_MAX_DAYS
                    )
                ),
                None,
            )

            if close_match is not None:
                (
                    existing_match,
                    days_difference,
                ) = close_match

                old_date = str(
                    existing_match.date
                ).strip()

                old_key = _match_key(
                    existing_match
                )

                existing_match.date = (
                    match.date
                )

                if match.round > 0:
                    existing_match.round = (
                        match.round
                    )

                if str(
                    match.notes or ""
                ).strip():
                    existing_match.notes = (
                        match.notes
                    )

                new_key = _match_key(
                    existing_match
                )

                existing_keys.discard(
                    old_key
                )

                existing_keys.add(
                    new_key
                )

                dates_updated += 1
                total_dates_updated += 1

                print(
                    "  Data corretta: "
                    f"{match.home} - "
                    f"{match.away} | "
                    f"{old_date} -> "
                    f"{match.date} "
                    f"({days_difference} giorni)"
                )

                continue

            distant_matches = [
                candidate
                for candidate
                in same_result_matches
                if (
                    candidate[1]
                    > CLOSE_DUPLICATE_MAX_DAYS
                )
            ]

            for (
                existing_match,
                days_difference,
            ) in distant_matches:
                suspect_rows.append(
                    _build_suspect_row(
                        league_id=league_id,
                        existing_match=(
                            existing_match
                        ),
                        new_match=match,
                        days_difference=(
                            days_difference
                        ),
                        input_file=input_file,
                    )
                )

            added.append(match)
            existing_keys.add(key)

        all_matches = (
            existing_matches
            + added
        )

        all_matches.sort(
            key=lambda match: (
                match.round,
                match.date,
                match.home,
                match.away,
            )
        )

        write_results_file(
            all_matches,
            results_file,
        )

        generate_current_standings_file(
            results_file,
            standings_file,
        )

        total_added += len(added)
        total_duplicates += duplicates

        print(league_id)
        print(
            f"  Aggiunte: {len(added)}"
        )
        print(
            "  Duplicate esatte ignorate: "
            f"{duplicates}"
        )
        print(
            "  Date corrette: "
            f"{dates_updated}"
        )
        print(
            f"  Storico: {results_file}"
        )
        print(
            f"  Classifica: {standings_file}"
        )
        print()

    _write_postponed(
        postponed_rows
    )

    new_suspects = _append_suspect_rows(
        suspect_rows
    )

    print("Import completato.")
    print(
        "Totale partite aggiunte: "
        f"{total_added}"
    )
    print(
        "Totale duplicate esatte ignorate: "
        f"{total_duplicates}"
    )
    print(
        "Totale date corrette: "
        f"{total_dates_updated}"
    )
    print(
        "Nuove partite rinviate registrate: "
        f"{postponed_registered}"
    )
    print(
        "Nuovi possibili duplicati sospetti: "
        f"{new_suspects}"
    )

    if suspect_rows:
        print(
            "Report possibili duplicati: "
            f"{SUSPECT_DUPLICATES_FILE}"
        )

    # Prima assegna i risultati finali alla prediction più recente
    # e compatibile; poi sincronizza le eventuali rinviate ancora aperte.
    for engine_name in get_available_engines():
        update_finished_matches(
            engine_name
        )

    sync_postponed_statuses_all_engines(
        get_available_engines()
    )

    rebuild_league_over_map()

    archive_file = archive_input_results(
        input_file
    )

    print(
        "File input risultati archiviato: "
        f"{archive_file}"
    )

def _run_post_update_tasks() -> None:
    commands = [
        (
            "aggiornamento laboratory",
            [sys.executable, "-m", "analysis.laboratory.run_all"],
        ),
        (
            "aggiornamento metrics",
            [sys.executable, "-m", "analysis.metrics.analyze_metrics"],
        ),
    ]

    for description, command in commands:
        print(f"\nAvvio {description}...")

        result = subprocess.run(
            command,
            check=False,
        )

        if result.returncode != 0:
            print(
                f"[WARN] {description} non completato "
                f"(codice {result.returncode})."
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Importa nuovi risultati, gestisce "
            "rinvii e possibili duplicati, "
            "aggiorna classifiche e storici "
            "del progetto GioOver2.5."
        )
    )

    parser.add_argument(
        "input_file",
        help=(
            "CSV nuovi risultati, normalmente "
            "data/input_risultati/"
            "risultati.csv"
        ),
    )

    args = parser.parse_args()

    append_results(
        args.input_file
    )
    _run_post_update_tasks() #aggiorna metriche e laboratory

if __name__ == "__main__":
    main()