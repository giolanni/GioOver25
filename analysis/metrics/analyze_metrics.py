"""
===============================================================================
GioOver2.5 - Analizzatore metriche basato sul Laboratory
===============================================================================

SCOPO
-----
Analizzare le metriche usando come unica fonte dati:

    analysis/laboratory/data/01_matches.csv

Il file contiene già:
- prediction;
- driver ex ante;
- fascia;
- esito reale;
- MatchStatus;
- dati finali;
- informazioni di matching validate dal Laboratory.

FILE LETTO
----------
    analysis/laboratory/data/01_matches.csv

FILE SCRITTI
-------------
    data/debug/metrics/v25/

MODALITÀ D'USO
--------------
    python -m analysis.metrics.analyze_metrics

LIMITAZIONI
-----------
Le righe senza esito OK/KO vengono caricate ma saranno escluse dai report
secondo le regole già applicate dai moduli evaluator/report_writer.
===============================================================================
"""

from argparse import ArgumentParser
from pathlib import Path
from dataclasses import replace

from .config import AnalysisConfig
from .loaders import load_csv_records
from .feature_builder import enrich_records
from .metric_catalog import build_metric_catalog
from .evaluator import evaluate_metrics, build_pair_metrics
from .report_writer import (
    write_population_summary,
    write_metric_catalog,
    write_ranked_reports,
    write_occurrences,
    write_monthly_stability,
    write_skipped_rows,
    write_unmatched_rows,
)


DEFAULT_INPUT = Path(
    "analysis/laboratory/data/01_matches.csv"
)

DEFAULT_OUTPUT = Path(
    "data/debug/metrics/v25"
)


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description=(
            "Analizza pattern ALTA/KO e MEDIA/OK "
            "usando il dataset validato del Laboratory."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Dataset 01_matches.csv prodotto dal Laboratory.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Cartella di output dei report.",
    )

    parser.add_argument(
        "--min-occurrences",
        type=int,
        default=None,
    )

    parser.add_argument(
        "--media-ok-threshold",
        type=float,
        default=None,
    )

    parser.add_argument(
        "--no-pairs",
        action="store_true",
    )

    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = AnalysisConfig()

    if not args.input.exists():
        raise FileNotFoundError(
            "Dataset Laboratory non trovato: "
            f"{args.input}. "
            "Eseguire prima "
            "'python -m analysis.laboratory.run_all'."
        )

    if args.min_occurrences is not None:
        config = replace(
            config,
            min_occurrences_simple=args.min_occurrences,
            min_occurrences_pair=max(
                args.min_occurrences,
                config.min_occurrences_pair,
            ),
        )

    if args.media_ok_threshold is not None:
        config = replace(
            config,
            min_media_ok_precision=(
                args.media_ok_threshold
            ),
        )

    laboratory_rows = load_csv_records(
        args.input
    )

    rows = enrich_records(
        laboratory_rows
    )

    simple_metrics = build_metric_catalog(
        config
    )

    simple_eval, _ = evaluate_metrics(
        rows,
        simple_metrics,
        config,
    )

    all_metrics = list(
        simple_metrics
    )

    all_eval = list(
        simple_eval
    )

    if not args.no_pairs:
        pair_metrics = build_pair_metrics(
            simple_metrics,
            simple_eval,
            config,
        )

        pair_eval, _ = evaluate_metrics(
            rows,
            pair_metrics,
            config,
        )

        all_metrics.extend(
            pair_metrics
        )

        all_eval.extend(
            pair_eval
        )

    args.output.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_population_summary(
        rows,
        config,
        args.output,
    )

    write_metric_catalog(
        all_eval,
        args.output,
    )

    write_ranked_reports(
        all_eval,
        args.output,
        config,
    )

    write_occurrences(
        rows,
        all_metrics,
        config,
        args.output,
    )

    write_monthly_stability(
        rows,
        all_metrics,
        config,
        args.output,
    )

    write_skipped_rows(
        rows,
        config,
        args.output,
    )

    # Il matching è già stato validato dal Laboratory.
    write_unmatched_rows(
        [],
        [],
        args.output,
    )

    completed_rows = [
        row
        for row in rows
        if str(
            row.get("Outcome", "")
        ).strip().upper()
        in {"OK", "KO"}
    ]

    postponed_rows = [
        row
        for row in rows
        if str(
            row.get("MatchStatus", "")
        ).strip().upper()
        == "POSTPONED"
    ]

    print(
        f"Righe Laboratory caricate: "
        f"{len(laboratory_rows)}"
    )

    print(
        f"Righe con esito OK/KO: "
        f"{len(completed_rows)}"
    )

    print(
        f"Righe POSTPONED: "
        f"{len(postponed_rows)}"
    )

    print(
        "Righe non abbinate: 0 "
        "(matching gestito dal Laboratory)"
    )

    print(
        f"Metriche totali valutate: "
        f"{len(all_eval)}"
    )

    print(
        f"Report prodotti in: "
        f"{args.output}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
