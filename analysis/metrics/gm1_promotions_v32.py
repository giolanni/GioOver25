"""GM1 V3.2: chronological audit of V2 Over15 -> V3 Over25 promotions.

The cutoff is selected using only the earlier training portion; the later
holdout is evaluated once. This is an offline experiment, not a new engine.
Run: python -m analysis.metrics.gm1_promotions_v32
"""
from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path

from .gm1_walkforward_v2 import KEY, numeric, wilson_lower
from .gm1_audit_v31 import load

ROOT = Path("data/analysis")
V2 = ROOT / "gm1_walkforward_v2_selections.csv"
V3 = ROOT / "gm1_walkforward_v3_selections.csv"
DETAIL = ROOT / "gm1_v32_promotions.csv"
SUMMARY = ROOT / "gm1_v32_promotion_summary.csv"
TRAIN_FRACTION = 0.70
MIN_TRAIN_ACCEPTED = 25

# Predefined grid. No candidate is created or modified after viewing holdout.
RULES = (
    ("ALL", 0, 0, 0),
    ("WILSON_55", 55, 0, 0),
    ("WILSON_60", 60, 0, 0),
    ("WILSON_65", 65, 0, 0),
    ("WILSON_70", 70, 0, 0),
    ("HIT_80", 0, 80, 0),
    ("HIT_85", 0, 85, 0),
    ("W60_H80", 60, 80, 0),
    ("W65_H80", 65, 80, 0),
    ("W60_H85", 60, 85, 0),
    ("W65_H85", 65, 85, 0),
    ("W60_N30", 60, 0, 30),
    ("W65_N30", 65, 0, 30),
    ("W60_H80_N30", 60, 80, 30),
    ("W65_H80_N30", 65, 80, 30),
)


def eligible(row, rule):
    _, min_wilson, min_hit, min_n = rule
    w = numeric(row.get("V3WilsonLower"))
    h = numeric(row.get("V3HistoricalHitRate"))
    n = numeric(row.get("V3SimilarMatches"))
    return (w is not None and h is not None and n is not None
            and w >= min_wilson and h >= min_hit and n >= min_n)


def aggregate(rows):
    ok = sum(r["V3Result"] == "OK" for r in rows)
    ko = len(rows) - ok
    return ok, ko


def pct(ok, ko):
    return round(100 * ok / (ok + ko), 2) if ok + ko else None


