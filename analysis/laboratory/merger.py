"""
===============================================================================
GioOver2.5 - analysis/laboratory/merger.py
===============================================================================

SCOPO
-----
Unire lo storico ranking v25 con i ranking originali e costruire il dataset
principale del laboratorio senza perdere prediction valide.

PRINCIPI
--------
- La riga dello storico fornisce esito e stato reale.
- La riga del ranking originale fornisce i driver ex ante.
- Le prediction POSTPONED restano nello storico ma non devono essere scambiate
  con prediction FINAL della stessa partita.
- In presenza di più candidati viene applicato un ordinamento deterministico.

CRITERI DI MATCHING
-------------------
Candidati di base:
- stessa LeagueId;
- stessa Home;
- stessa Away.

Criteri di scelta, in ordine:
1. MatchStatus coerente:
   - storico FINAL preferisce ranking non POSTPONED;
   - storico POSTPONED preferisce ranking POSTPONED;
2. stesso Round;
3. stessa PredictionDate;
4. stessa MatchDate;
5. stessa Score;
6. stessa Band;
7. stessa AlgorithmVersion;
8. distanza temporale minima.

Solo se due candidati restano identici su tutti i criteri la riga viene
considerata ambigua.

GESTIONE RINVIATE
-----------------
Una prediction POSTPONED senza esito viene comunque abbinata al proprio ranking
originale per conservare i driver ex ante, ma resta esclusa automaticamente
dalle statistiche perché Outcome è vuoto.

FILE SCRITTI
-------------
analysis/laboratory/data/06_unmatched_matches.csv
===============================================================================
"""

from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any
import csv


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


def _status(row: dict) -> str:
    return _text(
        row.get("MatchStatus")
    ).upper()


def _has_result(row: dict) -> bool:
    return (
        _text(row.get("HG")) != ""
        and _text(row.get("AG")) != ""
    )


def _reference_date(row: dict) -> date | None:
    return (
        _parse_date(row.get("MatchDate"))
        or _parse_date(row.get("PredictionDate"))
    )


def build_index(
    rankings: list[dict],
) -> dict[
    tuple[str, str, str],
    list[dict],
]:
    index: dict[
        tuple[str, str, str],
        list[dict],
    ] = {}

    for ranking in rankings:
        index.setdefault(
            _base_key(ranking),
            [],
        ).append(ranking)

    return index


def _date_distance_days(
    history_row: dict,
    ranking_row: dict,
) -> int:
    history_date = _reference_date(
        history_row
    )
    ranking_date = _reference_date(
        ranking_row
    )

    if (
        history_date is None
        or ranking_date is None
    ):
        return 999999

    return abs(
        (
            history_date
            - ranking_date
        ).days
    )


def _match_score(
    history_row: dict,
    ranking_row: dict,
) -> tuple:
    history_status = _status(
        history_row
    )
    ranking_status = _status(
        ranking_row
    )

    history_final = (
        history_status == "FINAL"
        or _has_result(history_row)
    )

    history_postponed = (
        history_status == "POSTPONED"
    )

    ranking_postponed = (
        ranking_status == "POSTPONED"
    )

    if history_final:
        status_penalty = (
            1
            if ranking_postponed
            else 0
        )
    elif history_postponed:
        status_penalty = (
            0
            if ranking_postponed
            else 1
        )
    else:
        status_penalty = 0

    same_round = int(
        not (
            _text(history_row.get("Round"))
            and _text(ranking_row.get("Round"))
            and _text(history_row.get("Round"))
            == _text(ranking_row.get("Round"))
        )
    )

    same_prediction_date = int(
        not (
            _text(history_row.get("PredictionDate"))
            and _text(ranking_row.get("PredictionDate"))
            and _text(history_row.get("PredictionDate"))
            == _text(ranking_row.get("PredictionDate"))
        )
    )

    same_match_date = int(
        not (
            _text(history_row.get("MatchDate"))
            and _text(ranking_row.get("MatchDate"))
            and _text(history_row.get("MatchDate"))
            == _text(ranking_row.get("MatchDate"))
        )
    )

    same_score = int(
        not (
            _text(history_row.get("Score"))
            and _text(ranking_row.get("Score"))
            and _text(history_row.get("Score"))
            == _text(ranking_row.get("Score"))
        )
    )

    same_band = int(
        not (
            _text(history_row.get("Band"))
            and _text(ranking_row.get("Band"))
            and _text(history_row.get("Band"))
            == _text(ranking_row.get("Band"))
        )
    )

    same_algorithm = int(
        not (
            _text(history_row.get("AlgorithmVersion"))
            and _text(ranking_row.get("AlgorithmVersion"))
            and _text(history_row.get("AlgorithmVersion"))
            == _text(ranking_row.get("AlgorithmVersion"))
        )
    )

    distance = _date_distance_days(
        history_row,
        ranking_row,
    )

    return (
        status_penalty,
        same_round,
        same_prediction_date,
        same_match_date,
        same_score,
        same_band,
        same_algorithm,
        distance,
    )


