import argparse
from pathlib import Path
from .io_utils import read_matches_from_csv, write_results_to_csv
from .scoring import calculate_score


def run(input_file: str, output_file: str, random_seed: int | None = None) -> list[dict]:
    matches = read_matches_from_csv(input_file)
    results = [calculate_score(match, random_seed=random_seed) for match in matches]
    results.sort(key=lambda x: x["score"], reverse=True)
    write_results_to_csv(results, output_file)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="GioOver2.5 - classifica partite Over 2.5")
    parser.add_argument("input_file", help="Percorso CSV input con separatore ;")
    parser.add_argument("--output", default="data/output/classifica_over25.csv", help="Percorso CSV output")
    parser.add_argument("--seed", type=int, default=None, help="Seed per rendere stabile la componente random")
    args = parser.parse_args()

    results = run(args.input_file, args.output, args.seed)

    print("\nClassifica GioOver2.5\n")
    for i, row in enumerate(results, start=1):
        print(f"{i:02d}. {row['match']} - Score {row['score']} - {row['band']}")
    print(f"\nOutput salvato in: {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
