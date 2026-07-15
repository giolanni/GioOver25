"""
===============================================================================
GioOver2.5 - analysis/laboratory/merger.py
===============================================================================

SCOPO
-----
Unire lo storico ranking v25 con i ranking originali e produrre il dataset
principale del laboratorio.

MATCHING
--------
1. stessa LeagueId;
2. stessa Home;
3. stessa Away;
4. confronto temporale:
   - usa MatchDate quando disponibile;
   - altrimenti usa PredictionDate;
   - tolleranza massima configurata a ±2 giorni;
5. se esistono più candidati, sceglie quello con distanza temporale minore.

PRIORITÀ DEI DATI
-----------------
La riga del ranking originale fornisce i driver ex ante.

La riga dello storico prevale per:

    PredictionDate
    MatchDate
    LeagueId
    Round
    Home
    Away
    Score
    Band
    Outcome
    HG
    AG
    Goals
    BTTS
    Reason
    AlgorithmVersion

FILE SCRITTI
-------------
Oltre a restituire le righe abbinate, produce:

    analysis/laboratory/data/06_unmatched_matches.csv

Il file contiene tutte le righe dello storico escluse dal laboratorio.

LIMITAZIONI
-----------
Il matching dipende dalla coerenza di LeagueId e nomi squadra. Non vengono
applicate normalizzazioni aggressive per evitare associazioni errate.
===============================================================================
"""

from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any
import csv


MAX_DATE_DIFFERENCE_DAYS = 2

UNMATCHED_FILE = Path(
    "analysis/laboratory/data/06_unmatched_matches.csv"
)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_team(value: Any) -> str:
    return " ".join(
        _text(value)
        .casefold()
        .split()
    )


def _parse_date(value: Any) -> date | None:
    raw = _text(value)

    if not raw:
        return None

    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _base_key(row: dict) -> tuple[str, str, str]:
    return (
        _text(row.get("LeagueId")),
        _normalize_team(row.get("Home")),
        _normalize_team(row.get("Away")),
    )


def _row_date(row: dict) -> tuple[date | None, str]:
    match_date = _parse_date(
        row.get("MatchDate")
    )

    if match_date is not None:
        return match_date, "MATCH_DATE"

    prediction_date = _parse_date(
        row.get("PredictionDate")
    )

    if prediction_date is not None:
        return prediction_date, "PREDICTION_DATE"

    return None, ""


def build_index(
    rankings: list[dict],
) -> dict[tuple[str, str, str], list[dict]]:
    index: dict[
        tuple[str, str, str],
        list[dict]
    ] = {}

    for ranking in rankings:
        key = _base_key(ranking)

        index.setdefault(
            key,
            [],
        ).append(ranking)

    return index


def _find_ranking(
    history_row: dict,
    ranking_index: dict[
        tuple[str, str, str],
        list[dict]
    ],
) -> tuple[
    dict | None,
    str,
    int | None,
    str,
    int,
]:
    """
    Restituisce:

        ranking trovato
        modalità matching
        differenza giorni
        motivo diagnostico
        numero candidati base
    """
    candidates = ranking_index.get(
        _base_key(history_row),
        [],
    )

    if not candidates:
        return (
            None,
            "",
            None,
            "NO_TEAM_LEAGUE_CANDIDATE",
            0,
        )

    history_date, history_date_type = (
        _row_date(history_row)
    )

    if history_date is None:
        if len(candidates) == 1:
            return (
                candidates[0],
                "TEAM_ONLY",
                None,
                "",
                1,
            )

        return (
            None,
            "",
            None,
            "HISTORY_DATE_MISSING_MULTIPLE_CANDIDATES",
            len(candidates),
        )

    dated_candidates = []

    for ranking in candidates:
        ranking_date, ranking_date_type = (
            _row_date(ranking)
        )

        if ranking_date is None:
            continue

        distance = abs(
            (
                history_date
                - ranking_date
            ).days
        )

        if distance > MAX_DATE_DIFFERENCE_DAYS:
            continue

        date_priority = (
            0
            if ranking_date_type == "MATCH_DATE"
            else 1
        )

        dated_candidates.append(
            (
                distance,
                date_priority,
                ranking,
                ranking_date_type,
            )
        )

    if dated_candidates:
        dated_candidates.sort(
            key=lambda item: (
                item[0],
                item[1],
            )
        )

        (
            distance,
            _priority,
            ranking,
            ranking_date_type,
        ) = dated_candidates[0]

        match_mode = (
            f"{history_date_type}"
            f"_TO_"
            f"{ranking_date_type}"
        )

        return (
            ranking,
            match_mode,
            distance,
            "",
            len(candidates),
        )

    if len(candidates) == 1:
        return (
            candidates[0],
            "TEAM_ONLY_OUTSIDE_DATE_WINDOW",
            None,
            "",
            1,
        )

    return (
        None,
        "",
        None,
        "NO_DATE_CANDIDATE_WITHIN_WINDOW",
        len(candidates),
    )


