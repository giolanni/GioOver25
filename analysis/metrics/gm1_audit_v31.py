"""GM1-V3.1: audit paired V2/V3 selections without confusing markets.

Run: python -m analysis.metrics.gm1_audit_v31
Uses existing V2/V3 CSVs; never changes engine predictions.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

from .gm1_walkforward_v2 import KEY

ROOT = Path("data/analysis")
V2 = ROOT / "gm1_walkforward_v2_selections.csv"
V3 = ROOT / "gm1_walkforward_v3_selections.csv"
DETAIL = ROOT / "gm1_v31_divergences.csv"
SUMMARY = ROOT / "gm1_v31_audit_summary.csv"
ENGINE = ROOT / "gm1_v31_engine_changes.csv"
MARKETS = ("Over25", "Over15")


def load(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run the corresponding walkforward first.")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter=";"))
    indexed = {}
    for row in rows:
        key = tuple(row.get(k, "") for k in KEY)
        if key in indexed:
            raise ValueError(f"Duplicate fixture in {path}: {key}")
        indexed[key] = row
    return indexed


def result_for_market(row, market):
    # The market outcome is a property of the fixture, not the chosen engine.
    # Over25 OK implies Over15 OK; Over15 KO implies Over25 KO.
    if row is None:
        return None
    if row.get("Market") == market and row.get("Result") in ("OK", "KO"):
        return row["Result"]
    if market == "Over15" and row.get("Market") == "Over25" and row.get("Result") == "OK":
        return "OK"
    if market == "Over25" and row.get("Market") == "Over15" and row.get("Result") == "KO":
        return "KO"
    return None


def add_stats(counter, result):
    counter["Total"] += 1
    if result == "OK":
        counter["OK"] += 1
    elif result == "KO":
        counter["KO"] += 1
    else:
        counter["Unknown"] += 1


def pct(ok, ko):
    return f"{100 * ok / (ok + ko):.2f}" if ok + ko else ""


def write(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, delimiter=";", fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[WRITE] {path}: {len(rows)} righe")


def run():
    v2, v3 = load(V2), load(V3)
    common = sorted(v2.keys() & v3.keys())
    summary = defaultdict(Counter)
    changes = defaultdict(Counter)
    details = []
    for key in common:
        a, b = v2[key], v3[key]
        ma, mb = a.get("Market"), b.get("Market")
        ra, rb = a.get("Result"), b.get("Result")
        if ma not in MARKETS or mb not in MARKETS:
            raise ValueError(f"Unsupported market for {key}: {ma}, {mb}")
        if ra not in ("OK", "KO") or rb not in ("OK", "KO"):
            raise ValueError(f"Missing outcome for {key}: {ra}, {rb}")
        if ma == mb and ra != rb:
            raise ValueError(f"Contradictory outcomes for {key}: {ra}, {rb}")
        # Cross-market logical consistency; cannot infer Over25 from an Over15 OK.
        if (ma == "Over25" and ra == "OK" and mb == "Over15" and rb != "OK") or (
            mb == "Over25" and rb == "OK" and ma == "Over15" and ra != "OK"
        ):
            raise ValueError(f"Inconsistent Over25/Over15 outcomes for {key}")
        if (ma == "Over15" and ra == "KO" and mb == "Over25" and rb != "KO") or (
            mb == "Over15" and rb == "KO" and ma == "Over25" and ra != "KO"
        ):
            raise ValueError(f"Inconsistent Over15/Over25 outcomes for {key}")

        same_engine = a["Engine"] == b["Engine"]
        same_market = ma == mb
        category = ("SAME_MARKET_SAME_ENGINE" if same_market and same_engine else
                    "SAME_MARKET_DIFFERENT_ENGINE" if same_market else
                    "V2_OVER25_V3_OVER15" if ma == "Over25" else
                    "V2_OVER15_V3_OVER25")
        add_stats(summary[(category, "V2")], ra)
        add_stats(summary[(category, "V3")], rb)
        add_stats(summary[("ALL_COMMON", "V2")], ra)
        add_stats(summary[("ALL_COMMON", "V3")], rb)
        if ma != mb:
            # Both outcomes are directly observed in different selected markets.
            add_stats(summary[("CROSS_MARKET", "V2")], ra)
            add_stats(summary[("CROSS_MARKET", "V3")], rb)
        if not same_engine:
            changes[(a["Engine"], b["Engine"], ma, mb)]["Total"] += 1
            changes[(a["Engine"], b["Engine"], ma, mb)]["V2OK"] += ra == "OK"
            changes[(a["Engine"], b["Engine"], ma, mb)]["V3OK"] += rb == "OK"
        if not same_market or not same_engine:
            details.append({**dict(zip(KEY, key)), "Category": category,
                            "V2Engine": a["Engine"], "V3Engine": b["Engine"],
                            "V2Band": a.get("Band", ""), "V3Band": b.get("Band", ""),
                            "V2Score": a.get("Score", ""), "V3Score": b.get("Score", ""),
                            "V2Market": ma, "V3Market": mb,
                            "V2Result": ra, "V3Result": rb,
                            "V2SimilarMatches": a.get("SimilarMatches", ""),
                            "V3SimilarMatches": b.get("SimilarMatches", ""),
                            "V2HistoricalHitRate": a.get("HistoricalHitRate", ""),
                            "V3HistoricalHitRate": b.get("HistoricalHitRate", ""),
                            "V2WilsonLower": a.get("WilsonLower", ""),
                            "V3WilsonLower": b.get("WilsonLower", ""),
                            "SameMarket": int(same_market),
                            "SameEngine": int(same_engine)})
    detail_fields = (*KEY, "Category", "V2Engine", "V3Engine", "V2Band", "V3Band",
                     "V2Score", "V3Score", "V2Market", "V3Market",
                     "V2Result", "V3Result", "V2SimilarMatches", "V3SimilarMatches",
                     "V2HistoricalHitRate", "V3HistoricalHitRate",
                     "V2WilsonLower", "V3WilsonLower", "SameMarket", "SameEngine")
    write(DETAIL, detail_fields, details)
    summary_rows = []
    for (category, version), c in sorted(summary.items()):
        summary_rows.append({"Category": category, "Version": version,
                             "OK": c["OK"], "KO": c["KO"],
                             "Total": c["Total"], "Pct": pct(c["OK"], c["KO"]),
                             "Unknown": c["Unknown"]})
    write(SUMMARY, ("Category", "Version", "OK", "KO", "Total", "Pct", "Unknown"), summary_rows)
    engine_rows = []
    for (ea, eb, ma, mb), c in changes.items():
        engine_rows.append({"V2Engine": ea, "V3Engine": eb,
                            "V2Market": ma, "V3Market": mb,
                            "Total": c["Total"], "V2OK": c["V2OK"],
                            "V3OK": c["V3OK"]})
    engine_rows.sort(key=lambda r: (-r["Total"], r["V2Engine"], r["V3Engine"]))
    write(ENGINE, ("V2Engine", "V3Engine", "V2Market", "V3Market",
                   "Total", "V2OK", "V3OK"), engine_rows)
    cross = sum(1 for r in details if not r["SameMarket"])
    changed_engine = sum(1 for r in details if not r["SameEngine"])
    print(f"[GM1-V3.1] common={len(common)} v2_only={len(v2)-len(common)} "
          f"v3_only={len(v3)-len(common)}")
    print(f"[GM1-V3.1] cross_market={cross} changed_engine={changed_engine} "
          f"same_market_changed_engine={sum(r['SameMarket'] and not r['SameEngine'] for r in details)}")
    for category in ("V2_OVER25_V3_OVER15", "V2_OVER15_V3_OVER25", "CROSS_MARKET"):
        for version in ("V2", "V3"):
            c = summary[(category, version)]
            print(f"[GM1-V3.1] {category} {version}: OK={c['OK']} KO={c['KO']} "
                  f"Tot={c['Total']} Pct={pct(c['OK'], c['KO'])}")
    print("[NOTE] Cross-market percentages describe different betting markets; "
          "they are not a like-for-like engine accuracy comparison.")


if __name__ == "__main__":
    run()
