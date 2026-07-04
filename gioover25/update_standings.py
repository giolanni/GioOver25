from pathlib import Path

from .standings import generate_current_standings_file


RESULTS_DIR = Path("data/storico/risultati")
STANDINGS_DIR = Path("data/storico/classifiche_calcolate")


def update_all_standings() -> None:
    STANDINGS_DIR.mkdir(parents=True, exist_ok=True)

    updated = 0

    for results_file in sorted(RESULTS_DIR.glob("*.csv")):
        league_id = results_file.stem
        standings_file = STANDINGS_DIR / f"{league_id}.csv"

        generate_current_standings_file(results_file, standings_file)

        updated += 1
        print(f"AGGIORNATA: {league_id}")

    print()
    print(f"Classifiche aggiornate: {updated}")


def main() -> None:
    update_all_standings()


if __name__ == "__main__":
    main()