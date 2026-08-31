"""
===============================================================================
GioOver2.5 - ranking_history.py
===============================================================================

Gestisce gli storici ranking e il ciclo MatchStatus:

    SCHEDULED -> POSTPONED -> FINAL

Il matching dei risultati usa LeagueId + nomi squadra canonici. MatchDate e
Round servono a scegliere/disambiguare la prediction corretta. Le partite
formalmente posticipate possono essere recuperate anche molto dopo la data
originaria; inoltre, quando esiste una sola prediction irrisolta per la stessa
coppia di squadre, viene ammesso un recupero prudente entro 14 giorni. Questo
copre i casi in cui il provider sposta la data ma il rinvio non è stato
registrato esplicitamente prima dell'arrivo del risultato.
===============================================================================
"""

import csv
from datetime import date, timedelta
from pathlib import Path

from .history import MatchResult
from .team_names import normalize_team_name


POSTPONED_FILE = Path("data/storico/partite_posticipate.csv")
DEBUG_DIR = Path("data/debug/ranking_not_found")

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

RESULT_FIELDS = ["HG", "AG", "Goals", "Over25", "BTTS"]


def _history_file(engine_name: str) -> Path:
    return (
        Path("data/storico/ranking")
        / engine_name
        / f"storico_ranking_{engine_name}.csv"
    )


def _read_history(engine_name: str) -> list[dict]:
    path = _history_file(engine_name)
    if not path.exists():
        return []

    with path.open(newline="", encoding="utf-8-sig") as file_handle:
        return list(csv.DictReader(file_handle, delimiter=";"))


def _collect_fieldnames(rows: list[dict]) -> list[str]:
    fieldnames = list(BASE_FIELDNAMES)
    for row in rows:
        for field_name in row:
            if field_name not in fieldnames:
                fieldnames.append(field_name)
    return fieldnames


