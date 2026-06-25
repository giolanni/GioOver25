import csv
from pathlib import Path

from .ranking_history import append_predictions

RANKINGS_DIR = Path("data/output_ranking")


def import_all_rankings() -> None:

    files = sorted(RANKINGS_DIR.glob("*.csv"))

    if not files:
        print("Nessun ranking trovato.")
        return

    total = 0

    for file in files:

        print(f"Importo {file.name}")

        with open(file, newline="", encoding="utf-8-sig") as f:

            reader = csv.DictReader(f, delimiter=";")

            rows = list(reader)

        append_predictions(rows)

        total += len(rows)

    print()
    print(f"File elaborati: {len(files)}")
    print(f"Partite lette: {total}")


def main():
    import_all_rankings()


if __name__ == "__main__":
    main()