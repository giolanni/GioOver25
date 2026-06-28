import argparse

from .engines.factory import get_available_engines
from .ranking_history import update_finished_matches


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggiorna gli esiti reali nello storico ranking."
    )

    parser.add_argument(
        "--engine",
        default="all",
        choices=get_available_engines() + ["all"],
        help="Motore da aggiornare"
    )

    args = parser.parse_args()

    if args.engine == "all":
        for engine_name in get_available_engines():
            update_finished_matches(engine_name)
    else:
        update_finished_matches(args.engine)


if __name__ == "__main__":
    main()