def _write_history(engine_name: str, rows: list[dict]) -> None:
    path = _history_file(engine_name)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as file_handle:
        writer = csv.DictWriter(
            file_handle,
            fieldnames=_collect_fieldnames(rows),
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def _text(value) -> str:
    return str(value or "").strip()


def _key(row: dict) -> tuple[str, str, str, str, str]:
    league_id = _text(row.get("LeagueId"))
    match_date = _text(row.get("MatchDate"))
    prediction_date = _text(row.get("PredictionDate"))
    home = normalize_team_name(league_id, row.get("Home", ""))
    away = normalize_team_name(league_id, row.get("Away", ""))

    if match_date:
        return ("MATCH_DATE", league_id, match_date, home, away)

    return ("PREDICTION_DATE", league_id, prediction_date, home, away)


def append_predictions(
    rows: list[dict],
    engine_name: str,
    algorithm_version: str,
) -> None:
    history = _read_history(engine_name)
    existing_keys = {_key(row) for row in history}
    added = 0

    for row in rows:
        history_row = dict(row)
        history_row["AlgorithmVersion"] = (
            row.get("AlgorithmVersion") or algorithm_version
        )
        history_row["MatchStatus"] = (
            _text(row.get("MatchStatus")).upper() or "SCHEDULED"
        )

        for result_field in RESULT_FIELDS:
            history_row[result_field] = ""

        for field_name in BASE_FIELDNAMES:
            history_row.setdefault(field_name, "")

        key = _key(history_row)
        if key in existing_keys:
            continue

        history.append(history_row)
        existing_keys.add(key)
        added += 1

    _write_history(engine_name, history)
    print(
        f"[{engine_name}] Storico ranking aggiornato. "
        f"Nuove previsioni: {added}"
    )


def _parse_date(value: str) -> date | None:
    raw = _text(value)
    if not raw:
        return None

    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _read_postponed_rows() -> list[dict]:
    if not POSTPONED_FILE.exists():
        return []

    with POSTPONED_FILE.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file_handle:
        return list(csv.DictReader(file_handle, delimiter=";"))


def sync_postponed_statuses(engine_name: str) -> int:
    history = _read_history(engine_name)
    postponed_rows = _read_postponed_rows()

    if not history:
        return 0

    postponed_index: dict[tuple[str, str, str], list[dict]] = {}
    for postponed in postponed_rows:
        league_id = _text(postponed.get("LeagueId"))
        key = (
            league_id,
            normalize_team_name(league_id, postponed.get("Home", "")),
            normalize_team_name(league_id, postponed.get("Away", "")),
        )
        postponed_index.setdefault(key, []).append(postponed)

    updated = 0

    for row in history:
        if _text(row.get("HG")) and _text(row.get("AG")):
            if _text(row.get("MatchStatus")).upper() != "FINAL":
                row["MatchStatus"] = "FINAL"
                updated += 1
            continue

        league_id = _text(row.get("LeagueId"))
        key = (
            league_id,
            normalize_team_name(league_id, row.get("Home", "")),
            normalize_team_name(league_id, row.get("Away", "")),
        )
        candidates = postponed_index.get(key, [])
        if not candidates:
            continue

        row_round = _text(row.get("Round"))
        row_match_date = _text(row.get("MatchDate"))

        exact_date = [
            postponed
            for postponed in candidates
            if row_match_date
            and _text(postponed.get("MatchDate")) == row_match_date
        ]
        exact_round = [
            postponed
            for postponed in candidates
            if row_round and _text(postponed.get("Round")) == row_round
        ]

        if exact_date:
            compatible = exact_date
        elif exact_round:
            compatible = exact_round
        elif len(candidates) == 1:
            compatible = candidates
        else:
            compatible = []

        if compatible and _text(row.get("MatchStatus")).upper() != "POSTPONED":
            row["MatchStatus"] = "POSTPONED"
            updated += 1

    if updated:
        _write_history(engine_name, history)

    return updated


def sync_postponed_statuses_all_engines(engine_names: list[str]) -> int:
    total = 0
    for engine_name in engine_names:
        updated = sync_postponed_statuses(engine_name)
        total += updated
        if updated:
            print(
                f"[{engine_name}] MatchStatus sincronizzati: {updated}"
            )
    return total


def _candidate_score(row: dict, match, result_date: date) -> tuple:
    """Minore è il punteggio, migliore è il candidato."""
    row_match_date = _parse_date(row.get("MatchDate", ""))
    prediction_date = _parse_date(row.get("PredictionDate", ""))

    match_date_penalty = 0 if row_match_date == result_date else 1

    row_round = _text(row.get("Round"))
    match_round = _text(getattr(match, "round", ""))
    round_penalty = (
        0 if row_round and match_round and row_round == match_round else 1
    )

    prediction_after_result = (
        1
        if prediction_date is not None and prediction_date > result_date
        else 0
    )
    prediction_distance = (
        abs((result_date - prediction_date).days)
        if prediction_date is not None
        else 999999
    )
    prediction_recency = (
        -prediction_date.toordinal()
        if prediction_date is not None and prediction_date <= result_date
        else 0
    )

    return (
        match_date_penalty,
        round_penalty,
        prediction_after_result,
        prediction_distance,
        prediction_recency,
    )


def _is_unresolved(row: dict) -> bool:
    return not _text(row.get("HG")) and not _text(row.get("AG"))


def _date_is_compatible(
    row: dict,
    result_date: date,
    *,
    is_unique_unresolved_fixture: bool,
    legacy_max_days: int,
    match_date_tolerance_days: int,
    unique_fixture_recovery_days: int,
) -> bool:
    """Valuta la compatibilità temporale tra prediction e risultato.

    Regole:
    - match con MatchDate: tolleranza ordinaria +/- N giorni;
    - POSTPONED: nessun limite superiore rispetto alla data originaria;
    - singola prediction irrisolta per quella coppia di squadre: recupero
      prudente in avanti entro ``unique_fixture_recovery_days``;
    - righe legacy senza MatchDate: finestra basata su PredictionDate.
    """
    row_match_date = _parse_date(row.get("MatchDate", ""))
    prediction_date = _parse_date(row.get("PredictionDate", ""))
    match_status = _text(row.get("MatchStatus")).upper()

    if row_match_date is not None:
        first_valid = row_match_date - timedelta(days=match_date_tolerance_days)
        last_valid = row_match_date + timedelta(days=match_date_tolerance_days)

        if first_valid <= result_date <= last_valid:
            return True

        if match_status == "POSTPONED" and result_date >= row_match_date:
            return True

        if (
            is_unique_unresolved_fixture
            and result_date >= row_match_date
            and result_date
            <= row_match_date + timedelta(days=unique_fixture_recovery_days)
        ):
            return True

        return False

    if prediction_date is not None:
        return result_date <= prediction_date + timedelta(days=legacy_max_days)

    return False


def update_finished_matches(
    engine_name: str,
    finished_matches: list[tuple[str, MatchResult]],
    legacy_max_days: int = 3,
    match_date_tolerance_days: int = 2,
    unique_fixture_recovery_days: int = 14,
) -> None:
    """Aggiorna lo storico ranking con i risultati finali dell'input corrente.

    Le duplicate esatte vengono comunque elaborate: questo permette di
    rilanciare un file risultati già importato nello storico e recuperare una
    prediction che in precedenza non era stata sincronizzata.
    """
    history = _read_history(engine_name)
    if not history:
        print(f"[{engine_name}] Storico ranking vuoto.")
        return

    # Deduplica prediction già presenti nello stesso engine.
    unique_by_key: dict[tuple, dict] = {}
    duplicate_predictions_removed = 0

    for history_row in history:
        history_key = _key(history_row)
        current = unique_by_key.get(history_key)
        if current is None:
            unique_by_key[history_key] = history_row
            continue

        duplicate_predictions_removed += 1
        current_is_final = bool(
            _text(current.get("HG")) and _text(current.get("AG"))
        )
        new_is_final = bool(
            _text(history_row.get("HG")) and _text(history_row.get("AG"))
        )

        if new_is_final or not current_is_final:
            unique_by_key[history_key] = history_row

    history = list(unique_by_key.values())

    if duplicate_predictions_removed:
        print(
            f"[{engine_name}] Prediction duplicate rimosse dallo storico: "
            f"{duplicate_predictions_removed}"
        )

    # Deduplica risultati ricevuti dall'input.
    unique_finished_matches: list[tuple[str, MatchResult]] = []
    seen_finished_keys = set()

    for league_id, match in finished_matches:
        normalized_league_id = _text(league_id)
        result_key = (
            normalized_league_id,
            _text(match.date),
            normalize_team_name(normalized_league_id, match.home),
            normalize_team_name(normalized_league_id, match.away),
            int(match.home_goals),
            int(match.away_goals),
        )
        if result_key in seen_finished_keys:
            continue
        seen_finished_keys.add(result_key)
        unique_finished_matches.append((league_id, match))

    updated = 0
    already_final = 0
    not_found = 0
    ambiguous = 0
    not_found_rows: list[dict] = []

    for league_id, match in unique_finished_matches:
        normalized_league_id = _text(league_id)
        normalized_home = normalize_team_name(
            normalized_league_id, match.home
        )
        normalized_away = normalize_team_name(
            normalized_league_id, match.away
        )
        result_date = _parse_date(str(match.date))

        if not normalized_league_id or result_date is None:
            not_found += 1
            not_found_rows.append(
                {
                    "LeagueId": normalized_league_id,
                    "MatchDate": str(match.date),
                    "Home": match.home,
                    "Away": match.away,
                    "HG": str(match.home_goals),
                    "AG": str(match.away_goals),
                    "Reason": "LeagueId o MatchDate non valida",
                }
            )
            continue

        same_fixture_rows = [
            row
            for row in history
            if _text(row.get("LeagueId")) == normalized_league_id
            and normalize_team_name(
                normalized_league_id, row.get("Home", "")
            )
            == normalized_home
            and normalize_team_name(
                normalized_league_id, row.get("Away", "")
            )
            == normalized_away
        ]

        exact_final_rows = [
            row
            for row in same_fixture_rows
            if _text(row.get("MatchStatus")).upper() == "FINAL"
            and _text(row.get("MatchDate")) == result_date.isoformat()
            and _text(row.get("HG")) == str(match.home_goals)
            and _text(row.get("AG")) == str(match.away_goals)
        ]
        if exact_final_rows:
            already_final += 1
            continue

        unresolved_fixture_rows = [
            row for row in same_fixture_rows if _is_unresolved(row)
        ]
        is_unique_unresolved_fixture = len(unresolved_fixture_rows) == 1

        compatible_rows = [
            row
            for row in unresolved_fixture_rows
            if _date_is_compatible(
                row,
                result_date,
                is_unique_unresolved_fixture=is_unique_unresolved_fixture,
                legacy_max_days=legacy_max_days,
                match_date_tolerance_days=match_date_tolerance_days,
                unique_fixture_recovery_days=unique_fixture_recovery_days,
            )
        ]

        if not compatible_rows:
            not_found += 1
            reason = (
                "Nessuna prediction con stessi nomi canonici"
                if not same_fixture_rows
                else "Prediction trovata ma data/status non compatibili"
            )
            not_found_rows.append(
                {
                    "LeagueId": normalized_league_id,
                    "MatchDate": result_date.isoformat(),
                    "Home": match.home,
                    "Away": match.away,
                    "HG": str(match.home_goals),
                    "AG": str(match.away_goals),
                    "Reason": reason,
                }
            )
            continue

        scored = sorted(
            (
                (_candidate_score(row, match, result_date), row)
                for row in compatible_rows
            ),
            key=lambda item: item[0],
        )
        best_score = scored[0][0]
        best_rows = [row for score, row in scored if score == best_score]

        if len(best_rows) != 1:
            ambiguous += 1
            continue

        selected_row = best_rows[0]
        goals = match.home_goals + match.away_goals

        selected_row["MatchDate"] = result_date.isoformat()
        if not _text(selected_row.get("Round")) and getattr(match, "round", 0):
            selected_row["Round"] = str(match.round)

        selected_row["HG"] = str(match.home_goals)
        selected_row["AG"] = str(match.away_goals)
        selected_row["Goals"] = str(goals)
        selected_row["Over25"] = "OK" if goals >= 3 else "KO"
        selected_row["BTTS"] = (
            "OK"
            if match.home_goals > 0 and match.away_goals > 0
            else "KO"
        )
        selected_row["MatchStatus"] = "FINAL"
        updated += 1

        # Prediction precedenti della stessa gara restano POSTPONED.
        selected_prediction_date = _parse_date(
            selected_row.get("PredictionDate", "")
        )
        for other_row in same_fixture_rows:
            if other_row is selected_row or not _is_unresolved(other_row):
                continue

            other_prediction_date = _parse_date(
                other_row.get("PredictionDate", "")
            )
            if (
                other_prediction_date is not None
                and selected_prediction_date is not None
                and other_prediction_date < selected_prediction_date
            ):
                other_row["MatchStatus"] = "POSTPONED"

    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    debug_file = DEBUG_DIR / f"not_found_{engine_name}.csv"
    with debug_file.open("w", newline="", encoding="utf-8-sig") as file_handle:
        writer = csv.DictWriter(
            file_handle,
            fieldnames=[
                "LeagueId",
                "MatchDate",
                "Home",
                "Away",
                "HG",
                "AG",
                "Reason",
            ],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(not_found_rows)

    _write_history(engine_name, history)

    print(
        f"[{engine_name}] Risultati ricevuti dall'input: "
        f"{len(unique_finished_matches)}"
    )
    print(f"[{engine_name}] Risultati aggiornati: {updated}")
    print(f"[{engine_name}] Risultati già FINAL: {already_final}")
    print(f"[{engine_name}] Partite non trovate: {not_found}")
    print(f"[{engine_name}] Partite ambigue: {ambiguous}")
