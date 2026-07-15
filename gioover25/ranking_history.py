"""
===============================================================================
GioOver2.5 - ranking_history.py
===============================================================================

SCOPO
-----
Gestire lo storico dei ranking prodotti dagli engine GioOver2.5.

Il modulo svolge due operazioni principali:

1. append_predictions
   Salva nello storico le nuove prediction prodotte da un engine.

2. update_finished_matches
   Cerca i risultati reali nello storico risultati e aggiorna:
   - HG
   - AG
   - Goals
   - Over25
   - BTTS

FILE LETTI
----------
Storico ranking:

    data/storico/ranking/<engine_name>/storico_ranking_<engine_name>.csv

Storico risultati:

    data/storico/risultati/<LeagueId>.csv

FILE SCRITTI
-------------
Storico ranking:

    data/storico/ranking/<engine_name>/storico_ranking_<engine_name>.csv

LOGICA DI SALVATAGGIO
---------------------
Ogni nuova prediction viene salvata copiando integralmente la riga prodotta
dal ranking.

In questo modo vengono conservati automaticamente:

- driver dell'engine;
- statistiche ex ante;
- score;
- fascia;
- motivazioni;
- eventuali nuove colonne aggiunte in futuro.

I campi relativi al risultato reale vengono inizializzati vuoti e popolati
successivamente da update_finished_matches.

LOGICA DI MATCHING RISULTATI
----------------------------
Nuovi ranking:

    LeagueId + MatchDate + Home + Away

Vecchi ranking privi di MatchDate:

    LeagueId + Home + Away

con risultato compreso tra PredictionDate e:

    PredictionDate + legacy_max_days

LIMITAZIONI
-----------
La compatibilità tramite PredictionDate è temporanea e potrà essere eliminata
quando tutti i ranking storici saranno stati migrati a MatchDate.
===============================================================================
"""

import csv
from datetime import date, timedelta
from pathlib import Path

from .history import read_results_file


RESULTS_DIR = Path("data/storico/risultati")


BASE_FIELDNAMES = [
    "PredictionDate",
    "MatchDate",
    "LeagueId",
    "Round",
    "Home",
    "Away",
    "Score",
    "Band",
    "HG",
    "AG",
    "Goals",
    "Over25",
    "BTTS",
    "Reason",
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
    "AlgorithmVersion",
]


RESULT_FIELDS = [
    "HG",
    "AG",
    "Goals",
    "Over25",
    "BTTS",
]


def _history_file(engine_name: str) -> Path:
    """
    Restituisce il percorso dello storico ranking dell'engine indicato.
    """
    return (
        Path("data/storico/ranking")
        / engine_name
        / f"storico_ranking_{engine_name}.csv"
    )


def _read_history(engine_name: str) -> list[dict]:
    """
    Legge lo storico ranking dell'engine.

    Se il file non esiste restituisce una lista vuota.
    """
    path = _history_file(engine_name)

    if not path.exists():
        return []

    with open(
        path,
        newline="",
        encoding="utf-8-sig",
    ) as file_handle:
        return list(
            csv.DictReader(
                file_handle,
                delimiter=";",
            )
        )


def _collect_fieldnames(rows: list[dict]) -> list[str]:
    """
    Costruisce l'header dello storico.

    Le colonne standard vengono mantenute all'inizio.

    Tutte le ulteriori colonne presenti nelle righe vengono aggiunte
    automaticamente, preservando il loro ordine di prima apparizione.
    """
    fieldnames = list(BASE_FIELDNAMES)

    for row in rows:
        for field_name in row:
            if field_name not in fieldnames:
                fieldnames.append(field_name)

    return fieldnames


