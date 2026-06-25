import csv
from pathlib import Path
from datetime import datetime

from .history import read_results_file


RANKING_HISTORY_FILE = Path("data/storico/storico_ranking.csv")
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


def _read_history() -> list[dict]:
    if not RANKING_HISTORY_FILE.exists():
        return []

    with open(RANKING_HISTORY_FILE, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def _write_history(rows: list[dict]) -> None:
    RANKING_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(RANKING_HISTORY_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def _key(row: dict) -> tuple[str, str, str]:
    return (
        row["LeagueId"].strip(),
        row["Home"].strip().lower(),
        row["Away"].strip().lower(),
    )


def append_predictions(rows: list[dict], algorithm_version: str = "2.0.0") -> None:
    history = _read_history()
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

    _write_history(history)

    print(f"Storico ranking aggiornato. Nuove previsioni salvate: {added}")


def update_finished_matches() -> None:
    history = _read_history()

    if not history:
        return

    updated = 0

    for row in history:
        if row.get("HG", "").strip() != "" and row.get("AG", "").strip() != "":
            continue

        league_id = row["LeagueId"].strip()
        results_file = RESULTS_DIR / f"{league_id}.csv"

        if not results_file.exists():
            continue

        matches = read_results_file(results_file)

        for match in matches:
            if (
                match.home.strip().lower() == row["Home"].strip().lower()
                and match.away.strip().lower() == row["Away"].strip().lower()
            ):
                goals = match.home_goals + match.away_goals

                row["HG"] = match.home_goals
                row["AG"] = match.away_goals
                row["Goals"] = goals
                row["Over25"] = "OK" if goals >= 3 else "KO"
                row["BTTS"] = "OK" if match.home_goals > 0 and match.away_goals > 0 else "KO"

                updated += 1
                break

    _write_history(history)

    print(f"Storico ranking completato. Risultati aggiornati: {updated}")