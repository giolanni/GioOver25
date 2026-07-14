"""
===============================================================================
GioOver2.5 - analysis/laboratory/merger.py
===============================================================================

Unisce storico ranking e ranking originali.

Matching:

1) LeagueId + MatchDate + Home + Away

fallback

2) LeagueId + PredictionDate + Home + Away

Produce una lista di partite completa.
===============================================================================
"""

from copy import deepcopy


# ---------------------------------------------------------------------


def _text(value):

    if value is None:
        return ""

    return str(value).strip()


# ---------------------------------------------------------------------


def build_key(row):

    match_date = _text(row.get("MatchDate"))

    if match_date:

        return (

            _text(row.get("LeagueId")),

            match_date,

            _text(row.get("Home")),

            _text(row.get("Away")),

        ), "MATCH_DATE"

    return (

        _text(row.get("LeagueId")),

        _text(row.get("PredictionDate")),

        _text(row.get("Home")),

        _text(row.get("Away")),

    ), "PREDICTION_DATE"


# ---------------------------------------------------------------------


def build_index(rankings):

    index = {}

    for row in rankings:

        key, mode = build_key(row)

        row["MatchMode"] = mode

        index[key] = row

    return index


# ---------------------------------------------------------------------


def merge_matches(history, rankings):

    ranking_index = build_index(rankings)

    merged = []

    match_id = 1

    for h in history:

        key, mode = build_key(h)

        if key not in ranking_index:

            continue

        ranking = ranking_index[key]

        row = deepcopy(ranking)

        #
        # Lo storico prevale
        #

        for field in (

            "Band",

            "Outcome",

            "HG",

            "AG",

            "Score",

        ):

            if field in h:

                row[field] = h[field]

        #
        # Se nello storico esiste MatchDate
        # mantiene quella
        #

        if _text(h.get("MatchDate")):

            row["MatchDate"] = h["MatchDate"]

        row["HistorySource"] = h.get("SourceFile", "")

        row["RankingSource"] = ranking.get("SourceFile", "")

        row["MatchMode"] = mode

        row["MatchId"] = match_id

        match_id += 1

        merged.append(row)

    return merged