def _match_mode(
    history_row: dict,
    ranking_row: dict,
) -> str:
    if (
        _text(history_row.get("PredictionDate"))
        and _text(history_row.get("PredictionDate"))
        == _text(ranking_row.get("PredictionDate"))
    ):
        return "PREDICTION_DATE"

    if (
        _text(history_row.get("MatchDate"))
        and _text(history_row.get("MatchDate"))
        == _text(ranking_row.get("MatchDate"))
    ):
        return "MATCH_DATE"

    if (
        _text(history_row.get("Round"))
        and _text(history_row.get("Round"))
        == _text(ranking_row.get("Round"))
    ):
        return "ROUND"

    return "DETERMINISTIC_TIEBREAK"


def _find_ranking(
    history_row: dict,
    ranking_index: dict[
        tuple[str, str, str],
        list[dict],
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

    scored = [
        (
            _match_score(
                history_row,
                ranking,
            ),
            ranking,
        )
        for ranking in candidates
    ]

    scored.sort(
        key=lambda item: item[0]
    )

    best_score = scored[0][0]

    best = [
        ranking
        for score, ranking in scored
        if score == best_score
    ]

    if len(best) > 1:
        return (
            None,
            "",
            None,
            "AMBIGUOUS_AFTER_ALL_TIEBREAKS",
            len(candidates),
        )

    ranking = best[0]

    distance = _date_distance_days(
        history_row,
        ranking,
    )

    return (
        ranking,
        _match_mode(
            history_row,
            ranking,
        ),
        (
            None
            if distance == 999999
            else distance
        ),
        "",
        len(candidates),
    )


def _write_unmatched(
    rows: list[dict],
) -> None:
    fieldnames = [
        "LeagueId",
        "PredictionDate",
        "MatchDate",
        "Round",
        "Home",
        "Away",
        "Band",
        "Outcome",
        "HG",
        "AG",
        "MatchStatus",
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
    prediction_matches = 0
    match_date_matches = 0
    round_matches = 0
    deterministic_matches = 0
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
                "LeagueId": history_row.get(
                    "LeagueId",
                    "",
                ),
                "PredictionDate": history_row.get(
                    "PredictionDate",
                    "",
                ),
                "MatchDate": history_row.get(
                    "MatchDate",
                    "",
                ),
                "Round": history_row.get(
                    "Round",
                    "",
                ),
                "Home": history_row.get(
                    "Home",
                    "",
                ),
                "Away": history_row.get(
                    "Away",
                    "",
                ),
                "Band": history_row.get(
                    "Band",
                    "",
                ),
                "Outcome": history_row.get(
                    "Outcome",
                    "",
                ),
                "HG": history_row.get(
                    "HG",
                    "",
                ),
                "AG": history_row.get(
                    "AG",
                    "",
                ),
                "MatchStatus": history_row.get(
                    "MatchStatus",
                    "",
                ),
                "Reason": unmatched_reason,
                "BaseCandidates": base_candidates,
                "HistorySource": history_row.get(
                    "SourceFile",
                    "",
                ),
            })
            continue

        row = deepcopy(
            ranking
        )

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
            "MatchStatus",
            "CompetitionGroup",
            "HomeSourceLeagueId",
            "AwaySourceLeagueId",
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

        merged.append(
            row
        )

        match_id += 1
        matched += 1

        if match_mode == "PREDICTION_DATE":
            prediction_matches += 1
        elif match_mode == "MATCH_DATE":
            match_date_matches += 1
        elif match_mode == "ROUND":
            round_matches += 1
        else:
            deterministic_matches += 1

    _write_unmatched(
        unmatched_rows
    )

    print()
    print("===== LABORATORY MERGE =====")
    print(f"Storico caricato:          {len(history)}")
    print(f"Ranking caricati:          {len(rankings)}")
    print(f"Righe abbinate:            {matched}")
    print(f"Match PredictionDate:      {prediction_matches}")
    print(f"Match MatchDate:           {match_date_matches}")
    print(f"Match Round:               {round_matches}")
    print(f"Match tie-break:           {deterministic_matches}")
    print(f"Righe non abbinate:        {len(unmatched_rows)}")
    print(f"Diagnostica:               {UNMATCHED_FILE}")
    print()

    return merged
