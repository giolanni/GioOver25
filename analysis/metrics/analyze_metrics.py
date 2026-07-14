"""
===============================================================================
GioOver2.5 - Analizzatore principale delle metriche con doppia fonte
===============================================================================

SCOPO
-----
Eseguire l'analisi utilizzando:
- storico ranking v25 per fascia ed esito reale;
- ranking originali v25 per statistiche ex ante.

FILE LETTI
----------
Default storico:
    data/storico/ranking/v25/storico_ranking_v25.csv

Default ranking:
    data/output_ranking/v25/

MATCHING
--------
Se MatchDate è presente: LeagueId + MatchDate + Home + Away.
Altrimenti: LeagueId + PredictionDate + Home + Away.

FILE SCRITTI
-------------
Default:
    data/debug/metrics/v25/

Oltre ai report statistici vengono prodotti:
- unmatched_history.csv
- unmatched_rankings.csv

MODALITÀ D'USO
--------------
    python -m analysis.metrics.analyze_metrics

Oppure:

    python -m analysis.metrics.analyze_metrics ^
      --history data/storico/ranking/v25/storico_ranking_v25.csv ^
      --rankings data/output_ranking/v25 ^
      --output data/debug/metrics/v25

LIMITAZIONI
-----------
Le righe storiche prive di MatchDate non possono essere abbinate con la nuova
chiave. Restano visibili in unmatched_history.csv.
===============================================================================
"""

from argparse import ArgumentParser
from pathlib import Path
from dataclasses import replace

from .config import AnalysisConfig
from .loaders import load_csv_records, merge_history_with_rankings
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


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Analizza pattern ALTA/KO e MEDIA/OK.")
    parser.add_argument(
        "--history",
        type=Path,
        default=Path("data/storico/ranking/v25/storico_ranking_v25.csv"),
        help="Storico ranking con Band e Over25=OK/KO.",
    )
    parser.add_argument(
        "--rankings",
        type=Path,
        default=Path("data/output_ranking/v25"),
        help="File o cartella dei ranking originali con dati ex ante.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/debug/metrics/v25"),
        help="Cartella di output dei report.",
    )
    parser.add_argument("--min-occurrences", type=int, default=None)
    parser.add_argument("--media-ok-threshold", type=float, default=None)
    parser.add_argument("--no-pairs", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = AnalysisConfig()

    if args.min_occurrences is not None:
        config = replace(
            config,
            min_occurrences_simple=args.min_occurrences,
            min_occurrences_pair=max(args.min_occurrences, config.min_occurrences_pair),
        )
    if args.media_ok_threshold is not None:
        config = replace(config, min_media_ok_precision=args.media_ok_threshold)

    history_rows = load_csv_records(args.history)
    ranking_rows = load_csv_records(args.rankings)

    merged_rows, unmatched_history, unmatched_rankings = merge_history_with_rankings(
        history_rows,
        ranking_rows,
    )
    rows = enrich_records(merged_rows)

    simple_metrics = build_metric_catalog(config)
    simple_eval, _ = evaluate_metrics(rows, simple_metrics, config)

    all_metrics = list(simple_metrics)
    all_eval = list(simple_eval)

    if not args.no_pairs:
        pair_metrics = build_pair_metrics(simple_metrics, simple_eval, config)
        pair_eval, _ = evaluate_metrics(rows, pair_metrics, config)
        all_metrics.extend(pair_metrics)
        all_eval.extend(pair_eval)

    args.output.mkdir(parents=True, exist_ok=True)
    write_population_summary(rows, config, args.output)
    write_metric_catalog(all_eval, args.output)
    write_ranked_reports(all_eval, args.output, config)
    write_occurrences(rows, all_metrics, config, args.output)
    write_monthly_stability(rows, all_metrics, config, args.output)
    write_skipped_rows(rows, config, args.output)
    write_unmatched_rows(unmatched_history, unmatched_rankings, args.output)

    print(f"Righe storico caricate: {len(history_rows)}")
    print(f"Righe ranking caricate: {len(ranking_rows)}")
    print(f"Righe abbinate: {len(rows)}")
    print(f"Storico non abbinato: {len(unmatched_history)}")
    print(f"Ranking non abbinati: {len(unmatched_rankings)}")
    print(f"Metriche totali valutate: {len(all_eval)}")
    print(f"Report prodotti in: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
