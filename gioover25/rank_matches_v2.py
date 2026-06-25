import argparse
import csv
from pathlib import Path

from .history import read_results_file
from .match_statistics import build_match_statistics
from .registry import get_league_info
from .scoring_v2 import calculate_score_v2
from .ranking_history import append_predictions


INPUT_REQUIRED_COLUMNS = {
    "LeagueId",
    "Home",
    "Away",
}


RESULTS_DIR = Path("data/storico/risultati")
OUTPUT_DIR = Path("data/output_ranking")


def _int(value: str) -> int:
    value = (value or "").strip()
    return int(value) if value else 0

def infer_next_round(matches: list) -> int:
    if not matches:
        return 1

    return max(match.round for match in matches) + 1

def read_matches_to_rank(path: str | Path) -> list[dict]:
    input_path = Path(path)

    if not input_path.exists():
        raise FileNotFoundError(f"File input partite non trovato: {input_path}")

    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")

        missing = INPUT_REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                "File input partite non valido. Mancano le colonne: "
                + ", ".join(sorted(missing))
            )

        return list(reader)


def rank_matches(input_file: str | Path, output_file: str | Path) -> None:
    rows = read_matches_to_rank(input_file)

    results = []

    for row in rows:
        league_id = row["LeagueId"].strip()
        results_file = RESULTS_DIR / f"{league_id}.csv"
        matches = read_results_file(results_file)

        round_number = infer_next_round(matches)
        home = row["Home"].strip()
        away = row["Away"].strip()

        league_info = get_league_info(league_id)

        match_stats = build_match_statistics(
            matches=matches,
            home_team=home,
            away_team=away,
            before_round=round_number,
        )

        score = calculate_score_v2(match_stats, league_info)

        results.append(
            {
                "LeagueId": league_id,
                "Round": round_number,
                "Home": home,
                "Away": away,
                "Match": f"{home} - {away}",
                "Score": score.score,
                "Band": score.band,
                "RankingGapComponent": score.ranking_gap_score,
                "HomeAttackComponent": score.home_attack_score,
                "AwayDefenseWeaknessComponent": score.away_defense_weakness_score,
                "HomeLast10OverComponent": score.home_last10_over_score,
                "AwayLast10OverComponent": score.away_last10_over_score,
                "Reason": score.reason,
            }
        )

    results.sort(key=lambda x: x["Score"], reverse=True)

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "LeagueId",
        "Round",
        "Home",
        "Away",
        "Match",
        "Score",
        "Band",
        "RankingGapComponent",
        "HomeAttackComponent",
        "AwayDefenseWeaknessComponent",
        "HomeLast10OverComponent",
        "AwayLast10OverComponent",
        "Reason",
    ]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(results)

    print(f"Ranking generato: {output_path.resolve()}")
    append_predictions(results)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera ranking partite GioOver2.5 v2.0"
    )

    parser.add_argument(
        "input_file",
        help="CSV partite da analizzare"
    )

    parser.add_argument(
        "--output",
        default="data/output_ranking/ranking_v2.csv",
        help="CSV output ranking"
    )

    args = parser.parse_args()

    rank_matches(args.input_file, args.output)


if __name__ == "__main__":
    main()