def write(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, delimiter=";", fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[WRITE] {path}: {len(rows)} righe")


def run():
    v2, v3 = load(V2), load(V3)
    common = sorted(v2.keys() & v3.keys())
    promotions = []
    for key in common:
        a, b = v2[key], v3[key]
        if a.get("Market") != "Over15" or b.get("Market") != "Over25":
            continue
        if a.get("Result") not in ("OK", "KO") or b.get("Result") not in ("OK", "KO"):
            continue
        if b["Result"] == "OK" and a["Result"] != "OK":
            raise ValueError(f"Impossible outcome: {key}")
        promotions.append({**dict(zip(KEY, key)),
                           "V2Engine": a.get("Engine", ""),
                           "V3Engine": b.get("Engine", ""),
                           "V2Result": a["Result"], "V3Result": b["Result"],
                           "V3Score": b.get("Score", ""),
                           "V3Band": b.get("Band", ""),
                           "V3SimilarMatches": b.get("SimilarMatches", ""),
                           "V3HistoricalHitRate": b.get("HistoricalHitRate", ""),
                           "V3WilsonLower": b.get("WilsonLower", "")})
    promotions.sort(key=lambda r: tuple(r[k] for k in KEY[1:2]) + tuple(r[k] for k in KEY))
    days = sorted({date.fromisoformat(r["MatchDate"]) for r in promotions})
    if len(days) < 3:
        raise ValueError("Insufficient distinct MatchDate values for chronological split")
    split_index = min(len(days)-1, max(1, int(len(days) * TRAIN_FRACTION)))
    cutoff = days[split_index]
    train = [r for r in promotions if date.fromisoformat(r["MatchDate"]) < cutoff]
    test = [r for r in promotions if date.fromisoformat(r["MatchDate"]) >= cutoff]
    if not train or not test:
        raise ValueError("Empty chronological train or test partition")

    train_candidates = []
    for rule in RULES:
        accepted = [r for r in train if eligible(r, rule)]
        ok, ko = aggregate(accepted)
        if len(accepted) < MIN_TRAIN_ACCEPTED:
            continue
        lower = wilson_lower(ok, len(accepted))
        # Prefer higher conservative hit rate; break ties by sample size.
        train_candidates.append((lower, len(accepted), rule))
    # If no threshold has enough observations, use ALL and report that.
    chosen = max(train_candidates, key=lambda x: (x[0], x[1], x[2][0]))[2] if train_candidates else RULES[0]
    for r in promotions:
        is_train = date.fromisoformat(r["MatchDate"]) < cutoff
        r["Split"] = "TRAIN" if is_train else "TEST"
        r["PromoteOver25"] = "YES" if eligible(r, chosen) else "NO"
        r["ChosenRule"] = chosen[0]
        # When rejected, preserve V2's Over15 rather than infer Over25.
        r["FinalMarket"] = "Over25" if r["PromoteOver25"] == "YES" else "Over15"
        r["FinalResult"] = r["V3Result"] if r["PromoteOver25"] == "YES" else r["V2Result"]
    write(DETAIL, (*KEY, "V2Engine", "V3Engine", "V2Result", "V3Result",
                   "V3Score", "V3Band", "V3SimilarMatches",
                   "V3HistoricalHitRate", "V3WilsonLower", "Split",
                   "PromoteOver25", "ChosenRule", "FinalMarket", "FinalResult"),
          promotions)

    summary = []
    for split, subset in (("TRAIN", train), ("TEST", test)):
        for rule in RULES:
            selected = [r for r in subset if eligible(r, rule)]
            ok, ko = aggregate(selected)
            summary.append({"Split": split, "Rule": rule[0], "Selected": int(rule == chosen),
                            "N": len(selected), "OK": ok, "KO": ko,
                            "Pct": pct(ok, ko),
                            "WilsonLower": round(100*wilson_lower(ok, len(selected)), 2) if selected else ""})
        chosen_rows = [r for r in subset if r["PromoteOver25"] == "YES"]
        rejected = [r for r in subset if r["PromoteOver25"] == "NO"]
        c_ok, c_ko = aggregate(chosen_rows)
        base_ok = sum(r["V2Result"] == "OK" for r in subset)
        final_ok = sum(r["FinalResult"] == "OK" for r in subset)
        print(f"[GM1-V3.2] {split}: total={len(subset)} accepted={len(chosen_rows)} "
              f"Over25_OK={c_ok} Over25_KO={c_ko} Over25_Pct={pct(c_ok,c_ko)} "
              f"rejected={len(rejected)}")
        print(f"[GM1-V3.2] {split}: V2_Over15_OK={base_ok}/{len(subset)} "
              f"HYBRID_OK={final_ok}/{len(subset)} "
              f"(different markets; not comparable as engine accuracy)")
    write(SUMMARY, ("Split", "Rule", "Selected", "N", "OK", "KO", "Pct", "WilsonLower"), summary)
    print(f"[GM1-V3.2] cutoff={cutoff} rule={chosen[0]} "
          f"train_days={split_index} test_days={len(days)-split_index}")
    print("[NOTE] Threshold chosen exclusively on TRAIN; TEST is untouched by rule selection. "
          "Exploratory selection bias remains: original GM1 histories are walk-forward, "
          "but candidate rules were proposed after observing aggregate V3 outcomes.")


if __name__ == "__main__":
    run()
