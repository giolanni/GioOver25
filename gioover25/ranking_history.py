"""
===============================================================================
GioOver2.5 - ranking_history.py
===============================================================================

SCOPO
-----
Gestire gli storici ranking e il ciclo MatchStatus:

    SCHEDULED -> POSTPONED -> FINAL

PRINCIPI
--------
- ogni nuova prediction nasce SCHEDULED;
- una prediction presente nel registro rinviate diventa POSTPONED;
- quando arriva il risultato finale, la prediction più recente e compatibile
  viene aggiornata a FINAL;
- le prediction precedenti della stessa gara restano POSTPONED;
- MatchDate viene aggiornata alla data reale del recupero;
- Round resta quello originario della gara rinviata quando disponibile.

FILE LETTI
----------
    data/storico/ranking/<engine>/storico_ranking_<engine>.csv
    data/storico/risultati/<LeagueId>.csv
    data/storico/partite_posticipate.csv

FILE SCRITTI
-------------
    data/storico/ranking/<engine>/storico_ranking_<engine>.csv
===============================================================================
"""

import csv
from datetime import date, timedelta
from pathlib import Path

from .history import read_results_file


RESULTS_DIR = Path("data/storico/risultati")
POSTPONED_FILE = Path(
    "data/storico/partite_posticipate.csv"
)


