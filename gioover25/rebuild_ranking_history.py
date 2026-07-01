import argparse
import csv
from pathlib import Path

from .engines.factory import get_available_engines
from .ranking_history import append_predictions, update_finished_matches


OUTPUT_RANKING_DIR = Path("data/output_ranking")
STORICO_RANKING_DIR = Path("data/storico/ranking")


def clear_history(engine_name: str) -> None:
    history_file = STORICO_RANKING_DIR / engine_name / "storico_ranking_{engine_name}.csv"

    if history_file.exists():
        history_file.unlink()
        print(f"[{engine_name}] Storico cancellato: {history_file}")
    else:
        print(f"[{engine_name}] Nessuno storico da cancellare.")


def import_rankings_for_engine(engine_name: str) -> None:
    ranking_dir = OUTPUT_RANKING_DIR / engine_name

    if not ranking_dir.exists():
        print(f"[{engine_name}] Cartella ranking non trovata: {ranking_dir}")
        return

    files = sorted(ranking_dir.glob("*.csv"))

    if not files:
        print(f"[{engine_name}] Nessun file ranking trovato.")
        return

    for file in files:
        print(f"[{engine_name}] Importo {file.name}")

        with open(file, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            rows = list(reader)

        append_predictions(
            rows,
            engine_name=engine_name,
            algorithm_version=engine_name
        )


def rebuild_engine(engine_name: str) -> None:
    clear_history(engine_name)
    import_rankings_for_engine(engine_name)
    update_finished_matches(engine_name)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ricostruisce lo storico ranking dagli output ranking salvati."
    )

    parser.add_argument(
        "--engine",
        default="all",
        choices=get_available_engines() + ["all"],
        help="Motore da ricostruire"
    )

    args = parser.parse_args()

    if args.engine == "all":
        for engine_name in get_available_engines():
            rebuild_engine(engine_name)
    else:
        rebuild_engine(args.engine)


if __name__ == "__main__":
    main()