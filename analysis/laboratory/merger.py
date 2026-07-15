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


def _candidate_date_score(
    history_row: dict,
    ranking_row: dict,
) -> tuple[int, int, str] | None:
    history_match_date = _parse_date(
        history_row.get("MatchDate")
    )
    history_prediction_date = _parse_date(
        history_row.get("PredictionDate")
    )

    ranking_match_date = _parse_date(
        ranking_row.get("MatchDate")
    )
    ranking_prediction_date = _parse_date(
        ranking_row.get("PredictionDate")
    )

    comparisons = []

    if history_match_date is not None:
        if ranking_match_date is not None:
            comparisons.append((
                0,
                abs(
                    (
                        history_match_date
                        - ranking_match_date
                    ).days
                ),
                "MATCH_DATE_TO_MATCH_DATE",
            ))

        elif ranking_prediction_date is not None:
            comparisons.append((
                2,
                abs(
                    (
                        history_match_date
                        - ranking_prediction_date
                    ).days
                ),
                "MATCH_DATE_TO_PREDICTION_DATE",
            ))

    elif history_prediction_date is not None:
        if ranking_prediction_date is not None:
            comparisons.append((
                0,
                abs(
                    (
                        history_prediction_date
                        - ranking_prediction_date
                    ).days
                ),
                "PREDICTION_DATE_TO_PREDICTION_DATE",
            ))

        elif ranking_match_date is not None:
            comparisons.append((
                2,
                abs(
                    (
                        history_prediction_date
                        - ranking_match_date
                    ).days
                ),
                "PREDICTION_DATE_TO_MATCH_DATE",
            ))

    valid = [
        comparison
        for comparison in comparisons
        if comparison[1] <= MAX_DATE_DIFFERENCE_DAYS
    ]

    if not valid:
        return None

    valid.sort(
        key=lambda item: (
            item[0],
            item[1],
        )
    )

    return valid[0]

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

    scored_candidates = []

    for ranking in candidates:
        score = _candidate_date_score(
            history_row,
            ranking,
        )

        if score is None:
            continue

        priority, distance, mode = score

        scored_candidates.append((
            priority,
            distance,
            ranking,
            mode,
        ))

    if scored_candidates:
        scored_candidates.sort(
            key=lambda item: (
                item[0],
                item[1],
            )
        )

        best_priority = scored_candidates[0][0]
        best_distance = scored_candidates[0][1]

        best_candidates = [
            item
            for item in scored_candidates
            if (
                item[0] == best_priority
                and item[1] == best_distance
            )
        ]

        if len(best_candidates) > 1:
            return (
                None,
                "",
                None,
                "AMBIGUOUS_SAME_DATE_PRIORITY",
                len(candidates),
            )

        (
            _priority,
            distance,
            ranking,
            mode,
        ) = best_candidates[0]

        return (
            ranking,
            mode,
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
