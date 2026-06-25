import csv
from pathlib import Path

from .standings import generate_standings_file


QUEUE_FILE = Path("data/update_queue.csv")
RESULTS_DIR = Path("data/storico/risultati")
STANDINGS_DIR = Path("data/storico/classifiche_calcolate")


def read_queue() -> list[dict]:
    if not QUEUE_FILE.exists():
        raise FileNotFoundError(f"File update queue non trovato: {QUEUE_FILE}")

    with open(QUEUE_FILE, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def write_queue(rows: list[dict]) -> None:
    with open(QUEUE_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["LeagueId", "NeedsStandingsUpdate"],
            delimiter=";"
        )
        writer.writeheader()
        writer.writerows(rows)


def update_standings_from_queue() -> None:
    rows = read_queue()
    STANDINGS_DIR.mkdir(parents=True, exist_ok=True)

    updated = 0
    skipped = 0
    missing = 0

    for row in rows:
        league_id = row["LeagueId"].strip()
        needs_update = row["NeedsStandingsUpdate"].strip() == "1"

        if not needs_update:
            skipped += 1
            continue

        results_file = RESULTS_DIR / f"{league_id}.csv"
        standings_file = STANDINGS_DIR / f"{league_id}.csv"

        if not results_file.exists():
            print(f"MANCANTE: {results_file}")
            missing += 1
            continue

        generate_standings_file(results_file, standings_file)

        row["NeedsStandingsUpdate"] = "0"
        updated += 1

        print(f"AGGIORNATA: {league_id}")

    write_queue(rows)

    print()
    print(f"Classifiche aggiornate: {updated}")
    print(f"Classifiche saltate: {skipped}")
    print(f"File risultati mancanti: {missing}")


def main() -> None:
    update_standings_from_queue()


if __name__ == "__main__":
    main()