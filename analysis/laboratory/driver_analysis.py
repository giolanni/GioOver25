"""
===============================================================================
GioOver2.5 - analysis/laboratory/driver_analysis.py
===============================================================================

SCOPO
-----
Analizzare i driver ex ante del motore v25 confrontando sempre le quattro
popolazioni fondamentali del progetto:

    ALTA_OK
    ALTA_KO
    MEDIA_OK
    MEDIA_KO

OBIETTIVI
---------
1. Ridurre gli ALTA_KO.
2. Individuare MEDIA_OK con caratteristiche simili agli ALTA_OK, così da
   costruire future regole di promozione da MEDIA ad ALTA.
3. Individuare driver poco discriminanti o ridondanti.
4. Produrre soglie, coppie e triple candidate senza modificare automaticamente
   l'algoritmo.

FILE LETTO
----------
    analysis/laboratory/data/01_matches.csv

FILE SCRITTI
-------------
    07_driver_power.csv
    08_driver_curves.csv
    09_driver_pairs.csv
    10_driver_triples.csv
    11_driver_correlation.csv
    12_driver_useless.csv

LOGICA
------
07_driver_power.csv
    Statistiche per ciascun driver nelle quattro popolazioni, differenze tra
    OK e KO nelle due fasce, AUC empirica e dimensione dell'effetto.

08_driver_curves.csv
    Curve di successo per quantili, separate per fascia ALTA e MEDIA.

09_driver_pairs.csv
    Coppie di condizioni semplici (<= o >= soglia) valutate separatamente
    nelle fasce ALTA e MEDIA.

10_driver_triples.csv
    Triple costruite soltanto dalle condizioni singole più promettenti.

11_driver_correlation.csv
    Correlazione Pearson tra i driver sulle partite concluse.

12_driver_useless.csv
    Classificazione diagnostica dei driver poco discriminanti, instabili o
    fortemente ridondanti.

LIMITAZIONI
-----------
- I report descrivono lo storico disponibile e non sono regole già validate.
- Coppie e triple con campioni piccoli vengono escluse.
- Le soglie sono ricavate dai quantili dei valori osservati.
===============================================================================
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Callable
import csv
import math


INPUT_FILE = Path("analysis/laboratory/data/01_matches.csv")
OUTPUT_DIR = Path("analysis/laboratory/data")

DRIVERS = [
    "RankingGapScore",
    "HomeAttackScore",
    "AwayAttackScore",
    "HomeDefenseWeaknessScore",
    "AwayDefenseWeaknessScore",
    "HomeLast10OverScore",
    "AwayLast10OverScore",
    "HomeVenueOverScore",
    "AwayVenueOverScore",
    "BTTSProfileScore",
]

GROUPS = [
    "ALTA_OK",
    "ALTA_KO",
    "MEDIA_OK",
    "MEDIA_KO",
]

MIN_PAIR_OCCURRENCES = 15
MIN_TRIPLE_OCCURRENCES = 12
MAX_SINGLE_RULES_FOR_TRIPLES = 18


def _text(value: Any) -> str:
    return str(value or "").strip()


def _to_float(value: Any) -> float | None:
    raw = _text(value).replace(",", ".")

    if not raw:
        return None

    try:
        return float(raw)
    except ValueError:
        return None


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return ordered[lower]

    fraction = position - lower

    return (
        ordered[lower] * (1.0 - fraction)
        + ordered[upper] * fraction
    )


def _group(row: dict) -> str:
    band = _text(row.get("Band")).upper()
    outcome = _text(row.get("Outcome")).upper()
    return f"{band}_{outcome}"


def _load_rows(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset Laboratory non trovato: {path}"
        )

    rows = []

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(
            handle,
            delimiter=";",
        )

        missing = {
            "Band",
            "Outcome",
            *DRIVERS,
        }.difference(reader.fieldnames or [])

        if missing:
            raise ValueError(
                "Colonne mancanti in 01_matches.csv: "
                + ", ".join(sorted(missing))
            )

        for raw in reader:
            group = _group(raw)

            if group not in GROUPS:
                continue

            row = dict(raw)
            row["_Group"] = group

            valid = True

            for driver in DRIVERS:
                value = _to_float(
                    raw.get(driver)
                )

                if value is None:
                    valid = False
                    break

                row[driver] = value

            if valid:
                rows.append(row)

    return rows


def _write_csv(
    path: Path,
    rows: list[dict],
    fieldnames: list[str],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


def _auc(
    positive_values: list[float],
    negative_values: list[float],
) -> float | None:
    """
    AUC empirica tramite confronti a coppie.

    0.5 = nessuna separazione.
    > 0.5 = valori più alti associati agli OK.
    < 0.5 = valori più bassi associati agli OK.
    """
    if not positive_values or not negative_values:
        return None

    wins = 0.0
    comparisons = 0

    for positive in positive_values:
        for negative in negative_values:
            comparisons += 1

            if positive > negative:
                wins += 1.0
            elif positive == negative:
                wins += 0.5

    return wins / comparisons


def _cohen_d(
    first: list[float],
    second: list[float],
) -> float | None:
    if len(first) < 2 or len(second) < 2:
        return None

    first_std = pstdev(first)
    second_std = pstdev(second)

    pooled_variance = (
        (
            (len(first) - 1) * first_std ** 2
            + (len(second) - 1) * second_std ** 2
        )
        / (
            len(first)
            + len(second)
            - 2
        )
    )

    if pooled_variance <= 0:
        return 0.0

    return (
        mean(first)
        - mean(second)
    ) / math.sqrt(pooled_variance)


def build_driver_power(
    rows: list[dict],
) -> list[dict]:
    output = []

    for driver in DRIVERS:
        values_by_group = {
            group: [
                row[driver]
                for row in rows
                if row["_Group"] == group
            ]
            for group in GROUPS
        }

        alta_auc = _auc(
            values_by_group["ALTA_OK"],
            values_by_group["ALTA_KO"],
        )

        media_auc = _auc(
            values_by_group["MEDIA_OK"],
            values_by_group["MEDIA_KO"],
        )

        alta_effect = _cohen_d(
            values_by_group["ALTA_OK"],
            values_by_group["ALTA_KO"],
        )

        media_effect = _cohen_d(
            values_by_group["MEDIA_OK"],
            values_by_group["MEDIA_KO"],
        )

        row = {
            "Driver": driver,
        }

        for group in GROUPS:
            values = values_by_group[group]

            row[f"{group}_Count"] = len(values)
            row[f"{group}_Mean"] = (
                round(mean(values), 6)
                if values
                else ""
            )
            row[f"{group}_Median"] = (
                round(median(values), 6)
                if values
                else ""
            )
            row[f"{group}_StdDev"] = (
                round(pstdev(values), 6)
                if len(values) > 1
                else 0.0
            )

        row["AltaDeltaMean"] = round(
            mean(values_by_group["ALTA_OK"])
            - mean(values_by_group["ALTA_KO"]),
            6,
        )

        row["MediaDeltaMean"] = round(
            mean(values_by_group["MEDIA_OK"])
            - mean(values_by_group["MEDIA_KO"]),
            6,
        )

        row["AltaAUC"] = (
            round(alta_auc, 6)
            if alta_auc is not None
            else ""
        )

        row["MediaAUC"] = (
            round(media_auc, 6)
            if media_auc is not None
            else ""
        )

        row["AltaEffectSize"] = (
            round(alta_effect, 6)
            if alta_effect is not None
            else ""
        )

        row["MediaEffectSize"] = (
            round(media_effect, 6)
            if media_effect is not None
            else ""
        )

        row["AltaDirection"] = (
            "HIGHER_IS_BETTER"
            if alta_auc is not None and alta_auc >= 0.5
            else "LOWER_IS_BETTER"
        )

        row["MediaDirection"] = (
            "HIGHER_IS_BETTER"
            if media_auc is not None and media_auc >= 0.5
            else "LOWER_IS_BETTER"
        )

        row["AltaPower"] = (
            round(abs(alta_auc - 0.5) * 2, 6)
            if alta_auc is not None
            else ""
        )

        row["MediaPower"] = (
            round(abs(media_auc - 0.5) * 2, 6)
            if media_auc is not None
            else ""
        )

        output.append(row)

    output.sort(
        key=lambda item: (
            -max(
                float(item["AltaPower"] or 0),
                float(item["MediaPower"] or 0),
            ),
            item["Driver"],
        )
    )

    return output


def build_driver_curves(
    rows: list[dict],
) -> list[dict]:
    output = []

    for driver in DRIVERS:
        all_values = [
            row[driver]
            for row in rows
        ]

        edges = [
            _percentile(
                all_values,
                index / 10,
            )
            for index in range(11)
        ]

        # Rimuove soglie duplicate, comuni per driver discreti/cappati.
        unique_edges = []

        for edge in edges:
            if (
                not unique_edges
                or edge != unique_edges[-1]
            ):
                unique_edges.append(edge)

        if len(unique_edges) == 1:
            unique_edges.append(
                unique_edges[0]
            )

        for band in ("ALTA", "MEDIA"):
            band_rows = [
                row
                for row in rows
                if row["_Group"].startswith(
                    f"{band}_"
                )
            ]

            for index in range(
                len(unique_edges) - 1
            ):
                lower = unique_edges[index]
                upper = unique_edges[index + 1]

                selected = []

                for row in band_rows:
                    value = row[driver]

                    if index == len(unique_edges) - 2:
                        inside = (
                            lower <= value <= upper
                        )
                    else:
                        inside = (
                            lower <= value < upper
                        )

                    if inside:
                        selected.append(row)

                ok_count = sum(
                    1
                    for row in selected
                    if row["_Group"]
                    == f"{band}_OK"
                )

                ko_count = sum(
                    1
                    for row in selected
                    if row["_Group"]
                    == f"{band}_KO"
                )

                total = ok_count + ko_count

                output.append({
                    "Driver": driver,
                    "Band": band,
                    "BinIndex": index + 1,
                    "BinMin": round(lower, 6),
                    "BinMax": round(upper, 6),
                    "OK": ok_count,
                    "KO": ko_count,
                    "Total": total,
                    "HitRate": (
                        round(ok_count / total, 6)
                        if total
                        else ""
                    ),
                })

    return output


def _single_rules(
    rows: list[dict],
) -> list[dict]:
    rules = []

    for driver in DRIVERS:
        values = [
            row[driver]
            for row in rows
        ]

        thresholds = sorted({
            round(
                _percentile(values, q),
                6,
            )
            for q in (
                0.20,
                0.30,
                0.40,
                0.50,
                0.60,
                0.70,
                0.80,
            )
        })

        for threshold in thresholds:
            for operator in ("<=", ">="):
                rules.append({
                    "Driver": driver,
                    "Operator": operator,
                    "Threshold": threshold,
                })

    return rules


def _rule_matches(
    row: dict,
    rule: dict,
) -> bool:
    value = row[
        rule["Driver"]
    ]

    threshold = float(
        rule["Threshold"]
    )

    if rule["Operator"] == "<=":
        return value <= threshold

    return value >= threshold


def _rule_text(
    rule: dict,
) -> str:
    return (
        f'{rule["Driver"]}'
        f'{rule["Operator"]}'
        f'{rule["Threshold"]}'
    )


def _evaluate_condition(
    rows: list[dict],
    predicate: Callable[[dict], bool],
) -> dict:
    counters = {
        group: 0
        for group in GROUPS
    }

    for row in rows:
        if predicate(row):
            counters[
                row["_Group"]
            ] += 1

    alta_total = (
        counters["ALTA_OK"]
        + counters["ALTA_KO"]
    )

    media_total = (
        counters["MEDIA_OK"]
        + counters["MEDIA_KO"]
    )

    return {
        **counters,
        "AltaTotal": alta_total,
        "AltaHitRate": (
            counters["ALTA_OK"]
            / alta_total
            if alta_total
            else None
        ),
        "MediaTotal": media_total,
        "MediaHitRate": (
            counters["MEDIA_OK"]
            / media_total
            if media_total
            else None
        ),
    }


def build_driver_pairs(
    rows: list[dict],
) -> tuple[list[dict], list[dict]]:
    rules = _single_rules(rows)

    single_scores = []

    for rule in rules:
        result = _evaluate_condition(
            rows,
            lambda row, rule=rule: (
                _rule_matches(row, rule)
            ),
        )

        alta_hit = result["AltaHitRate"]
        media_hit = result["MediaHitRate"]

        score = max(
            (
                alta_hit
                if (
                    alta_hit is not None
                    and result["AltaTotal"]
                    >= MIN_PAIR_OCCURRENCES
                )
                else 0
            ),
            (
                media_hit
                if (
                    media_hit is not None
                    and result["MediaTotal"]
                    >= MIN_PAIR_OCCURRENCES
                )
                else 0
            ),
        )

        single_scores.append({
            **rule,
            **result,
            "Score": score,
        })

    output = []

    for first, second in combinations(
        rules,
        2,
    ):
        if first["Driver"] == second["Driver"]:
            continue

        result = _evaluate_condition(
            rows,
            lambda row, first=first, second=second: (
                _rule_matches(row, first)
                and _rule_matches(row, second)
            ),
        )

        if (
            result["AltaTotal"]
            < MIN_PAIR_OCCURRENCES
            and result["MediaTotal"]
            < MIN_PAIR_OCCURRENCES
        ):
            continue

        alta_hit = result["AltaHitRate"]
        media_hit = result["MediaHitRate"]

        output.append({
            "Rule1": _rule_text(first),
            "Rule2": _rule_text(second),
            **{
                group: result[group]
                for group in GROUPS
            },
            "AltaTotal": result["AltaTotal"],
            "AltaHitRate": (
                round(alta_hit, 6)
                if alta_hit is not None
                else ""
            ),
            "MediaTotal": result["MediaTotal"],
            "MediaHitRate": (
                round(media_hit, 6)
                if media_hit is not None
                else ""
            ),
            "PrimaryUse": (
                "REDUCE_ALTA_KO"
                if (
                    alta_hit is not None
                    and (
                        media_hit is None
                        or alta_hit >= media_hit
                    )
                )
                else "PROMOTE_MEDIA_OK"
            ),
        })

    output.sort(
        key=lambda item: (
            -max(
                float(item["AltaHitRate"] or 0),
                float(item["MediaHitRate"] or 0),
            ),
            -max(
                int(item["AltaTotal"]),
                int(item["MediaTotal"]),
            ),
            item["Rule1"],
            item["Rule2"],
        )
    )

    single_scores.sort(
        key=lambda item: (
            -float(item["Score"]),
            -max(
                item["AltaTotal"],
                item["MediaTotal"],
            ),
        )
    )

    return output, single_scores


def build_driver_triples(
    rows: list[dict],
    single_scores: list[dict],
) -> list[dict]:
    selected_rules = []

    seen = set()

    for rule in single_scores:
        key = (
            rule["Driver"],
            rule["Operator"],
            rule["Threshold"],
        )

        if key in seen:
            continue

        selected_rules.append({
            "Driver": rule["Driver"],
            "Operator": rule["Operator"],
            "Threshold": rule["Threshold"],
        })

        seen.add(key)

        if (
            len(selected_rules)
            >= MAX_SINGLE_RULES_FOR_TRIPLES
        ):
            break

    output = []

    for first, second, third in combinations(
        selected_rules,
        3,
    ):
        if len({
            first["Driver"],
            second["Driver"],
            third["Driver"],
        }) < 3:
            continue

        result = _evaluate_condition(
            rows,
            lambda row, first=first, second=second, third=third: (
                _rule_matches(row, first)
                and _rule_matches(row, second)
                and _rule_matches(row, third)
            ),
        )

        if (
            result["AltaTotal"]
            < MIN_TRIPLE_OCCURRENCES
            and result["MediaTotal"]
            < MIN_TRIPLE_OCCURRENCES
        ):
            continue

        alta_hit = result["AltaHitRate"]
        media_hit = result["MediaHitRate"]

        output.append({
            "Rule1": _rule_text(first),
            "Rule2": _rule_text(second),
            "Rule3": _rule_text(third),
            **{
                group: result[group]
                for group in GROUPS
            },
            "AltaTotal": result["AltaTotal"],
            "AltaHitRate": (
                round(alta_hit, 6)
                if alta_hit is not None
                else ""
            ),
            "MediaTotal": result["MediaTotal"],
            "MediaHitRate": (
                round(media_hit, 6)
                if media_hit is not None
                else ""
            ),
            "PrimaryUse": (
                "REDUCE_ALTA_KO"
                if (
                    alta_hit is not None
                    and (
                        media_hit is None
                        or alta_hit >= media_hit
                    )
                )
                else "PROMOTE_MEDIA_OK"
            ),
        })

    output.sort(
        key=lambda item: (
            -max(
                float(item["AltaHitRate"] or 0),
                float(item["MediaHitRate"] or 0),
            ),
            -max(
                int(item["AltaTotal"]),
                int(item["MediaTotal"]),
            ),
        )
    )

    return output


def _pearson(
    first: list[float],
    second: list[float],
) -> float | None:
    if (
        len(first) != len(second)
        or len(first) < 2
    ):
        return None

    first_mean = mean(first)
    second_mean = mean(second)

    numerator = sum(
        (x - first_mean)
        * (y - second_mean)
        for x, y in zip(
            first,
            second,
        )
    )

    first_denominator = math.sqrt(
        sum(
            (x - first_mean) ** 2
            for x in first
        )
    )

    second_denominator = math.sqrt(
        sum(
            (y - second_mean) ** 2
            for y in second
        )
    )

    denominator = (
        first_denominator
        * second_denominator
    )

    if denominator == 0:
        return 0.0

    return numerator / denominator


def build_correlation(
    rows: list[dict],
) -> list[dict]:
    output = []

    for first, second in combinations(
        DRIVERS,
        2,
    ):
        first_values = [
            row[first]
            for row in rows
        ]

        second_values = [
            row[second]
            for row in rows
        ]

        correlation = _pearson(
            first_values,
            second_values,
        )

        output.append({
            "Driver1": first,
            "Driver2": second,
            "Count": len(rows),
            "Correlation": (
                round(correlation, 6)
                if correlation is not None
                else ""
            ),
            "AbsoluteCorrelation": (
                round(abs(correlation), 6)
                if correlation is not None
                else ""
            ),
            "RedundancyLevel": (
                "HIGH"
                if (
                    correlation is not None
                    and abs(correlation) >= 0.80
                )
                else (
                    "MEDIUM"
                    if (
                        correlation is not None
                        and abs(correlation) >= 0.60
                    )
                    else "LOW"
                )
            ),
        })

    output.sort(
        key=lambda item: (
            -float(
                item["AbsoluteCorrelation"]
                or 0
            ),
            item["Driver1"],
            item["Driver2"],
        )
    )

    return output


def build_useless_report(
    power_rows: list[dict],
    correlation_rows: list[dict],
) -> list[dict]:
    max_correlation = {
        driver: 0.0
        for driver in DRIVERS
    }

    correlated_with = {
        driver: ""
        for driver in DRIVERS
    }

    for row in correlation_rows:
        value = float(
            row["AbsoluteCorrelation"]
            or 0
        )

        first = row["Driver1"]
        second = row["Driver2"]

        if value > max_correlation[first]:
            max_correlation[first] = value
            correlated_with[first] = second

        if value > max_correlation[second]:
            max_correlation[second] = value
            correlated_with[second] = first

    output = []

    for row in power_rows:
        driver = row["Driver"]

        alta_power = float(
            row["AltaPower"]
            or 0
        )

        media_power = float(
            row["MediaPower"]
            or 0
        )

        best_power = max(
            alta_power,
            media_power,
        )

        redundancy = max_correlation[
            driver
        ]

        reasons = []

        if best_power < 0.10:
            reasons.append(
                "LOW_DISCRIMINATION"
            )

        if redundancy >= 0.80:
            reasons.append(
                "HIGH_REDUNDANCY"
            )

        if (
            row["AltaDirection"]
            != row["MediaDirection"]
        ):
            reasons.append(
                "UNSTABLE_DIRECTION"
            )

        if not reasons:
            classification = "USEFUL"
            recommendation = "KEEP_AND_MONITOR"
        elif (
            "LOW_DISCRIMINATION"
            in reasons
            and "HIGH_REDUNDANCY"
            in reasons
        ):
            classification = "WEAK"
            recommendation = "CONSIDER_REDUCING_WEIGHT"
        elif (
            "LOW_DISCRIMINATION"
            in reasons
        ):
            classification = "WEAK"
            recommendation = "REVIEW_WEIGHT"
        else:
            classification = "REDUNDANT_OR_UNSTABLE"
            recommendation = "REVIEW_INTERACTIONS"

        output.append({
            "Driver": driver,
            "AltaPower": round(
                alta_power,
                6,
            ),
            "MediaPower": round(
                media_power,
                6,
            ),
            "MaxAbsoluteCorrelation": round(
                redundancy,
                6,
            ),
            "MostCorrelatedWith": correlated_with[
                driver
            ],
            "Classification": classification,
            "Reasons": "|".join(
                reasons
            ),
            "Recommendation": recommendation,
        })

    output.sort(
        key=lambda item: (
            0
            if item["Classification"] == "WEAK"
            else (
                1
                if item["Classification"]
                == "REDUNDANT_OR_UNSTABLE"
                else 2
            ),
            max(
                float(item["AltaPower"]),
                float(item["MediaPower"]),
            ),
        )
    )

    return output


def main() -> int:
    rows = _load_rows(
        INPUT_FILE
    )

    power = build_driver_power(
        rows
    )

    curves = build_driver_curves(
        rows
    )

    pairs, single_scores = (
        build_driver_pairs(
            rows
        )
    )

    triples = build_driver_triples(
        rows,
        single_scores,
    )

    correlations = build_correlation(
        rows
    )

    useless = build_useless_report(
        power,
        correlations,
    )

    _write_csv(
        OUTPUT_DIR / "07_driver_power.csv",
        power,
        [
            "Driver",
            "ALTA_OK_Count",
            "ALTA_OK_Mean",
            "ALTA_OK_Median",
            "ALTA_OK_StdDev",
            "ALTA_KO_Count",
            "ALTA_KO_Mean",
            "ALTA_KO_Median",
            "ALTA_KO_StdDev",
            "MEDIA_OK_Count",
            "MEDIA_OK_Mean",
            "MEDIA_OK_Median",
            "MEDIA_OK_StdDev",
            "MEDIA_KO_Count",
            "MEDIA_KO_Mean",
            "MEDIA_KO_Median",
            "MEDIA_KO_StdDev",
            "AltaDeltaMean",
            "MediaDeltaMean",
            "AltaAUC",
            "MediaAUC",
            "AltaEffectSize",
            "MediaEffectSize",
            "AltaDirection",
            "MediaDirection",
            "AltaPower",
            "MediaPower",
        ],
    )

    _write_csv(
        OUTPUT_DIR / "08_driver_curves.csv",
        curves,
        [
            "Driver",
            "Band",
            "BinIndex",
            "BinMin",
            "BinMax",
            "OK",
            "KO",
            "Total",
            "HitRate",
        ],
    )

    _write_csv(
        OUTPUT_DIR / "09_driver_pairs.csv",
        pairs,
        [
            "Rule1",
            "Rule2",
            "ALTA_OK",
            "ALTA_KO",
            "MEDIA_OK",
            "MEDIA_KO",
            "AltaTotal",
            "AltaHitRate",
            "MediaTotal",
            "MediaHitRate",
            "PrimaryUse",
        ],
    )

    _write_csv(
        OUTPUT_DIR / "10_driver_triples.csv",
        triples,
        [
            "Rule1",
            "Rule2",
            "Rule3",
            "ALTA_OK",
            "ALTA_KO",
            "MEDIA_OK",
            "MEDIA_KO",
            "AltaTotal",
            "AltaHitRate",
            "MediaTotal",
            "MediaHitRate",
            "PrimaryUse",
        ],
    )

    _write_csv(
        OUTPUT_DIR / "11_driver_correlation.csv",
        correlations,
        [
            "Driver1",
            "Driver2",
            "Count",
            "Correlation",
            "AbsoluteCorrelation",
            "RedundancyLevel",
        ],
    )

    _write_csv(
        OUTPUT_DIR / "12_driver_useless.csv",
        useless,
        [
            "Driver",
            "AltaPower",
            "MediaPower",
            "MaxAbsoluteCorrelation",
            "MostCorrelatedWith",
            "Classification",
            "Reasons",
            "Recommendation",
        ],
    )

    group_counts = {
        group: sum(
            1
            for row in rows
            if row["_Group"] == group
        )
        for group in GROUPS
    }

    print("=== DRIVER ANALYSIS ===")
    print(
        f"Partite concluse analizzate: "
        f"{len(rows)}"
    )

    for group in GROUPS:
        print(
            f"{group}: "
            f"{group_counts[group]}"
        )

    print(
        f"Driver power: {len(power)}"
    )

    print(
        f"Curve: {len(curves)}"
    )

    print(
        f"Coppie: {len(pairs)}"
    )

    print(
        f"Triple: {len(triples)}"
    )

    print(
        f"Correlazioni: "
        f"{len(correlations)}"
    )

    print(
        f"Diagnostica driver: "
        f"{len(useless)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
