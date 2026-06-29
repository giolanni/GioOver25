import csv
from datetime import datetime
from pathlib import Path

from .history import read_results_file


RESULTS_DIR = Path("data/storico/risultati")


FIELDNAMES = [
    "PredictionDate",
    "AlgorithmVersion",
    "LeagueId",
    "Round",
    "Home",
    "Away",
    "Match",
    "Score",
    "Band",
    "HG",
    "AG",
    "Goals",
    "Over25",
    "BTTS",
]


def _history_file(engine_name: str) -> Path:
    return Path("data/storico/ranking") / engine_name / "storico_ranking.csv"


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


def _key(row: dict) -> tuple[str, str, str]:
    return (
        row["LeagueId"].strip(),
        row["Home"].strip().lower(),
        row["Away"].strip().lower(),
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
        new_row = {
            "PredictionDate": datetime.now().strftime("%Y-%m-%d"),
            "AlgorithmVersion": algorithm_version,
            "LeagueId": row["LeagueId"],
            "Round": row["Round"],
            "Home": row["Home"],
            "Away": row["Away"],
            "Match": row["Match"],
            "Score": row["Score"],
            "Band": row["Band"],
            "HG": "",
            "AG": "",
            "Goals": "",
            "Over25": "",
            "BTTS": "",
        }

        key = _key(new_row)

        if key in existing_keys:
            continue

        history.append(new_row)
        existing_keys.add(key)
        added += 1

    _write_history(engine_name, history)

    print(f"[{engine_name}] Storico ranking aggiornato. Nuove previsioni: {added}")


def _normalize_team_name(value: str) -> str:
    return " ".join(str(value or "").strip().lower().split())


def update_finished_matches(engine_name: str) -> None:
    history = _read_history(engine_name)

    if not history:
        print(f"[{engine_name}] Storico ranking vuoto.")
        return

    results_cache = {}
    updated = 0
    not_found = 0

    for row in history:
        if row.get("HG", "").strip() != "" and row.get("AG", "").strip() != "":
            continue

        league_id = row["LeagueId"].strip()
        results_file = RESULTS_DIR / f"{league_id}.csv"

        if not results_file.exists():
            not_found += 1
            print(f"[{engine_name}] File risultati mancante: {league_id}")
            continue

        if league_id not in results_cache:
            matches = read_results_file(results_file)
            match_index = {}

            for match in matches:
                key = (
                    _normalize_team_name(match.home),
                    _normalize_team_name(match.away),
                )
                match_index[key] = match

            results_cache[league_id] = match_index

        key = (
            _normalize_team_name(row["Home"]),
            _normalize_team_name(row["Away"]),
        )

        match = results_cache[league_id].get(key)

        if match is None:
            not_found += 1
            print(
                f"[{engine_name}] NON TROVATA: "
                f"{league_id} | {row['Home']} - {row['Away']}"
            )
            continue

        goals = match.home_goals + match.away_goals

        row["HG"] = str(match.home_goals)
        row["AG"] = str(match.away_goals)
        row["Goals"] = str(goals)
        row["Over25"] = "OK" if goals >= 3 else "KO"
        row["BTTS"] = "OK" if match.home_goals > 0 and match.away_goals > 0 else "KO"

        updated += 1

    _write_history(engine_name, history)

    print(f"[{engine_name}] Risultati aggiornati nello storico ranking: {updated}")
    print(f"[{engine_name}] Partite non trovate: {not_found}")