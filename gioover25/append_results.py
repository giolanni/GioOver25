import argparse
import csv
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from .history import MatchResult, read_results_file, write_results_file
from .registry import get_league_info
from .standings import generate_current_standings_file
from .ranking_history import update_finished_matches
from gioover25.league_over_map import rebuild_league_over_map
from gioover25.engines.factory import get_available_engines


INPUT_REQUIRED_COLUMNS = {
    "LeagueId",
    "Season",
    "Round",
    "MatchDate",
    "Home",
    "Away",
    "HG",
    "AG",
}

RESULTS_DIR = Path("data/storico/risultati")
STANDINGS_DIR = Path("data/storico/classifiche_calcolate")

INPUT_RESULTS_ARCHIVE_DIR = Path(
    "data/input_risultati/storico"
)

POSTPONED_FILE = Path(
    "data/storico/partite_posticipate.csv"
)

POSTPONED_FIELDNAMES = [
    "LeagueId",
    "Season",
    "Round",
    "MatchDate",
    "Home",
    "Away",
    "Status",
    "Notes",
]

POSTPONED_STATUSES = {
    "RINVIATA",
    "POSTICIPATA",
}


def _int(value: str) -> int:
    raw = str(value or "").strip()
    return int(raw) if raw else 0


def _optional_int(value: str) -> int | None:
    raw = str(value or "").strip()

    if raw == "":
        return None

    return int(raw)


def _normalize(value: str) -> str:
    return " ".join(
        str(value or "").strip().lower().split()
    )


def _match_key(match: MatchResult) -> tuple[str, str, str]:
    return (
        str(match.date).strip(),
        _normalize(match.home),
        _normalize(match.away),
    )


def _postponed_key(
    league_id: str,
    home: str,
    away: str,
) -> tuple[str, str, str]:
    return (
        league_id.strip(),
        _normalize(home),
        _normalize(away),
    )


def _resolve_round(
    row: dict,
    existing_matches: list[MatchResult],
) -> int:
    raw_round = str(row.get("Round", "")).strip()

    if raw_round and raw_round != "?":
        return int(raw_round)

    home = _normalize(row.get("Home", ""))
    away = _normalize(row.get("Away", ""))

    home_last_round = max(
        [
            match.round
            for match in existing_matches
            if (
                _normalize(match.home) == home
                or _normalize(match.away) == home
            )
        ],
        default=0,
    )

    away_last_round = max(
        [
            match.round
            for match in existing_matches
            if (
                _normalize(match.home) == away
                or _normalize(match.away) == away
            )
        ],
        default=0,
    )

    return max(
        home_last_round,
        away_last_round,
    ) + 1


def _parse_round(value) -> int:
    raw = str(value or "").strip()

    if raw == "" or raw == "?":
        return 0

    # Evita che una data compatta venga interpretata come round.
    if (
        raw.isdigit()
        and len(raw) == 8
        and raw.startswith("20")
    ):
        return 0

    return int(raw)


def _read_postponed() -> list[dict]:
    if not POSTPONED_FILE.exists():
        return []

    with POSTPONED_FILE.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        return list(
            csv.DictReader(
                f,
                delimiter=";",
            )
        )


def _write_postponed(rows: list[dict]) -> None:
    POSTPONED_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with POSTPONED_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=POSTPONED_FIELDNAMES,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def _register_postponed(
    postponed_rows: list[dict],
    row: dict,
) -> bool:
    key = _postponed_key(
        row["LeagueId"],
        row["Home"],
        row["Away"],
    )

    for existing in postponed_rows:
        existing_key = _postponed_key(
            existing.get("LeagueId", ""),
            existing.get("Home", ""),
            existing.get("Away", ""),
        )

        if existing_key == key:
            existing["Season"] = row.get("Season", "")
            existing["Round"] = row.get("Round", "")
            existing["MatchDate"] = row.get(
                "MatchDate",
                "",
            )
            existing["Status"] = row.get(
                "Status",
                "RINVIATA",
            )
            existing["Notes"] = row.get(
                "Notes",
                "",
            )
            return False

    postponed_rows.append(
        {
            "LeagueId": row.get("LeagueId", ""),
            "Season": row.get("Season", ""),
            "Round": row.get("Round", ""),
            "MatchDate": row.get("MatchDate", ""),
            "Home": row.get("Home", ""),
            "Away": row.get("Away", ""),
            "Status": row.get(
                "Status",
                "RINVIATA",
            ),
            "Notes": row.get("Notes", ""),
        }
    )

    return True


def _remove_postponed_if_present(
    postponed_rows: list[dict],
    league_id: str,
    home: str,
    away: str,
) -> bool:
    target_key = _postponed_key(
        league_id,
        home,
        away,
    )

    for index, existing in enumerate(postponed_rows):
        existing_key = _postponed_key(
            existing.get("LeagueId", ""),
            existing.get("Home", ""),
            existing.get("Away", ""),
        )

        if existing_key == target_key:
            postponed_rows.pop(index)
            return True

    return False


def archive_input_results(
    input_file: str | Path,
) -> Path:
    source = Path(input_file)

    if not source.exists():
        raise FileNotFoundError(
            "File risultati da archiviare non trovato: "
            f"{source}"
        )

    INPUT_RESULTS_ARCHIVE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    now = datetime.now()

    date_part = now.strftime("%Y%m%d")
    timestamp_part = now.strftime("%H%M%S%f")[:8]

    archive_file = (
        INPUT_RESULTS_ARCHIVE_DIR
        / f"risultati_{date_part}_{timestamp_part}.csv"
    )

    counter = 1

    while archive_file.exists():
        archive_file = (
            INPUT_RESULTS_ARCHIVE_DIR
            / (
                f"risultati_{date_part}_"
                f"{timestamp_part}_{counter}.csv"
            )
        )
        counter += 1

    shutil.copy2(
        source,
        archive_file,
    )

    return archive_file


