"""GM1: diagnostica delle divergenze tra engine sulla STESSA partita.

Esecuzione: python -m analysis.metrics.gm1_disagreements
Richiede: python -m analysis.metrics.gm1_engine_matrix
Non modifica engine, ranking o storici. Non interpreta fasce non mappate.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path("data/analysis")
KEY = ("LeagueId", "MatchDate", "Home", "Away")
SOURCE = ROOT / "gm1_engine_matrix_long.csv"
PAIR_FIELDS = (*KEY, "EngineA", "EngineB", "BandA", "BandB", "ScoreA",
               "ScoreB", "MarketA", "MarketB", "ResultA", "ResultB",
               "Over25", "Over15", "Comparison")
SUMMARY_FIELDS = ("EngineA", "EngineB", "Comparison", "Fixtures",
                  "BothOK", "BothKO", "OnlyAOK", "OnlyBOK",
                  "NeitherEvaluable", "AWinPct", "BWinPct")
DRIVER_FIELDS = ("Engine", "DriverSet", "Predictions", "RowsWithDriverSet",
                 "Status")


def read():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Manca {SOURCE}; eseguire prima gm1_engine_matrix")
    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def write(name, fields, rows):
    path = ROOT / name
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        w.writeheader()
        w.writerows(rows)
    print(f"[WRITE] {path}: {len(rows)} righe")


def outcome(row):
    return row["PredictionResult"] if row["PredictionResult"] in ("OK", "KO") else None


def comparison(a, b):
    ma, mb = a["Market"], b["Market"]
    if ma == mb == "NOT_EVALUATED":
        return "BOTH_UNEVALUATED"
    if ma == mb:
        return "SAME_MARKET"
    if "NOT_EVALUATED" in (ma, mb):
        return "ONE_UNEVALUATED"
    return "DIFFERENT_MARKETS"


def run():
    rows = read()
    fixtures = defaultdict(list)
    driver_sets = defaultdict(Counter)
    for row in rows:
        key = tuple(row[k] for k in KEY)
        fixtures[key].append(row)
        driver_sets[row["Engine"]][row.get("DriverSet", "")] += 1

    pair_rows = []
    summary = defaultdict(Counter)
    totals = Counter()
    for key, group in sorted(fixtures.items()):
        for a, b in combinations(sorted(group, key=lambda x: x["Engine"]), 2):
            kind = comparison(a, b)
            # Keep only actionable divergences in the detailed file.
            # Same-market rows are audited but cannot establish a winner.
            totals[kind] += 1
            if kind == "SAME_MARKET":
                if outcome(a) != outcome(b):
                    raise ValueError(f"Stesso mercato, esiti discordanti: {key}")
                continue
            if kind == "BOTH_UNEVALUATED":
                continue
            oa, ob = outcome(a), outcome(b)
            counter = summary[(a["Engine"], b["Engine"], kind)]
            counter["Fixtures"] += 1
            if oa is None or ob is None:
                counter["NeitherEvaluable"] += 1
            elif oa == ob == "OK":
                counter["BothOK"] += 1
            elif oa == ob == "KO":
                counter["BothKO"] += 1
            elif oa == "OK":
                counter["OnlyAOK"] += 1
            else:
                counter["OnlyBOK"] += 1
            pair_rows.append({
                **dict(zip(KEY, key)), "EngineA": a["Engine"],
                "EngineB": b["Engine"], "BandA": a["Band"],
                "BandB": b["Band"], "ScoreA": a["Score"],
                "ScoreB": b["Score"], "MarketA": a["Market"],
                "MarketB": b["Market"], "ResultA": a["PredictionResult"],
                "ResultB": b["PredictionResult"], "Over25": a["Over25"],
                "Over15": a["Over15"], "Comparison": kind,
            })
    summaries = []
    for (a, b, kind), c in summary.items():
        decisive = c["OnlyAOK"] + c["OnlyBOK"]
        summaries.append({
            "EngineA": a, "EngineB": b, "Comparison": kind,
            **{k: c[k] for k in ("Fixtures", "BothOK", "BothKO",
                                  "OnlyAOK", "OnlyBOK", "NeitherEvaluable")},
            "AWinPct": round(100*c["OnlyAOK"]/decisive, 2) if decisive else "",
            "BWinPct": round(100*c["OnlyBOK"]/decisive, 2) if decisive else "",
        })
    summaries.sort(key=lambda r: (-r["Fixtures"], r["EngineA"], r["EngineB"]))
    write("gm1_disagreements_pairs.csv", PAIR_FIELDS, pair_rows)
    write("gm1_disagreements_summary.csv", SUMMARY_FIELDS, summaries)
    driver_rows = []
    for engine, counts in sorted(driver_sets.items()):
        for fields, count in counts.items():
            driver_rows.append({
                "Engine": engine, "DriverSet": fields, "Predictions": count,
                "RowsWithDriverSet": count if fields else 0,
                "Status": "TO_VALIDATE_AGAINST_SOURCE" if fields else "NO_DRIVERS",
            })
    write("gm1_driver_validation_queue.csv", DRIVER_FIELDS, driver_rows)
    print(f"[GM1-DIVERGENCES] fixtures={len(fixtures)} engines={len(driver_sets)}")
    for kind, n in sorted(totals.items()):
        print(f"[GM1-DIVERGENCES] {kind}={n}")
    print("[NOTE] AWinPct/BWinPct riguardano SOLO casi con esiti opposti "
          "e mercati diversi; non sono stime della qualita' di un engine. "
          "Over15 e Over25 sono mercati diversi: non trattarli come "
          "pronostici equivalenti. I driver sono DA VALIDARE sul sorgente.")


if __name__ == "__main__":
    run()