BASE_FIELDNAMES = [
    "PredictionDate",
    "MatchDate",
    "LeagueId",
    "Round",
    "Home",
    "Away",
    "Score",
    "Band",
    "MatchStatus",
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


def _history_file(
    engine_name: str,
) -> Path:
    return (
        Path("data/storico/ranking")
        / engine_name
        / f"storico_ranking_{engine_name}.csv"
    )


def _read_history(
    engine_name: str,
) -> list[dict]:
    path = _history_file(
        engine_name
    )

    if not path.exists():
        return []

    with path.open(
        newline="",
        encoding="utf-8-sig",
    ) as file_handle:
        return list(
            csv.DictReader(
                file_handle,
                delimiter=";",
            )
        )


def _collect_fieldnames(
    rows: list[dict],
) -> list[str]:
    fieldnames = list(
        BASE_FIELDNAMES
    )

    for row in rows:
        for field_name in row:
            if field_name not in fieldnames:
                fieldnames.append(
                    field_name
                )

    return fieldnames


def _write_history(
    engine_name: str,
    rows: list[dict],
) -> None:
    path = _history_file(
        engine_name
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file_handle:
        writer = csv.DictWriter(
            file_handle,
            fieldnames=_collect_fieldnames(
                rows
            ),
            delimiter=";",
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(
            rows
        )


def _normalize_team_name(
    value: str,
) -> str:
    return " ".join(
        str(value or "")
        .strip()
        .lower()
        .split()
    )


def _text(
    value,
) -> str:
    return str(
        value or ""
    ).strip()


def _key(
    row: dict,
) -> tuple[
    str,
    str,
    str,
    str,
    str,
]:
    league_id = _text(
        row.get("LeagueId")
    )

    match_date = _text(
        row.get("MatchDate")
    )

    prediction_date = _text(
        row.get("PredictionDate")
    )

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
    history = _read_history(
        engine_name
    )

    existing_keys = {
        _key(row)
        for row in history
    }

    added = 0

    for row in rows:
        history_row = dict(
            row
        )

        history_row[
            "AlgorithmVersion"
        ] = (
            row.get(
                "AlgorithmVersion"
            )
            or algorithm_version
        )

        history_row[
            "MatchStatus"
        ] = (
            _text(
                row.get(
                    "MatchStatus"
                )
            ).upper()
            or "SCHEDULED"
        )

        for result_field in RESULT_FIELDS:
            history_row[
                result_field
            ] = ""

        for field_name in BASE_FIELDNAMES:
            history_row.setdefault(
                field_name,
                "",
            )

        key = _key(
            history_row
        )

        if key in existing_keys:
            continue

        history.append(
            history_row
        )

        existing_keys.add(
            key
        )

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
    raw = _text(
        value
    )

    if not raw:
        return None

    try:
        return date.fromisoformat(
            raw
        )
    except ValueError:
        return None


def _read_postponed_rows() -> list[dict]:
    if not POSTPONED_FILE.exists():
        return []

    with POSTPONED_FILE.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as file_handle:
        return list(
            csv.DictReader(
                file_handle,
                delimiter=";",
            )
        )


def sync_postponed_statuses(
    engine_name: str,
) -> int:
    history = _read_history(
        engine_name
    )

    postponed_rows = (
        _read_postponed_rows()
    )

    if not history:
        return 0

    postponed_index = {}

    for postponed in postponed_rows:
        key = (
            _text(
                postponed.get(
                    "LeagueId"
                )
            ),
            _normalize_team_name(
                postponed.get(
                    "Home",
                    "",
                )
            ),
            _normalize_team_name(
                postponed.get(
                    "Away",
                    "",
                )
            ),
        )

        postponed_index.setdefault(
            key,
            [],
        ).append(
            postponed
        )

    updated = 0

    for row in history:
        if (
            _text(row.get("HG"))
            and _text(row.get("AG"))
        ):
            if (
                _text(
                    row.get(
                        "MatchStatus"
                    )
                ).upper()
                != "FINAL"
            ):
                row[
                    "MatchStatus"
                ] = "FINAL"
                updated += 1
            continue

        key = (
            _text(
                row.get(
                    "LeagueId"
                )
            ),
            _normalize_team_name(
                row.get(
                    "Home",
                    "",
                )
            ),
            _normalize_team_name(
                row.get(
                    "Away",
                    "",
                )
            ),
        )

        candidates = (
            postponed_index.get(
                key,
                [],
            )
        )

        if candidates:
            row_round = _text(
                row.get("Round")
            )

            row_match_date = _text(
                row.get("MatchDate")
            )

            # Il matching principale usa LeagueId + Home + Away.
            # MatchDate e Round servono soltanto a disambiguare eventuali
            # confronti ripetuti tra le stesse squadre: il Round calcolato
            # dal ranking può infatti non coincidere con quello ufficiale.
            exact_date = [
                postponed
                for postponed in candidates
                if (
                    row_match_date
                    and _text(postponed.get("MatchDate"))
                    == row_match_date
                )
            ]

            exact_round = [
                postponed
                for postponed in candidates
                if (
                    row_round
                    and _text(postponed.get("Round"))
                    == row_round
                )
            ]

            if exact_date:
                compatible = exact_date
            elif exact_round:
                compatible = exact_round
            elif len(candidates) == 1:
                compatible = candidates
            else:
                compatible = []

            if compatible:
                if (
                    _text(
                        row.get(
                            "MatchStatus"
                        )
                    ).upper()
                    != "POSTPONED"
                ):
                    row[
                        "MatchStatus"
                    ] = "POSTPONED"
                    updated += 1
                continue

    if updated:
        _write_history(
            engine_name,
            history,
        )

    return updated


def sync_postponed_statuses_all_engines(
    engine_names: list[str],
) -> int:
    total = 0

    for engine_name in engine_names:
        updated = (
            sync_postponed_statuses(
                engine_name
            )
        )

        total += updated

        if updated:
            print(
                f"[{engine_name}] "
                f"MatchStatus sincronizzati: "
                f"{updated}"
            )

    return total


def _candidate_score(
    row: dict,
    match,
    result_date: date,
) -> tuple:
    """
    Minore è il punteggio, migliore è il candidato.

    Preferenze:
    1. MatchDate esatta;
    2. Round uguale;
    3. PredictionDate più recente ma non successiva al risultato;
    4. distanza temporale minima.
    """
    row_match_date = _parse_date(
        row.get("MatchDate", "")
    )

    prediction_date = _parse_date(
        row.get("PredictionDate", "")
    )

    match_date_penalty = (
        0
        if row_match_date == result_date
        else 1
    )

    row_round = _text(
        row.get("Round")
    )

    match_round = _text(
        getattr(
            match,
            "round",
            "",
        )
    )

    round_penalty = (
        0
        if (
            row_round
            and match_round
            and row_round
            == match_round
        )
        else 1
    )

    prediction_after_result = (
        1
        if (
            prediction_date is not None
            and prediction_date
            > result_date
        )
        else 0
    )

    prediction_distance = (
        abs(
            (
                result_date
                - prediction_date
            ).days
        )
        if prediction_date is not None
        else 999999
    )

    # Preferisce la prediction più recente tra quelle precedenti al match.
    prediction_recency = (
        -prediction_date.toordinal()
        if (
            prediction_date is not None
            and prediction_date
            <= result_date
        )
        else 0
    )

    return (
        match_date_penalty,
        round_penalty,
        prediction_after_result,
        prediction_distance,
        prediction_recency,
    )


def update_finished_matches(
    engine_name: str,
    legacy_max_days: int = 3,
    match_date_tolerance_days: int = 2,
) -> None:
    history = _read_history(
        engine_name
    )

    if not history:
        print(
            f"[{engine_name}] "
            "Storico ranking vuoto."
        )
        return

    results_cache: dict[
        str,
        list,
    ] = {}

    updated = 0
    not_found = 0
    ambiguous = 0

    unresolved_rows = [
        row
        for row in history
        if not (
            _text(row.get("HG"))
            and _text(row.get("AG"))
        )
    ]

    grouped_rows = {}

    for row in unresolved_rows:
        key = (
            _text(
                row.get("LeagueId")
            ),
            _normalize_team_name(
                row.get(
                    "Home",
                    "",
                )
            ),
            _normalize_team_name(
                row.get(
                    "Away",
                    "",
                )
            ),
        )

        grouped_rows.setdefault(
            key,
            [],
        ).append(
            row
        )

    for (
        league_id,
        home,
        away,
    ), rows in grouped_rows.items():
        if not league_id:
            not_found += len(
                rows
            )
            continue

        results_file = (
            RESULTS_DIR
            / f"{league_id}.csv"
        )

        if not results_file.exists():
            not_found += len(
                rows
            )
            continue

        if league_id not in results_cache:
            results_cache[
                league_id
            ] = read_results_file(
                results_file
            )

        result_candidates = []

        for match in results_cache[
            league_id
        ]:
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

            compatible_rows = []

            for row in rows:
                row_match_date = (
                    _parse_date(
                        row.get(
                            "MatchDate",
                            "",
                        )
                    )
                )

                prediction_date = (
                    _parse_date(
                        row.get(
                            "PredictionDate",
                            "",
                        )
                    )
                )

                if row_match_date is not None:
                    first_valid = (
                        row_match_date
                        - timedelta(
                            days=(
                                match_date_tolerance_days
                            )
                        )
                    )

                    last_valid = (
                        row_match_date
                        + timedelta(
                            days=(
                                match_date_tolerance_days
                            )
                        )
                    )

                    if not (
                        first_valid
                        <= result_date
                        <= last_valid
                    ):
                        continue

                elif prediction_date is not None:
                    if (
                        result_date
                        < prediction_date
                    ):
                        continue

                    if (
                        result_date
                        > prediction_date
                        + timedelta(
                            days=legacy_max_days
                        )
                    ):
                        continue

                else:
                    continue

                compatible_rows.append(
                    row
                )

            if compatible_rows:
                result_candidates.append(
                    (
                        match,
                        result_date,
                        compatible_rows,
                    )
                )

        if not result_candidates:
            not_found += len(
                rows
            )
            continue

        # Per ogni risultato sceglie una sola prediction:
        # la più recente e temporalmente coerente.
        for (
            match,
            result_date,
            compatible_rows,
        ) in result_candidates:
            scored = sorted(
                (
                    _candidate_score(
                        row,
                        match,
                        result_date,
                    ),
                    row,
                )
                for row in compatible_rows
            )

            best_score = scored[
                0
            ][0]

            best_rows = [
                row
                for score, row in scored
                if score == best_score
            ]

            if len(best_rows) != 1:
                ambiguous += 1
                continue

            row = best_rows[0]

            goals = (
                match.home_goals
                + match.away_goals
            )

            row["MatchDate"] = (
                result_date.isoformat()
            )

            # Mantiene il Round originario della prediction.
            # Lo valorizza dal risultato solo se nello storico è vuoto.
            if (
                not _text(
                    row.get("Round")
                )
                and getattr(
                    match,
                    "round",
                    0,
                )
            ):
                row["Round"] = str(
                    match.round
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

            row["MatchStatus"] = (
                "FINAL"
            )

            updated += 1

            # Le prediction precedenti della stessa gara restano POSTPONED.
            for other_row in rows:
                if other_row is row:
                    continue

                other_prediction_date = (
                    _parse_date(
                        other_row.get(
                            "PredictionDate",
                            "",
                        )
                    )
                )

                selected_prediction_date = (
                    _parse_date(
                        row.get(
                            "PredictionDate",
                            "",
                        )
                    )
                )

                if (
                    other_prediction_date
                    is not None
                    and selected_prediction_date
                    is not None
                    and other_prediction_date
                    < selected_prediction_date
                    and not _text(
                        other_row.get("HG")
                    )
                    and not _text(
                        other_row.get("AG")
                    )
                ):
                    other_row[
                        "MatchStatus"
                    ] = "POSTPONED"

    _write_history(
        engine_name,
        history,
    )

    print(
        f"[{engine_name}] "
        f"Risultati aggiornati: "
        f"{updated}"
    )

    print(
        f"[{engine_name}] "
        f"Partite non trovate: "
        f"{not_found}"
    )

    print(
        f"[{engine_name}] "
        f"Partite ambigue: "
        f"{ambiguous}"
    )