def _write_history(
    engine_name: str,
    rows: list[dict],
) -> None:
    """
    Scrive lo storico ranking conservando tutte le colonne disponibili.
    """
    path = _history_file(engine_name)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = _collect_fieldnames(rows)

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file_handle:
        writer = csv.DictWriter(
            file_handle,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


def _normalize_team_name(value: str) -> str:
    """
    Normalizza il nome di una squadra per il matching.
    """
    return " ".join(
        str(value or "")
        .strip()
        .lower()
        .split()
    )


def _key(
    row: dict,
) -> tuple[str, str, str, str, str]:
    """
    Costruisce la chiave univoca della prediction.

    Se MatchDate è presente usa:

        MATCH_DATE + LeagueId + MatchDate + Home + Away

    Altrimenti usa la modalità legacy:

        PREDICTION_DATE + LeagueId + PredictionDate + Home + Away
    """
    league_id = str(
        row.get("LeagueId", "")
    ).strip()

    match_date = str(
        row.get("MatchDate", "")
    ).strip()

    prediction_date = str(
        row.get("PredictionDate", "")
    ).strip()

    home = _normalize_team_name(
        row.get("Home", "")
    )

    away = _normalize_team_name(
        row.get("Away", "")
    )

    if match_date:
        return (
            "MATCH_DATE",
            league_id,
            match_date,
            home,
            away,
        )

    return (
        "PREDICTION_DATE",
        league_id,
        prediction_date,
        home,
        away,
    )


def append_predictions(
    rows: list[dict],
    engine_name: str,
    algorithm_version: str,
) -> None:
    """
    Aggiunge allo storico le nuove prediction.

    La riga viene copiata integralmente dal ranking in modo da conservare
    tutte le statistiche ex ante disponibili.

    I campi del risultato reale vengono sempre inizializzati vuoti.
    """
    history = _read_history(engine_name)
    existing_keys = {
        _key(row)
        for row in history
    }

    added = 0

    for row in rows:
        history_row = dict(row)

        history_row["AlgorithmVersion"] = (
            row.get("AlgorithmVersion")
            or algorithm_version
        )

        for result_field in RESULT_FIELDS:
            history_row[result_field] = ""

        for field_name in BASE_FIELDNAMES:
            history_row.setdefault(
                field_name,
                "",
            )

        key = _key(history_row)

        if key in existing_keys:
            continue

        history.append(history_row)
        existing_keys.add(key)
        added += 1

    _write_history(
        engine_name,
        history,
    )

    print(
        f"[{engine_name}] "
        f"Storico ranking aggiornato. "
        f"Nuove previsioni: {added}"
    )


def _parse_date(
    value: str,
) -> date | None:
    """
    Converte una data ISO YYYY-MM-DD in datetime.date.

    Se il valore è vuoto o non valido restituisce None.
    """
    raw = str(
        value or ""
    ).strip()

    if not raw:
        return None

    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def update_finished_matches(
    engine_name: str,
    legacy_max_days: int = 3,
) -> None:
    """
    Aggiorna lo storico ranking con i risultati reali.

    Per i ranking con MatchDate viene richiesto il match esatto.

    Per i ranking legacy privi di MatchDate viene accettato un risultato
    compreso tra PredictionDate e PredictionDate + legacy_max_days.
    """
    history = _read_history(engine_name)

    if not history:
        print(
            f"[{engine_name}] "
            f"Storico ranking vuoto."
        )
        return

    results_cache: dict[str, list] = {}

    updated = 0
    not_found = 0
    ambiguous = 0

    for row in history:
        home_goals_value = str(
            row.get("HG", "")
        ).strip()

        away_goals_value = str(
            row.get("AG", "")
        ).strip()

        if (
            home_goals_value != ""
            and away_goals_value != ""
        ):
            continue

        league_id = str(
            row.get("LeagueId", "")
        ).strip()

        if not league_id:
            not_found += 1
            continue

        results_file = (
            RESULTS_DIR
            / f"{league_id}.csv"
        )

        if not results_file.exists():
            not_found += 1
            continue

        if league_id not in results_cache:
            results_cache[league_id] = (
                read_results_file(
                    results_file
                )
            )

        home = _normalize_team_name(
            row.get("Home", "")
        )

        away = _normalize_team_name(
            row.get("Away", "")
        )

        match_date = _parse_date(
            row.get("MatchDate", "")
        )

        candidates = []

        for match in results_cache[league_id]:
            if (
                _normalize_team_name(
                    match.home
                )
                != home
            ):
                continue

            if (
                _normalize_team_name(
                    match.away
                )
                != away
            ):
                continue

            result_date = _parse_date(
                str(match.date)
            )

            if result_date is None:
                continue

            if match_date is not None:
                # Tolleranza per partite spostate di pochi giorni.
                first_valid_date = match_date - timedelta(days=2)
                last_valid_date = match_date + timedelta(days=2)

                if result_date < first_valid_date:
                    continue

                if result_date > last_valid_date:
                    continue

            else:
                prediction_date = _parse_date(
                    row.get(
                        "PredictionDate",
                        "",
                    )
                )

                if prediction_date is None:
                    continue

                last_valid_date = (
                    prediction_date
                    + timedelta(
                        days=legacy_max_days
                    )
                )

                if result_date < prediction_date:
                    continue

                if result_date > last_valid_date:
                    continue

            candidates.append(match)

        if len(candidates) == 0:
            not_found += 1
            continue

        if len(candidates) > 1:
            ambiguous += 1
            continue

        match = candidates[0]

        goals = (
            match.home_goals
            + match.away_goals
        )

        row["HG"] = str(
            match.home_goals
        )

        row["AG"] = str(
            match.away_goals
        )

        row["Goals"] = str(
            goals
        )

        row["Over25"] = (
            "OK"
            if goals >= 3
            else "KO"
        )

        row["BTTS"] = (
            "OK"
            if (
                match.home_goals > 0
                and match.away_goals > 0
            )
            else "KO"
        )

        updated += 1

    _write_history(
        engine_name,
        history,
    )

    print(
        f"[{engine_name}] "
        f"Risultati aggiornati: {updated}"
    )

    print(
        f"[{engine_name}] "
        f"Partite non trovate: {not_found}"
    )

    print(
        f"[{engine_name}] "
        f"Partite ambigue: {ambiguous}"
    )