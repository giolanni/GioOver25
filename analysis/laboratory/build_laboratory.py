"""
===============================================================================
GioOver2.5 - analysis/laboratory/build_laboratory.py
===============================================================================

Costruisce il database del laboratorio.

Output:

analysis/laboratory/data/

    01_matches.csv
    02_drivers.csv
"""

from pathlib import Path

from .loaders import (
    load_history,
    load_rankings,
)

from .merger import merge_matches
from .recent_form_drivers import enrich_matches_with_recent_form
from .writer import (
    write_matches,
    write_drivers,
)


ROOT = Path(".")

HISTORY = ROOT / "data/storico/ranking/v25/storico_ranking_v25.csv"

RANKINGS = ROOT / "data/output_ranking/v25"

OUTPUT = ROOT / "analysis/laboratory/data"


def main():

    print("Loading history...")
    history = load_history(HISTORY)

    print("Loading rankings...")
    rankings = load_rankings(RANKINGS)

    print("Merging...")
    matches = merge_matches(history, rankings)

    print("Calculating recent-form candidate drivers...")
    matches = enrich_matches_with_recent_form(matches)

    OUTPUT.mkdir(parents=True, exist_ok=True)

    print("Writing 01_matches.csv...")
    write_matches(matches, OUTPUT / "01_matches.csv")

    print("Writing 02_drivers.csv...")
    write_drivers(matches, OUTPUT / "02_drivers.csv")

    print()

    print("Done")

    print(f"Predictions : {len(matches)}")


if __name__ == "__main__":
    main()