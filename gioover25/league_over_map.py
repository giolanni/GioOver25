from pathlib import Path
import csv

from gioover25.history import read_results_file


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

OUTPUT_FIELDS = [
    "LeagueId",
    "Matches",
    "Over15",
    "Over15Pct",
    "Over25",
    "Over25Pct",
    "Over35",
    "Over35Pct",
    "BTTS",
    "BTTSPct",
    "AvgGoals",
]


def calculate_league_over_row(league_id: str, matches: list) -> dict:
    total = len(matches)

    if total == 0:
        return {
            "LeagueId": league_id,
            "Matches": 0,
            "Over15": 0,
            "Over15Pct": 0,
            "Over25": 0,
            "Over25Pct": 0,
            "Over35": 0,
            "Over35Pct": 0,
            "BTTS": 0,
            "BTTSPct": 0,
            "AvgGoals": 0,
        }

    goals = [m.home_goals + m.away_goals for m in matches]

    over15 = sum(1 for g in goals if g >= 2)
    over25 = sum(1 for g in goals if g >= 3)
    over35 = sum(1 for g in goals if g >= 4)
    btts = sum(1 for m in matches if m.home_goals > 0 and m.away_goals > 0)

    return {
        "LeagueId": league_id,
        "Matches": total,
        "Over15": over15,
        "Over15Pct": round(over15 / total * 100, 2),
        "Over25": over25,
        "Over25Pct": round(over25 / total * 100, 2),
        "Over35": over35,
        "Over35Pct": round(over35 / total * 100, 2),
        "BTTS": btts,
        "BTTSPct": round(btts / total * 100, 2),
        "AvgGoals": round(sum(goals) / total, 2),
    }


def rebuild_league_over_map() -> Path:
    results_dir = DATA_DIR / "storico" / "risultati"
    output_file = DATA_DIR / "storico" / "league_over_map.csv"

    rows = []

    for results_file in sorted(results_dir.glob("*.csv")):
        league_id = results_file.stem
        matches = read_results_file(results_file)
        rows.append(calculate_league_over_row(league_id, matches))

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    return output_file