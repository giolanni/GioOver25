import argparse
import csv
from collections import defaultdict
from pathlib import Path

from .history import MatchResult, read_results_file, write_results_file
from .registry import get_league_info
from .standings import generate_standings_file


INPUT_REQUIRED_COLUMNS = {
    "LeagueId",
    "Season",
    "Round",
    "Date",
    "Home",
    "Away",
    "HG",
    "AG",
    "Notes",
}


RESULTS_DIR = Path("data/storico/risultati")
STANDINGS_DIR = Path("data/storico/classifiche_calcolate")


def _int(value: str) -> int:
    value = (value or "").strip()
    return int(value) if value else 0


def _match_key(match: MatchResult) -> tuple:
    return (
        match.season,
        match.round,
        match.date,
        match.home.strip().lower(),
        match.away.strip().lower(),
    )


def read_input_results(path: str | Path) -> dict[str, list[MatchResult]]:
    input_path = Path(path)

    if not input_path.exists():
        raise FileNotFoundError(f"File input risultati non trovato: {input_path}")

    grouped: dict[str, list[MatchResult]] = defaultdict(list)

    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")

        missing = INPUT_REQUIRED_COLUMNS - set(reader.fieldnames or [])

        if missing:
            raise ValueError(
                "File input risultati non valido. Mancano le colonne: "
                + ", ".join(sorted(missing))
            )

        for row in reader:
            league_id = row["LeagueId"].strip()
            league_info = get_league_info(league_id)

            season = _int(row["Season"])

            if season != league_info.season:
                raise ValueError(
                    f"Season incoerente per {league_id}: "
                    f"input={season}, registry={league_info.season}"
                )

            match = MatchResult(
                country=league_info.country,
                league=league_info.league,
                season=season,
                round=_int(row["Round"]),
                date=row["Date"].strip(),
                home=row["Home"].strip(),
                away=row["Away"].strip(),
                home_goals=_int(row["HG"]),
                away_goals=_int(row["AG"]),
                notes=row.get("Notes", "").strip(),
            )

            grouped[league_id].append(match)

    return grouped


def append_results(input_file: str | Path) -> None:
    grouped_matches = read_input_results(input_file)

    total_added = 0
    total_duplicates = 0

    for league_id, new_matches in grouped_matches.items():
        results_file = RESULTS_DIR / f"{league_id}.csv"
        standings_file = STANDINGS_DIR / f"{league_id}.csv"

        if results_file.exists():
            existing_matches = read_results_file(results_file)
        else:
            existing_matches = []

        existing_keys = {_match_key(match) for match in existing_matches}

        added = []
        duplicates = 0

        for match in new_matches:
            key = _match_key(match)

            if key in existing_keys:
                duplicates += 1
                continue

            added.append(match)
            existing_keys.add(key)

        all_matches = existing_matches + added

        all_matches.sort(
            key=lambda m: (
                m.season,
                m.round,
                m.date,
                m.home,
                m.away,
            )
        )

        write_results_file(all_matches, results_file)
        generate_standings_file(results_file, standings_file)

        total_added += len(added)
        total_duplicates += duplicates

        print(f"{league_id}")
        print(f"  Aggiunte: {len(added)}")
        print(f"  Duplicate ignorate: {duplicates}")
        print(f"  Storico: {results_file}")
        print(f"  Classifica: {standings_file}")
        print()

    print("Import completato.")
    print(f"Totale partite aggiunte: {total_added}")
    print(f"Totale duplicate ignorate: {total_duplicates}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Importa nuovi risultati e aggiorna storico/classifica GioOver2.5 v2.0"
    )

    parser.add_argument(
        "input_file",
        help="CSV nuovi risultati in data/input_risultati/"
    )

    args = parser.parse_args()

    append_results(args.input_file)


if __name__ == "__main__":
    main()