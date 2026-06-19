import csv
from pathlib import Path
from .models import MatchInput, TeamStats


def _int(row: dict, key: str) -> int:
    value = row.get(key, "")
    if value is None or str(value).strip() == "":
        return 0
    return int(str(value).strip())


def read_matches_from_csv(path: str | Path) -> list[MatchInput]:
    matches: list[MatchInput] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            home = TeamStats(
                name=row["home_team"].strip(),
                position=_int(row, "home_position"),
                goals_for=_int(row, "home_goals_for"),
                goals_against=_int(row, "home_goals_against"),
                played=_int(row, "home_played"),
                last10_over25=_int(row, "home_last10_over25"),
                last10_goals_for=_int(row, "home_last10_goals_for"),
                last10_goals_against=_int(row, "home_last10_goals_against"),
            )
            away = TeamStats(
                name=row["away_team"].strip(),
                position=_int(row, "away_position"),
                goals_for=_int(row, "away_goals_for"),
                goals_against=_int(row, "away_goals_against"),
                played=_int(row, "away_played"),
                last10_over25=_int(row, "away_last10_over25"),
                last10_goals_for=_int(row, "away_last10_goals_for"),
                last10_goals_against=_int(row, "away_last10_goals_against"),
            )
            matches.append(MatchInput(home=home, away=away))
    return matches


def write_results_to_csv(results: list[dict], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if not results:
        return
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()), delimiter=";")
        writer.writeheader()
        writer.writerows(results)
