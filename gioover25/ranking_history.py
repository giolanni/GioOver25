import csv
from datetime import date, datetime, timedelta
from pathlib import Path

from .history import read_results_file


RESULTS_DIR = Path("data/storico/risultati")


FIELDNAMES = [
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


def _history_file(engine_name: str) -> Path:
    return Path("data/storico/ranking") / engine_name / f"storico_ranking_{engine_name}.csv"


def _read_history(engine_name: str) -> list[dict]:
    path = _history_file(engine_name)

    if not path.exists():
        return []

    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def _write_history(engine_name: str, rows: list[dict]) -> None:
    path = _history_file(engine_name)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def _normalize_team_name(value: str) -> str:
    return " ".join(str(value or "").strip().lower().split())

def _key(
    row: dict,
) -> tuple[str, str, str, str, str]:
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

    # Compatibilità con le vecchie righe dello storico,
    # create prima dell'introduzione di MatchDate.
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
    algorithm_version: str
) -> None:
    history = _read_history(engine_name)
    existing_keys = {_key(row) for row in history}

    added = 0

    for row in rows:
        history_row = {
            "PredictionDate": row.get("PredictionDate", ""),
            "MatchDate": row.get("MatchDate", ""),
            "LeagueId": row.get("LeagueId", ""),
            "Round": row.get("Round", ""),
            "Home": row.get("Home", ""),
            "Away": row.get("Away", ""),
            "Score": row.get("Score", ""),
            "Band": row.get("Band", ""),

            "HG": "",
            "AG": "",
            "Goals": "",
            "Over25": "",
            "BTTS": "",

            "Reason": row.get("Reason", ""),
            "RankingGapScore": row.get("RankingGapScore", ""),
            "HomeAttackScore": row.get("HomeAttackScore", ""),
            "AwayAttackScore": row.get("AwayAttackScore", ""),
            "HomeDefenseWeaknessScore": row.get("HomeDefenseWeaknessScore", ""),
            "AwayDefenseWeaknessScore": row.get("AwayDefenseWeaknessScore", ""),
            "HomeLast10OverScore": row.get("HomeLast10OverScore", ""),
            "AwayLast10OverScore": row.get("AwayLast10OverScore", ""),
            "HomeVenueOverScore": row.get("HomeVenueOverScore", ""),
            "AwayVenueOverScore": row.get("AwayVenueOverScore", ""),
            "BTTSProfileScore": row.get("BTTSProfileScore", ""),
            "AlgorithmVersion": row.get("AlgorithmVersion", ""),
        }

        key = _key(history_row)

        if key in existing_keys:
            continue

        history.append(history_row)
        existing_keys.add(key)
        added += 1

    _write_history(engine_name, history)

    print(f"[{engine_name}] Storico ranking aggiornato. Nuove previsioni: {added}")


def _parse_date(value: str) -> date | None:
    raw = str(value or "").strip()

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
    history = _read_history(engine_name)

    if not history:
        print(
            f"[{engine_name}] Storico ranking vuoto."
        )
        return

    results_cache: dict[str, list] = {}

    updated = 0
    not_found = 0
    ambiguous = 0

    for row in history:
        if (
            str(row.get("HG", "")).strip() != ""
            and str(row.get("AG", "")).strip() != ""
        ):
            continue

        league_id = str(
            row.get("LeagueId", "")
        ).strip()

        results_file = (
            RESULTS_DIR
            / f"{league_id}.csv"
        )

        if not results_file.exists():
            not_found += 1
            continue

        if league_id not in results_cache:
            results_cache[league_id] = (
                read_results_file(results_file)
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
                _normalize_team_name(match.home)
                != home
            ):
                continue

            if (
                _normalize_team_name(match.away)
                != away
            ):
                continue

            result_date = _parse_date(
                str(match.date)
            )

            if result_date is None:
                continue

            if match_date is not None:
                # Nuovi ranking: data esatta della partita.
                if result_date != match_date:
                    continue

            else:
                # Vecchi ranking: compatibilità temporanea.
                prediction_date = _parse_date(
                    row.get("PredictionDate", "")
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

        row["HG"] = str(match.home_goals)
        row["AG"] = str(match.away_goals)
        row["Goals"] = str(goals)

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