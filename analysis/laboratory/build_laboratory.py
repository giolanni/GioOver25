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

from argparse import ArgumentParser
from pathlib import Path

from .loaders import load_csv, load_rankings, load_results
from .merger import merge_matches
from .recent_form_drivers import (
    RECENT_FORM_DRIVERS,
    enrich_matches_with_recent_form,
)
from .writer import write_matches, write_drivers

ROOT = Path(".")
RANKINGS = ROOT / "data/output_ranking/v25"
RESULTS = ROOT / "data/storico/risultati"
OUTPUT = ROOT / "analysis/laboratory/data"
MATCHES_FILE = OUTPUT / "01_matches.csv"

PREDICTION_IDENTITY_FIELDS = (
    "PredictionDate",
    "MatchDate",
    "LeagueId",
    "Round",
    "Home",
    "Away",
    "Score",
    "Band",
    "AlgorithmVersion",
)


def _text(value) -> str:
    return str(value or "").strip()


def _prediction_key(row: dict) -> tuple[str, ...]:
    """Identità già usata dal loader per deduplicare le predizioni."""
    return tuple(
        _text(row.get(field))
        for field in PREDICTION_IDENTITY_FIELDS
    )


def enrich_incrementally(
    matches: list[dict],
    existing_rows: list[dict],
) -> tuple[list[dict], int, int]:
    """Riusa i driver ex ante esistenti e calcola soltanto le nuove righe.

    Esito e campi del matching provengono sempre dal merge appena eseguito:
    quindi una partita passata da SCHEDULED a FINAL viene aggiornata senza
    ricalcolare driver che, per definizione, descrivono il momento precedente
    alla partita.
    """
    existing_by_key = {
        _prediction_key(row): row
        for row in existing_rows
    }
    reused: dict[int, dict] = {}
    new_matches: list[dict] = []

    for index, match in enumerate(matches):
        existing = existing_by_key.get(
            _prediction_key(match)
        )
        if existing is None:
            new_matches.append(match)
            continue

        row = dict(match)
        for driver in RECENT_FORM_DRIVERS:
            if driver in existing:
                row[driver] = existing.get(driver, "")
        reused[index] = row

    enriched_new = iter(
        enrich_matches_with_recent_form(new_matches)
        if new_matches
        else []
    )
    enriched = []
    for index in range(len(matches)):
        enriched.append(
            reused[index]
            if index in reused
            else next(enriched_new)
        )

    return enriched, len(reused), len(new_matches)


def write_laboratory_outputs(
    matches: list[dict],
    *,
    incremental: bool,
) -> None:
    """Scrive solo gli output necessari alla modalità richiesta.

    ``02_drivers.csv`` è un dataset lungo usato esclusivamente dalle analisi
    complete (distribuzioni e regole candidate). Riscriverlo durante ogni
    import incrementale genera centinaia di migliaia di righe inutili.
    """
    OUTPUT.mkdir(parents=True, exist_ok=True)

    print("Writing 01_matches.csv...")
    write_matches(matches, MATCHES_FILE)

    if incremental:
        print(
            "Skipping 02_drivers.csv "
            "(verrà rigenerato con --full-analysis)."
        )
        return

    print("Writing 02_drivers.csv...")
    write_drivers(matches, OUTPUT / "02_drivers.csv")


def main(incremental: bool = False):
    print("Loading rankings...")
    rankings = load_rankings(RANKINGS)

    print("Loading results...")
    results = load_results(RESULTS)

    print("Merging predictions with results...")
    matches = merge_matches(rankings, results)

    if incremental and MATCHES_FILE.exists():
        print("Updating recent-form drivers incrementally...")
        existing_rows = load_csv(MATCHES_FILE)
        matches, reused_count, new_count = enrich_incrementally(
            matches,
            existing_rows,
        )
        print(f"Driver riusati : {reused_count}")
        print(f"Driver calcolati: {new_count}")
    else:
        print("Calculating recent-form candidate drivers...")
        matches = enrich_matches_with_recent_form(matches)

    write_laboratory_outputs(
        matches,
        incremental=incremental,
    )
    print()
    print("Done")
    print(f"Predictions : {len(matches)}")


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Costruisce o aggiorna il dataset del Laboratory."
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help=(
            "Riusa i driver delle predizioni già presenti e calcola "
            "soltanto quelli delle nuove predizioni."
        ),
    )
    args = parser.parse_args()
    main(incremental=args.incremental)
