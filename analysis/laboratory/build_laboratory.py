"""
===============================================================================
GioOver2.5 - analysis/laboratory/build_laboratory.py
===============================================================================

Costruisce il database del laboratorio.

Le predizioni vengono prese dai ranking giornalieri v25. I risultati reali
vengono recuperati esclusivamente da data/storico/risultati, evitando di usare
lo storico ranking corrente come sorgente delle partite da analizzare.
===============================================================================
"""

from pathlib import Path

from .loaders import load_rankings, load_results
from .merger import merge_matches
from .recent_form_drivers import enrich_matches_with_recent_form
from .writer import write_matches, write_drivers

ROOT = Path(".")
RANKINGS = ROOT / "data/output_ranking/v25"
RESULTS = ROOT / "data/storico/risultati"
OUTPUT = ROOT / "analysis/laboratory/data"


def main():
    print("Loading rankings...")
    rankings = load_rankings(RANKINGS)

    print("Loading results...")
    results = load_results(RESULTS)

    print("Merging predictions with results...")
    matches = merge_matches(rankings, results)

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
