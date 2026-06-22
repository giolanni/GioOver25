import argparse
import csv
from datetime import date
from pathlib import Path


def append_to_storico(
    classifica_file: str,
    storico_file: str,
    data_partite: str | None = None
) -> None:
    data_value = data_partite or date.today().isoformat()

    classifica_path = Path(classifica_file)
    storico_path = Path(storico_file)

    storico_path.parent.mkdir(parents=True, exist_ok=True)

    with open(classifica_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)

    if not rows:
        print("Nessuna riga trovata nella classifica.")
        return

    progressivo = 1

    if storico_path.exists():
        with open(storico_path, newline="", encoding="utf-8-sig") as sf:
            storico_reader = csv.DictReader(sf, delimiter=";")
            for riga in storico_reader:
                if riga.get("data") == data_value:
                    progressivo += 1

    output_rows = []

    for row in rows:
        new_row = {
            "id": f"{data_value.replace('-', '')}_{progressivo:03d}",
            "data": data_value,
            **row
        }

        progressivo += 1
        output_rows.append(new_row)

    fieldnames = [
    "id",
    "data",
    "model_version",

    "country",
    "league",

    "home",
    "away",
    "match",

    "risultato",
    "ESITO",

    "score",
    "band",

    "ranking_component",
    "strong_gf_component",
    "weak_ga_component",
    "strong_ga_component",
    "weak_gf_component",
    "last10_component",
    "real_over_index_component",
    "random_component",

    "reason",
]
    file_exists = storico_path.exists()

    with open(storico_path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")

        if not file_exists:
            writer.writeheader()

        writer.writerows(output_rows)

    print(f"Aggiunte {len(output_rows)} partite allo storico:")
    print(storico_path.resolve())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggiunge una classifica GioOver2.5 allo storico."
    )

    parser.add_argument(
        "classifica_file",
        help="File CSV classifica giornaliera"
    )

    parser.add_argument(
        "--storico",
        default="data/storico/storico_risultati.csv",
        help="File CSV storico cumulativo"
    )

    parser.add_argument(
        "--data",
        default=None,
        help="Data partite in formato YYYY-MM-DD. Se omessa usa la data odierna."
    )

    args = parser.parse_args()

    append_to_storico(
        classifica_file=args.classifica_file,
        storico_file=args.storico,
        data_partite=args.data
    )


if __name__ == "__main__":
    main()