def read_input_results(
    path: str | Path,
) -> tuple[
    dict[str, list[MatchResult]],
    list[dict],
    int,
]:
    input_path = Path(path)

    if not input_path.exists():
        raise FileNotFoundError(
            f"File input risultati non trovato: {input_path}"
        )

    grouped: dict[str, list[MatchResult]] = defaultdict(list)
    postponed_rows = _read_postponed()

    postponed_registered = 0

    with input_path.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        reader = csv.DictReader(
            f,
            delimiter=";",
        )

        missing = (
            INPUT_REQUIRED_COLUMNS
            - set(reader.fieldnames or [])
        )

        if missing:
            raise ValueError(
                "File input risultati non valido. "
                "Mancano le colonne: "
                + ", ".join(sorted(missing))
            )

        for row in reader:
            league_id = row["LeagueId"].strip()
            league_info = get_league_info(league_id)

            season = _int(row["Season"])

            if season != league_info.season:
                raise ValueError(
                    f"Season incoerente per {league_id}: "
                    f"input={season}, "
                    f"registry={league_info.season}"
                )

            status = str(
                row.get("Status", "")
            ).strip().upper()

            hg = _optional_int(row.get("HG", ""))
            ag = _optional_int(row.get("AG", ""))

            if status == "" and hg is not None and ag is not None:
                status = "FINALE"

            if status in POSTPONED_STATUSES:
                row["Status"] = status

                inserted = _register_postponed(
                    postponed_rows,
                    row,
                )

                if inserted:
                    postponed_registered += 1

                continue

            if status != "FINALE":
                raise ValueError(
                    f"Status non valido per "
                    f"{league_id} | "
                    f"{row['Home']} - {row['Away']}: "
                    f"{status or '<vuoto>'}"
                )

            if hg is None or ag is None:
                raise ValueError(
                    f"Risultato mancante per "
                    f"{league_id} | "
                    f"{row['Home']} - {row['Away']}"
                )

            _remove_postponed_if_present(
                postponed_rows,
                league_id,
                row["Home"],
                row["Away"],
            )

            match = MatchResult(
                country=league_info.country,
                league=league_info.league,
                season=season,
                round=_parse_round(
                    row.get("Round")
                ),
                date=row["MatchDate"].strip(),
                home=row["Home"].strip(),
                away=row["Away"].strip(),
                home_goals=hg,
                away_goals=ag,
                notes=row.get(
                    "Notes",
                    "",
                ).strip(),
            )

            grouped[league_id].append(match)

    return (
        grouped,
        postponed_rows,
        postponed_registered,
    )


def append_results(
    input_file: str | Path,
) -> None:
    (
        grouped_matches,
        postponed_rows,
        postponed_registered,
    ) = read_input_results(input_file)

    total_added = 0
    total_duplicates = 0

    for league_id, new_matches in grouped_matches.items():
        results_file = (
            RESULTS_DIR
            / f"{league_id}.csv"
        )

        standings_file = (
            STANDINGS_DIR
            / f"{league_id}.csv"
        )

        if results_file.exists():
            existing_matches = read_results_file(
                results_file
            )
        else:
            existing_matches = []

        existing_keys = {
            _match_key(match)
            for match in existing_matches
        }

        added = []
        duplicates = 0

        for match in new_matches:
            if match.round == 0:
                fake_row = {
                    "Round": "?",
                    "Home": match.home,
                    "Away": match.away,
                }

                match.round = _resolve_round(
                    fake_row,
                    existing_matches + added,
                )

            key = _match_key(match)

            if key in existing_keys:
                duplicates += 1
                continue

            added.append(match)
            existing_keys.add(key)

        all_matches = existing_matches + added

        all_matches.sort(
            key=lambda match: (
                match.season,
                match.round,
                match.date,
                match.home,
                match.away,
            )
        )

        write_results_file(
            all_matches,
            results_file,
        )

        generate_current_standings_file(
            results_file,
            standings_file,
        )

        total_added += len(added)
        total_duplicates += duplicates

        print(league_id)
        print(f"  Aggiunte: {len(added)}")
        print(
            f"  Duplicate ignorate: {duplicates}"
        )
        print(f"  Storico: {results_file}")
        print(f"  Classifica: {standings_file}")
        print()

    _write_postponed(postponed_rows)

    print("Import completato.")
    print(
        f"Totale partite aggiunte: {total_added}"
    )
    print(
        "Totale duplicate ignorate: "
        f"{total_duplicates}"
    )
    print(
        "Nuove partite rinviate registrate: "
        f"{postponed_registered}"
    )

    for engine_name in get_available_engines():
        update_finished_matches(engine_name)

    rebuild_league_over_map()

    archive_file = archive_input_results(
        input_file
    )

    print(
        "File input risultati archiviato: "
        f"{archive_file}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Importa nuovi risultati e aggiorna "
            "storico/classifica GioOver2.5"
        )
    )

    parser.add_argument(
        "input_file",
        help=(
            "CSV nuovi risultati, normalmente "
            "data/input_risultati/risultati.csv"
        ),
    )

    args = parser.parse_args()

    append_results(args.input_file)


if __name__ == "__main__":
    main()