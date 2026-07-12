import argparse
import csv
from datetime import date
from pathlib import Path

from .history import read_results_file
from .match_statistics import build_match_statistics
from .registry import get_league_info
from .ranking_history import append_predictions
from .engines.factory import get_engine, get_available_engines


INPUT_REQUIRED_COLUMNS = {
    "LeagueId",
    "MatchDate",
    "Home",
    "Away",
}

RESULTS_DIR = Path("data/storico/risultati")
OUTPUT_DIR = Path("data/output_ranking")


FIELDNAMES = [
    "PredictionDate",
    "MatchDate",
    "LeagueId",
    "Round",
    "Home",
    "Away",
    "Score",
    "Band",
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


def infer_next_round(matches: list) -> int:
    if not matches:
        return 1

    return max(match.round for match in matches) + 1


def score_value(score, field: str):
    return getattr(score, field, "")


def read_matches_to_rank(path: str | Path) -> list[dict]:
    input_path = Path(path)

    if not input_path.exists():
        raise FileNotFoundError(f"File input partite non trovato: {input_path}")

    with input_path.open("r", newline="", encoding="utf-8-sig") as f:
        lines = [line for line in f if line.strip()]

    reader = csv.DictReader(lines, delimiter=";")

    missing = INPUT_REQUIRED_COLUMNS - set(reader.fieldnames or [])
    if missing:
        raise ValueError(
            "File input partite non valido. Mancano le colonne: "
            + ", ".join(sorted(missing))
        )

    return list(reader)


def build_output_row(
    *,
    prediction_date: str,
    match_date: str,
    algorithm_version: str,
    league_id: str,
    round_number: int,
    home: str,
    away: str,
    score,
) -> dict:
    return {
        "PredictionDate": prediction_date,
        "MatchDate": match_date,
        "LeagueId": league_id,
        "Round": round_number,
        "Home": home,
        "Away": away,
        "Score": score_value(score, "score"),
        "Band": score_value(score, "band"),
        "Reason": score_value(score, "reason"),
        "RankingGapScore": score_value(score, "ranking_gap_score"),
        "HomeAttackScore": score_value(score, "home_attack_score"),
        "AwayAttackScore": score_value(score, "away_attack_score"),
        "HomeDefenseWeaknessScore": score_value(
            score,
            "home_defense_weakness_score",
        ),
        "AwayDefenseWeaknessScore": score_value(
            score,
            "away_defense_weakness_score",
        ),
        "HomeLast10OverScore": score_value(score, "home_last10_over_score"),
        "AwayLast10OverScore": score_value(score, "away_last10_over_score"),
        "HomeVenueOverScore": score_value(score, "home_venue_over_score"),
        "AwayVenueOverScore": score_value(score, "away_venue_over_score"),
        "BTTSProfileScore": score_value(score, "btts_profile_score"),
        "AlgorithmVersion": algorithm_version,
    }


def rank_matches(
    input_file: str | Path,
    output_file: str | Path,
    engine_name: str = "v20",
) -> None:
    engine = get_engine(engine_name)

    prediction_date = date.today().isoformat()
    algorithm_version = engine.ENGINE_VERSION

    rows = read_matches_to_rank(input_file)
    results = []

    for row in rows:
        league_id = row["LeagueId"].strip()
        match_date = row["MatchDate"].strip()
        home = row["Home"].strip()
        away = row["Away"].strip()

        league_info = get_league_info(league_id)

        results_file = RESULTS_DIR / f"{league_id}.csv"
        if not results_file.exists():
            raise FileNotFoundError(f"File risultati non trovato: {results_file}")

        matches = read_results_file(results_file)
        round_number = infer_next_round(matches)

        match_stats = build_match_statistics(
            matches=matches,
            home_team=home,
            away_team=away,
            before_round=round_number,
        )

        score = engine.calculate_score(match_stats, league_info)

        results.append(
            build_output_row(
                prediction_date=prediction_date,
                match_date=match_date,
                algorithm_version=algorithm_version,
                league_id=league_id,
                round_number=round_number,
                home=home,
                away=away,
                score=score,
            )
        )

    results.sort(key=lambda x: float(x["Score"] or 0), reverse=True)

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter=";")
        writer.writeheader()
        writer.writerows(results)

    print(f"[{engine_name}] Ranking generato: {output_path.resolve()}")

    append_predictions(
        results,
        engine_name=engine_name,
        algorithm_version=algorithm_version,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera ranking partite GioOver2.5 v2.0"
    )

    parser.add_argument(
        "input_file",
        help="CSV partite da analizzare",
    )

    parser.add_argument(
        "--engine",
        default="v20",
        choices=get_available_engines() + ["all"],
        help="Motore di scoring da usare",
    )

    parser.add_argument(
        "--output",
        default=None,
        help="CSV output ranking",
    )

    args = parser.parse_args()

    input_path = Path(args.input_file)
    base_name = input_path.stem.replace("partite", "ranking")

    if args.engine == "all":
        for engine_name in get_available_engines():
            output_file = (
                OUTPUT_DIR
                / engine_name
                / f"{base_name}_{engine_name}.csv"
            )

            rank_matches(
                args.input_file,
                output_file,
                engine_name,
            )
    else:
        output_file = (
            Path(args.output)
            if args.output
            else OUTPUT_DIR / args.engine / f"{base_name}_{args.engine}.csv"
        )

        rank_matches(
            args.input_file,
            output_file,
            args.engine,
        )


if __name__ == "__main__":
    main()