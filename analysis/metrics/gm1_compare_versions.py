"""Confronto diagnostico GM1 v1/v2 su stesse partite e mercati.

Esecuzione: python -m analysis.metrics.gm1_compare_versions
Input: data/analysis/gm1_walkforward[_v2]_selections.csv
Output: data/analysis/gm1_compare_*.csv
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("data/analysis")
V1 = ROOT / "gm1_walkforward_selections.csv"
V2 = ROOT / "gm1_walkforward_v2_selections.csv"
KEY = ("LeagueId", "MatchDate", "Home", "Away")
THRESHOLDS = (0, 60, 65, 70, 75, 80, 85, 90, 95)
MIN_SAMPLES = (10, 20, 30, 40)


def load(path):
    result = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f, delimiter=";"):
            key = tuple(row[k] for k in KEY)
            if key in result:
                raise ValueError(f"Duplicato in {path}: {key}")
            result[key] = row
    return result


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def write(name, columns, rows):
    path = ROOT / name
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, delimiter=";")
        w.writeheader()
        w.writerows(rows)
    print(f"[WRITE] {path}: {len(rows)} righe")


def summarize(rows):
    n = len(rows)
    ok = sum(r["Result"] == "OK" for r in rows)
    return {"OK": ok, "KO": n-ok, "Totale": n,
            "Perc": round(100*ok/n, 2) if n else 0}


def print_stats(label, rows):
    s = summarize(rows)
    print(f"{label}: OK={s['OK']} KO={s['KO']} "
          f"Tot={s['Totale']} Perc={s['Perc']:.2f}%")


def run():
    a, b = load(V1), load(V2)
    print(f"[GM1-COMPARE] v1={len(a)} v2={len(b)}")
    common = set(a) & set(b)
    comparable = [k for k in common if a[k]["Market"] == b[k]["Market"]]
    changed_market = common - set(comparable)
    print(f"[GM1-COMPARE] common_fixture={len(common)} "
          f"same_market={len(comparable)} different_market={len(changed_market)} "
          f"only_v1={len(set(a)-set(b))} only_v2={len(set(b)-set(a))}")
    for market in ("Over25", "Over15"):
        keys = [k for k in comparable if a[k]["Market"] == market]
        same = [k for k in keys if a[k]["Engine"] == b[k]["Engine"]]
        different = [k for k in keys if a[k]["Engine"] != b[k]["Engine"]]
        print(f"\n[{market}] common={len(keys)} same_engine={len(same)} "
              f"different_engine={len(different)}")
        for name, selection in (("v1 same", a), ("v2 same", b)):
            print_stats(name, [selection[k] for k in same])
        for name, selection in (("v1 different", a), ("v2 different", b)):
            print_stats(name, [selection[k] for k in different])
        # Results are match-level outcomes. If the market is identical,
        # the actual OK/KO must match regardless of chosen engine.
        mismatches = [k for k in keys if a[k]["Result"] != b[k]["Result"]]
        print(f"[CHECK] same_market_outcome_mismatches={len(mismatches)}")
        if mismatches:
            print("[WARNING] Disaccordo negli esiti: verificare dataset.")
    # Per-market engine breakdown and v2's confidence distribution.
    engine_rows = []
    for version, data in (("v1", a), ("v2", b)):
        groups = defaultdict(list)
        for row in data.values():
            groups[(row["Market"], row["Engine"])].append(row)
        for (market, engine), rows in groups.items():
            engine_rows.append({"Version": version, "Market": market,
                                "Engine": engine, **summarize(rows)})
    engine_rows.sort(key=lambda r: (r["Market"], -r["Perc"], -r["Totale"], r["Version"]))
    write("gm1_compare_engine_market.csv",
          ("Version", "Market", "Engine", "OK", "KO", "Totale", "Perc"),
          engine_rows)
    print("\n[GM1-COMPARE] V20:")
    for version, data in (("v1", a), ("v2", b)):
        for market in ("Over25", "Over15"):
            print_stats(f"{version} {market}",
                        [r for r in data.values()
                         if r["Engine"] == "v20" and r["Market"] == market])
    # This is an in-sample diagnostic on walk-forward predictions.
    # Thresholds MUST NOT be selected here and reported as held-out performance.
    threshold_rows = []
    for market in ("Over25", "Over15"):
        market_rows = [r for r in b.values() if r["Market"] == market]
        print(f"\n[GM1-V2] {market} soglie diagnostiche (NON out-of-sample)")
        for metric in ("HistoricalHitRate", "WilsonLower"):
            for samples in MIN_SAMPLES:
                for threshold in THRESHOLDS:
                    filtered = [r for r in market_rows
                                if (number(r.get(metric)) is not None
                                    and number(r.get(metric)) >= threshold
                                    and (number(r.get("SimilarMatches")) or 0) >= samples)]
                    stats = summarize(filtered)
                    threshold_rows.append({"Market": market, "Metric": metric,
                                           "MinSimilar": samples, "MinMetric": threshold,
                                           "CoveragePct": round(100*len(filtered)/len(market_rows), 2)
                                           if market_rows else 0, **stats})
                    if metric == "WilsonLower" and samples == 10 and threshold in (0, 70, 80, 90):
                        print_stats(f"Wilson>={threshold}", filtered)
    write("gm1_compare_thresholds_v2.csv",
          ("Market", "Metric", "MinSimilar", "MinMetric", "OK", "KO",
           "Totale", "Perc", "CoveragePct"), threshold_rows)
    changes = []
    for key in sorted(common):
        r1, r2 = a[key], b[key]
        changes.append(dict(zip(KEY, key), V1Engine=r1["Engine"],
                            V2Engine=r2["Engine"], V1Market=r1["Market"],
                            V2Market=r2["Market"], V1Result=r1["Result"],
                            V2Result=r2["Result"],
                            SameMarket=int(r1["Market"] == r2["Market"]),
                            SameEngine=int(r1["Engine"] == r2["Engine"])))
    write("gm1_compare_common_fixtures.csv",
          (*KEY, "V1Engine", "V2Engine", "V1Market", "V2Market",
           "V1Result", "V2Result", "SameMarket", "SameEngine"), changes)
    print("\n[NOTA] Su stesso incontro e stesso mercato l'esito non dipende "
          "dall'engine: le differenze di precisione derivano dalla selezione "
          "di partite/mercati differenti. Le soglie sono esplorative.")


if __name__ == "__main__":
    run()
