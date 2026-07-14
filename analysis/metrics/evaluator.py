"""
===============================================================================
GioOver2.5 - Valutazione statistica delle metriche
===============================================================================

SCOPO
-----
Valutare ogni metrica sulle quattro popolazioni:
ALTA+OK, ALTA+KO, MEDIA+OK, MEDIA+KO.

FILE LETTI / SCRITTI
--------------------
Nessuno direttamente.

INDICATORI
----------
- occurrences: numero di partite che soddisfano la metrica;
- over_precision: OK / (OK + KO);
- coverage: quota dello storico analizzato coperta;
- alta_ko_capture: quota di tutti gli ALTA KO intercettata;
- media_ok_precision: MEDIA OK / (MEDIA OK + MEDIA KO);
- lift: rapporto rispetto al tasso base della popolazione;
- exclusion_efficiency: ALTA KO / (ALTA KO + ALTA OK);
- promotion_efficiency: MEDIA OK / (MEDIA OK + MEDIA KO).

INTERPRETAZIONE
---------------
Una metrica di esclusione dovrebbe intercettare molti ALTA KO e pochi ALTA OK.
Una metrica di promozione dovrebbe avere precisione MEDIA superiore alla base,
supporto sufficiente e possibilmente stabilità nel tempo.

LIMITAZIONI
-----------
Il framework misura associazioni storiche, non causalità. Le metriche candidate
devono essere validate su periodi non usati per scoprirle.
===============================================================================
"""

from collections import Counter
from typing import Dict, Any, Iterable, List, Tuple
from .config import AnalysisConfig
from .models import MetricDefinition, MetricEvaluation


def classify_group(row: Dict[str, Any], config: AnalysisConfig) -> str:
    band = row.get("BandNorm", "")
    outcome = row.get("OutcomeNorm", "")
    if band in config.high_band_labels and outcome in config.ok_labels:
        return "ALTA_OK"
    if band in config.high_band_labels and outcome in config.ko_labels:
        return "ALTA_KO"
    if band in config.medium_band_labels and outcome in config.ok_labels:
        return "MEDIA_OK"
    if band in config.medium_band_labels and outcome in config.ko_labels:
        return "MEDIA_KO"
    return "OTHER"


def _ratio(num: int, den: int) -> float:
    return num / den if den else 0.0


def evaluate_metrics(
    rows: List[Dict[str, Any]],
    metrics: Iterable[MetricDefinition],
    config: AnalysisConfig,
) -> Tuple[List[MetricEvaluation], Dict[str, List[str]]]:
    groups = [classify_group(row, config) for row in rows]
    totals = Counter(groups)
    analyzed_total = sum(totals[g] for g in ("ALTA_OK", "ALTA_KO", "MEDIA_OK", "MEDIA_KO"))

    base_alta_ko_rate = _ratio(totals["ALTA_KO"], totals["ALTA_OK"] + totals["ALTA_KO"])
    base_media_ok_rate = _ratio(totals["MEDIA_OK"], totals["MEDIA_OK"] + totals["MEDIA_KO"])

    evaluations: List[MetricEvaluation] = []
    occurrences_by_metric: Dict[str, List[str]] = {}

    for metric in metrics:
        counts = Counter()
        matching_ids: List[str] = []
        for idx, (row, group) in enumerate(zip(rows, groups)):
            try:
                matched = bool(metric.predicate(row))
            except (TypeError, ValueError, KeyError):
                matched = False
            if matched:
                counts[group] += 1
                matching_ids.append(str(idx))

        occurrences = sum(counts.values())
        if occurrences == 0:
            continue

        alta_total = counts["ALTA_OK"] + counts["ALTA_KO"]
        media_total = counts["MEDIA_OK"] + counts["MEDIA_KO"]
        over_total = counts["ALTA_OK"] + counts["MEDIA_OK"]
        under_total = counts["ALTA_KO"] + counts["MEDIA_KO"]

        alta_ko_rate = _ratio(counts["ALTA_KO"], alta_total)
        media_ok_precision = _ratio(counts["MEDIA_OK"], media_total)

        evaluations.append(MetricEvaluation(
            metric_name=metric.name,
            family=metric.family,
            description=metric.description,
            occurrences=occurrences,
            alta_ok=counts["ALTA_OK"],
            alta_ko=counts["ALTA_KO"],
            media_ok=counts["MEDIA_OK"],
            media_ko=counts["MEDIA_KO"],
            other=counts["OTHER"],
            over_total=over_total,
            under_total=under_total,
            over_precision=_ratio(over_total, over_total + under_total),
            coverage=_ratio(occurrences, analyzed_total),
            alta_ko_capture=_ratio(counts["ALTA_KO"], totals["ALTA_KO"]),
            alta_ok_capture=_ratio(counts["ALTA_OK"], totals["ALTA_OK"]),
            media_ok_capture=_ratio(counts["MEDIA_OK"], totals["MEDIA_OK"]),
            media_ko_capture=_ratio(counts["MEDIA_KO"], totals["MEDIA_KO"]),
            alta_ko_lift=_ratio(alta_ko_rate, base_alta_ko_rate) if base_alta_ko_rate else 0.0,
            media_ok_precision=media_ok_precision,
            media_ok_lift=_ratio(media_ok_precision, base_media_ok_rate) if base_media_ok_rate else 0.0,
            exclusion_efficiency=alta_ko_rate,
            promotion_efficiency=media_ok_precision,
        ))
        occurrences_by_metric[metric.name] = matching_ids

    return evaluations, occurrences_by_metric


def build_pair_metrics(
    base_metrics: List[MetricDefinition],
    evaluations: List[MetricEvaluation],
    config: AnalysisConfig,
) -> List[MetricDefinition]:
    """Genera coppie usando solo metriche semplici con supporto sufficiente."""
    evaluation_map = {e.metric_name: e for e in evaluations}
    eligible = [
        m for m in base_metrics
        if m.name in evaluation_map
        and evaluation_map[m.name].occurrences >= config.min_occurrences_pair
    ]

    # Limita l'esplosione combinatoria privilegiando copertura e lift.
    eligible.sort(
        key=lambda m: (
            evaluation_map[m.name].occurrences,
            max(evaluation_map[m.name].alta_ko_lift, evaluation_map[m.name].media_ok_lift),
        ),
        reverse=True,
    )
    eligible = eligible[:config.max_pair_metrics]

    pairs: List[MetricDefinition] = []
    for i, left in enumerate(eligible):
        for right in eligible[i + 1:]:
            if left.family == right.family and left.name.split("_")[0] == right.name.split("_")[0]:
                continue

            def predicate(row, lp=left.predicate, rp=right.predicate):
                return bool(lp(row)) and bool(rp(row))

            pairs.append(MetricDefinition(
                name=f"{left.name}__AND__{right.name}",
                family="pair",
                description=f"{left.description} AND {right.description}",
                predicate=predicate,
            ))
    return pairs
