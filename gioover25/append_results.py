import argparse
import csv
from collections import defaultdict
from pathlib import Path

from .history import MatchResult, read_results_file, write_results_file
from .registry import get_league_info
from .standings import generate_standings_file
from .ranking_history import update_finished_matches
from gioover25.league_over_map import rebuild_league_over_map
from gioover25.engines.factory import get_available_engines


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
        match.home.strip().lower(),
        match.away.strip().lower(),
    )

def _team_played_count(matches: list[MatchResult], team: str) -> int:
    team_key = team.strip().lower()

    return sum(
        1
        for match in matches
        if match.home.strip().lower() == team_key
        or match.away.strip().lower() == team_key
    )


def _resolve_round(row: dict, existing_matches: list[MatchResult]) -> int:
    raw_round = str(row.get("Round", "")).strip()

    if raw_round and raw_round != "?":
        return int(raw_round)

    home = row["Home"].strip()
    away = row["Away"].strip()

    home_last_round = max(
        [m.round for m in existing_matches if m.home == home or m.away == home],
        default=0,
    )

    away_last_round = max(
        [m.round for m in existing_matches if m.home == away or m.away == away],
        default=0,
    )

    return max(home_last_round, away_last_round) + 1


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
                round=0 if row["Round"].strip() in {"", "?"} else _int(row["Round"]),
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
            if match.round == 0:
                fake_row = {
                    "Round": "?",
                    "Home": match.home,
                    "Away": match.away,
                }

                resolved_round = _resolve_round(fake_row, existing_matches + added)
                match.round = resolved_round

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
        
        league_info = get_league_info(league_id)
        notes = str(league_info.notes or "").upper()

        if "UNBALANCED" in notes:
            print(f"Classifica saltata per lega irregolare: {league_id}")
        else:
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
    notes = str(league_info.notes or "").upper()

    generate_standings_file(results_file, standings_file)

    for engine_name in get_available_engines():
        update_finished_matches(engine_name)

    rebuild_league_over_map()


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