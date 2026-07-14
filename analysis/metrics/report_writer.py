"""
===============================================================================
GioOver2.5 - Scrittura dei report CSV
===============================================================================

SCOPO
-----
Produrre file leggibili e verificabili con:
- riepilogo delle popolazioni;
- catalogo metriche;
- classifiche delle metriche di esclusione e promozione;
- occorrenze per partita;
- stabilità mensile.

FILE SCRITTI
-------------
Nella cartella indicata:
- population_summary.csv
- metric_catalog.csv
- top_alta_ko_patterns.csv
- top_media_ok_patterns.csv
- metric_occurrences.csv
- metric_monthly_stability.csv
- skipped_rows.csv

LOGICA
------
I CSV usano ';' e UTF-8 con BOM per facilitare l'apertura in Excel.

LIMITAZIONI
-----------
L'ordinamento evidenzia candidati statistici, non regole definitive.
===============================================================================
"""

from dataclasses import asdict
from pathlib import Path
import csv
from collections import Counter, defaultdict
from typing import Dict, Any, Iterable, List, Set
from .config import AnalysisConfig
from .models import MetricDefinition, MetricEvaluation
from .evaluator import classify_group


def _write_csv(path: Path, rows: Iterable[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_population_summary(rows, config: AnalysisConfig, output_dir: Path):
    counts = Counter(classify_group(r, config) for r in rows)
    report = [{"Group": k, "Count": counts[k]} for k in
              ("ALTA_OK", "ALTA_KO", "MEDIA_OK", "MEDIA_KO", "OTHER")]
    _write_csv(output_dir / "population_summary.csv", report, ["Group", "Count"])


def write_metric_catalog(evaluations: List[MetricEvaluation], output_dir: Path):
    rows = [asdict(e) for e in evaluations]
    if not rows:
        return
    _write_csv(output_dir / "metric_catalog.csv", rows, list(rows[0].keys()))


def write_ranked_reports(
    evaluations: List[MetricEvaluation],
    output_dir: Path,
    config: AnalysisConfig,
):
    exclusion = [
        e for e in evaluations
        if e.occurrences >= config.min_occurrences_simple
        and e.alta_ko_capture >= config.min_alta_ko_capture
    ]
    exclusion.sort(
        key=lambda e: (e.alta_ko_lift, e.exclusion_efficiency, e.alta_ko_capture, e.occurrences),
        reverse=True,
    )

    promotion = [
        e for e in evaluations
        if e.occurrences >= config.min_occurrences_simple
        and e.media_ok + e.media_ko >= config.min_occurrences_simple
        and e.media_ok_precision >= config.min_media_ok_precision
    ]
    promotion.sort(
        key=lambda e: (e.media_ok_precision, e.media_ok_lift, e.media_ok_capture, e.occurrences),
        reverse=True,
    )

    fields = list(asdict(evaluations[0]).keys()) if evaluations else []
    if fields:
        _write_csv(output_dir / "top_alta_ko_patterns.csv",
                   [asdict(e) for e in exclusion], fields)
        _write_csv(output_dir / "top_media_ok_patterns.csv",
                   [asdict(e) for e in promotion], fields)


def write_occurrences(
    rows: List[Dict[str, Any]],
    metric_defs: List[MetricDefinition],
    config: AnalysisConfig,
    output_dir: Path,
):
    output_rows = []
    for idx, row in enumerate(rows):
        matched = []
        for metric in metric_defs:
            try:
                if metric.predicate(row):
                    matched.append(metric.name)
            except (TypeError, ValueError, KeyError):
                pass
        if not matched:
            continue
        output_rows.append({
            "RowId": idx,
            "Group": classify_group(row, config),
            "LeagueId": row.get("LeagueId", ""),
            "MatchDate": row.get("MatchDate", ""),
            "PredictionDate": row.get("PredictionDate", ""),
            "Home": row.get("Home", ""),
            "Away": row.get("Away", ""),
            "Band": row.get("Band", ""),
            "Outcome": row.get("Outcome", ""),
            "Score": row.get("Score", ""),
            "MatchMode": row.get("MatchMode", ""),
            "MatchedMetrics": "|".join(matched),
            "SourceFile": row.get("SourceFile", ""),
        })
    _write_csv(
        output_dir / "metric_occurrences.csv",
        output_rows,
        ["RowId", "Group", "LeagueId", "MatchDate", "PredictionDate", "Home", "Away",
         "Band", "Outcome", "Score", "MatchMode", "MatchedMetrics", "SourceFile"],
    )


def write_monthly_stability(
    rows: List[Dict[str, Any]],
    metric_defs: List[MetricDefinition],
    config: AnalysisConfig,
    output_dir: Path,
):
    stats = defaultdict(Counter)
    for row in rows:
        month = row.get("AnalysisMonth") or "UNKNOWN"
        group = classify_group(row, config)
        for metric in metric_defs:
            try:
                if metric.predicate(row):
                    stats[(metric.name, month)][group] += 1
            except (TypeError, ValueError, KeyError):
                pass

    report = []
    for (name, month), c in sorted(stats.items()):
        alta_total = c["ALTA_OK"] + c["ALTA_KO"]
        media_total = c["MEDIA_OK"] + c["MEDIA_KO"]
        report.append({
            "Metric": name,
            "Month": month,
            "AltaOK": c["ALTA_OK"],
            "AltaKO": c["ALTA_KO"],
            "AltaKOShare": c["ALTA_KO"] / alta_total if alta_total else 0.0,
            "MediaOK": c["MEDIA_OK"],
            "MediaKO": c["MEDIA_KO"],
            "MediaOKPrecision": c["MEDIA_OK"] / media_total if media_total else 0.0,
            "Occurrences": sum(c.values()),
        })
    _write_csv(
        output_dir / "metric_monthly_stability.csv",
        report,
        ["Metric", "Month", "AltaOK", "AltaKO", "AltaKOShare",
         "MediaOK", "MediaKO", "MediaOKPrecision", "Occurrences"],
    )


def write_skipped_rows(rows, config: AnalysisConfig, output_dir: Path):
    skipped = []
    for idx, row in enumerate(rows):
        if classify_group(row, config) == "OTHER":
            skipped.append({
                "RowId": idx,
                "LeagueId": row.get("LeagueId", ""),
                "MatchDate": row.get("MatchDate", ""),
                "Home": row.get("Home", ""),
                "Away": row.get("Away", ""),
                "Band": row.get("Band", ""),
                "Outcome": row.get("Outcome", ""),
                "Reason": "Band o Outcome non riconosciuti/mancanti",
                "SourceFile": row.get("SourceFile", ""),
            })
    _write_csv(
        output_dir / "skipped_rows.csv",
        skipped,
        ["RowId", "LeagueId", "MatchDate", "Home", "Away",
         "Band", "Outcome", "Reason", "SourceFile"],
    )


def write_unmatched_rows(
    unmatched_history,
    unmatched_rankings,
    output_dir: Path,
):
    history_rows = []
    for idx, row in enumerate(unmatched_history):
        history_rows.append({
            "RowId": idx,
            "LeagueId": row.get("LeagueId", ""),
            "MatchDate": row.get("MatchDate", ""),
            "Home": row.get("Home", ""),
            "Away": row.get("Away", ""),
            "Band": row.get("Band", ""),
            "Outcome": row.get("Outcome", ""),
            "SourceFile": row.get("SourceFile", ""),
            "Reason": "Nessun ranking originale trovato con la chiave esatta",
        })

    ranking_rows = []
    for idx, row in enumerate(unmatched_rankings):
        ranking_rows.append({
            "RowId": idx,
            "LeagueId": row.get("LeagueId", ""),
            "MatchDate": row.get("MatchDate", ""),
            "Home": row.get("Home", ""),
            "Away": row.get("Away", ""),
            "Band": row.get("Band", ""),
            "SourceFile": row.get("SourceFile", ""),
            "Reason": "Ranking originale senza riga corrispondente nello storico",
        })

    _write_csv(
        output_dir / "unmatched_history.csv",
        history_rows,
        ["RowId", "LeagueId", "MatchDate", "Home", "Away", "Band",
         "Outcome", "SourceFile", "Reason"],
    )
    _write_csv(
        output_dir / "unmatched_rankings.csv",
        ranking_rows,
        ["RowId", "LeagueId", "MatchDate", "Home", "Away", "Band",
         "SourceFile", "Reason"],
    )
