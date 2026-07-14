"""
===============================================================================
GioOver2.5 - analysis/laboratory/merger.py
===============================================================================

Unisce lo storico ranking con i ranking originali.

MATCHING
--------
1. LeagueId + Home + Away.
2. Confronto temporale:
   - usa MatchDate quando disponibile;
   - altrimenti usa PredictionDate;
   - accetta una differenza massima di 2 giorni.
3. Se esistono più candidati, sceglie quello con la distanza temporale minore.

Lo storico prevale per:
- fascia;
- risultato reale;
- HG;
- AG;
- Goals;
- BTTS;
- date.

===============================================================================
"""

from copy import deepcopy
from datetime import date
from typing import Any


MAX_DATE_DIFFERENCE_DAYS = 2


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
) -> tuple[dict | None, str, int | None]:
    candidates = ranking_index.get(
        _base_key(history_row),
        [],
    )

    if not candidates:
        return None, "", None

    history_date, history_date_type = (
        _row_date(history_row)
    )

    dated_candidates = []

    for ranking in candidates:
        ranking_date, ranking_date_type = (
            _row_date(ranking)
        )

        if (
            history_date is None
            or ranking_date is None
        ):
            continue

        distance = abs(
            (
                history_date
                - ranking_date
            ).days
        )

        if distance > MAX_DATE_DIFFERENCE_DAYS:
            continue

        # Priorità:
        # 1. distanza minore;
        # 2. ranking con MatchDate;
        # 3. ordine originale.
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
        )

    # Compatibilità estrema:
    # se esiste un solo ranking con stessa lega e squadre,
    # lo usa anche quando le date non sono disponibili.
    if len(candidates) == 1:
        return (
            candidates[0],
            "TEAM_ONLY",
            None,
        )

    return None, "", None


def merge_matches(
    history: list[dict],
    rankings: list[dict],
) -> list[dict]:
    ranking_index = build_index(
        rankings
    )

    merged = []

    matched = 0
    unmatched = 0
    match_id = 1

    for history_row in history:
        (
            ranking,
            match_mode,
            date_distance,
        ) = _find_ranking(
            history_row,
            ranking_index,
        )

        if ranking is None:
            unmatched += 1
            continue

        row = deepcopy(ranking)

        # I dati dello storico devono prevalere.
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

    print(
        f"Laboratory matchati: {matched}"
    )

    print(
        f"Laboratory non matchati: {unmatched}"
    )

    return merged