def _write_unmatched(
    rows: list[dict],
) -> None:
    fieldnames = [
        "LeagueId",
        "PredictionDate",
        "MatchDate",
        "Home",
        "Away",
        "Band",
        "Outcome",
        "HG",
        "AG",
        "Reason",
        "BaseCandidates",
        "HistorySource",
    ]

    UNMATCHED_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with UNMATCHED_FILE.open(
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


def merge_matches(
    history: list[dict],
    rankings: list[dict],
) -> list[dict]:
    ranking_index = build_index(
        rankings
    )

    merged = []
    unmatched_rows = []

    matched = 0
    match_date_matches = 0
    prediction_date_matches = 0
    team_only_matches = 0
    match_id = 1

    for history_row in history:
        (
            ranking,
            match_mode,
            date_distance,
            unmatched_reason,
            base_candidates,
        ) = _find_ranking(
            history_row,
            ranking_index,
        )

        if ranking is None:
            unmatched_rows.append({
                "LeagueId": history_row.get("LeagueId", ""),
                "PredictionDate": history_row.get(
                    "PredictionDate",
                    "",
                ),
                "MatchDate": history_row.get("MatchDate", ""),
                "Home": history_row.get("Home", ""),
                "Away": history_row.get("Away", ""),
                "Band": history_row.get("Band", ""),
                "Outcome": history_row.get("Outcome", ""),
                "HG": history_row.get("HG", ""),
                "AG": history_row.get("AG", ""),
                "Reason": unmatched_reason,
                "BaseCandidates": base_candidates,
                "HistorySource": history_row.get(
                    "SourceFile",
                    "",
                ),
            })
            continue

        row = deepcopy(ranking)

        for field in (
            "PredictionDate",
            "MatchDate",
            "LeagueId",
            "Round",
            "Home",
            "Away",
            "Score",
            "Band",
            "Outcome",
            "HG",
            "AG",
            "Goals",
            "BTTS",
            "Reason",
            "AlgorithmVersion",
        ):
            history_value = history_row.get(
                field,
                "",
            )

            if _text(history_value):
                row[field] = history_value

        row["HistorySource"] = (
            history_row.get(
                "SourceFile",
                "",
            )
        )

        row["RankingSource"] = (
            ranking.get(
                "SourceFile",
                "",
            )
        )

        row["MatchMode"] = match_mode

        row["DateDifferenceDays"] = (
            ""
            if date_distance is None
            else date_distance
        )

        row["MatchId"] = match_id

        merged.append(row)

        match_id += 1
        matched += 1

        if match_mode.startswith("MATCH_DATE"):
            match_date_matches += 1
        elif match_mode.startswith("PREDICTION_DATE"):
            prediction_date_matches += 1
        else:
            team_only_matches += 1

    _write_unmatched(
        unmatched_rows
    )

    print()
    print("===== LABORATORY MERGE =====")
    print(f"Storico caricato:          {len(history)}")
    print(f"Ranking caricati:          {len(rankings)}")
    print(f"Righe abbinate:            {matched}")
    print(f"Match tramite MatchDate:   {match_date_matches}")
    print(f"Match tramite Prediction:  {prediction_date_matches}")
    print(f"Match solo lega/squadre:   {team_only_matches}")
    print(f"Righe non abbinate:        {len(unmatched_rows)}")
    print(f"Diagnostica:               {UNMATCHED_FILE}")
    print()

    return merged
