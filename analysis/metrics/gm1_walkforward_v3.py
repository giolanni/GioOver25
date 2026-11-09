"""GM1-V3: engine-specific similarity profiles, strict chronological backtest.

No engine changes. V30/V31 are excluded until their autonomous scoring
features are represented faithfully in the pre-match dataset.
Run: python -m analysis.metrics.gm1_walkforward_v3
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict, deque
from pathlib import Path

from .gm1_walkforward_v2 import (
    KEY, DATASET, V20_DRIVERS, DRIVERS, SCALE, MIN_SIMILAR,
    NEIGHBORS, HISTORY_WINDOW, distance, market, numeric, read_dataset,
    read_drivers, wilson_lower,
)

OUT = Path("data/analysis/gm1_walkforward_v3_selections.csv")
COMPARE = Path("data/analysis/gm1_v2_v3_comparison.csv")
PROFILES = Path("data/analysis/gm1_v3_profiles.csv")
EXCLUDED = {"v30": "AUTONOMOUS_FEATURES_NOT_IN_DATASET",
            "v31": "AUTONOMOUS_FEATURES_NOT_IN_DATASET"}
BASE_V20 = {"v1", "v13", "v20", "v20plus", "v20select",
            "v20def", "v20defselect", "v20defplus",
            "v20defplus_v2", "v20defplus_v3"}
BASE_V25 = {"v25", "v251", "v25def", "v26", "v26def"}
# Context features are separate from the original score components.
CONTEXT = {
    "v25": ("HomePPG", "AwayPPG", "HomePlayed", "AwayPlayed"),
    "v251": ("HomePPG", "AwayPPG", "HomePlayed", "AwayPlayed"),
    "v25def": ("HomePPG", "AwayPPG", "HomePlayed", "AwayPlayed", "AwayGALast5"),
    "v26": ("HomePPG", "AwayPPG", "HomePlayed", "AwayPlayed"),
    "v26def": ("HomePPG", "AwayPPG", "HomePlayed", "AwayPlayed", "AwayGALast5"),
    "v27": ("AwayGALast5",),
}
SCALES = {**SCALE, "HomePlayed": 20.0, "AwayPlayed": 20.0,
          "HomeGALast5": 3.0, "AwayGALast5": 3.0}
OUTPUT_FIELDS = (*KEY, "Engine", "Band", "Score", "Market", "Result",
                 "SimilarMatches", "HistoricalHitRate", "WilsonLower",
                 "AvailableHistory", "DriverSet", "ProfileStatus")


def profiles(selected):
    result = {}
    for engine, detected in selected.items():
        if engine in EXCLUDED:
            result[engine] = ((), "EXCLUDED_" + EXCLUDED[engine])
            continue
        if engine in BASE_V20:
            base = V20_DRIVERS
        else:
            # Other engines use historically populated score components;
            # the profile remains experimental, not source-certified.
            base = tuple(f for f in detected if f in DRIVERS)
        context = CONTEXT.get(engine, ())
        fields = tuple(dict.fromkeys((*base, *context)))
        result[engine] = (fields, "EXPERIMENTAL")
    return result


def feature(engine, key, row, values, fields):
    raw = values.get((engine, key), {})
    vec = []
    for field in fields:
        val = numeric(row.get(field)) if field not in DRIVERS else raw.get(field)
        if val is None:
            return None
        vec.append(val / SCALES[field])
    return tuple(vec) if vec else None


def report(label, rows):
    for m in ("Over25", "Over15"):
        subset = [r for r in rows if r["Market"] == m]
        ok = sum(r["Result"] == "OK" for r in subset)
        ko = sum(r["Result"] == "KO" for r in subset)
        print(f"[{label}] {m}: OK={ok} KO={ko} Tot={ok+ko} "
              f"Pct={100*ok/(ok+ko):.2f}%" if ok+ko else
              f"[{label}] {m}: Tot=0")


def compare(picks):
    v2 = Path("data/analysis/gm1_walkforward_v2_selections.csv")
    if not v2.exists():
        print("[GM1-V3] Confronto V2 non disponibile: eseguire gm1_walkforward_v2")
        return
    with v2.open(encoding="utf-8-sig", newline="") as f:
        older = {tuple(r[k] for k in KEY): r for r in csv.DictReader(f, delimiter=";")}
    newer = {tuple(r[k] for k in KEY): r for r in picks}
    common = sorted(older.keys() & newer.keys())
    rows = []
    for key in common:
        a, b = older[key], newer[key]
        rows.append({**dict(zip(KEY, key)), "V2Engine": a["Engine"],
                     "V3Engine": b["Engine"], "V2Market": a["Market"],
                     "V3Market": b["Market"], "V2Result": a["Result"],
                     "V3Result": b["Result"], "SameEngine": int(a["Engine"] == b["Engine"]),
                     "SameMarket": int(a["Market"] == b["Market"])})
    fields = (*KEY, "V2Engine", "V3Engine", "V2Market", "V3Market",
              "V2Result", "V3Result", "SameEngine", "SameMarket")
    with COMPARE.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        w.writeheader()
        w.writerows(rows)
    print(f"[WRITE] {COMPARE}: {len(rows)} righe")
    print(f"[GM1-V3] common={len(common)} v2_only={len(older)-len(common)} "
          f"v3_only={len(newer)-len(common)}")
    for m in ("Over25", "Over15"):
        same = [r for r in rows if r["SameMarket"] and r["V3Market"] == m]
        print(f"[GM1-V3] common_same_market_{m}={len(same)}")
        report("GM1-V2-COMMON", [{"Market": m, "Result": r["V2Result"]} for r in same])
        report("GM1-V3-COMMON", [{"Market": m, "Result": r["V3Result"]} for r in same])


def run():
    fixtures = read_dataset()
    values, selected = read_drivers(fixtures)
    profile = profiles(selected)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with PROFILES.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=("Engine", "DriverSet", "Status"), delimiter=";")
        w.writeheader()
        w.writerows({"Engine": e, "DriverSet": ",".join(fields), "Status": status}
                    for e, (fields, status) in sorted(profile.items()))
    print(f"[WRITE] {PROFILES}: {len(profile)} righe")
    ordered = sorted(fixtures.items(), key=lambda item: (item[1]["day"], item[0]))
    history = defaultdict(lambda: deque(maxlen=HISTORY_WINDOW))
    stats = Counter()
    picks = []
    i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and ordered[j][1]["day"] == ordered[i][1]["day"]:
            j += 1
        for key, fixture in ordered[i:j]:
            candidates = []
            for engine, row in fixture["rows"].items():
                fields, status = profile[engine]
                if not fields:
                    stats["excluded"] += 1
                    continue
                m = market(row.get("Band"))
                if m is None:
                    continue
                vec = feature(engine, key, row, values, fields)
                if vec is None:
                    stats["missing_vector"] += 1
                    continue
                nearest = sorted(
                    ((distance(vec, old_vec), prior) for old_vec, prior in history[engine]
                     if market(prior.get("Band")) == m),
                    key=lambda item: item[0])[:NEIGHBORS]
                outcomes = [prior[m] == "OK" for _, prior in nearest
                            if prior.get(m) in ("OK", "KO")]
                n = len(outcomes)
                if n < MIN_SIMILAR:
                    continue
                ok = sum(outcomes)
                candidates.append((wilson_lower(ok, n), ok/n, n,
                                   engine, row, m, len(history[engine]), fields, status))
            if not candidates:
                stats["abstained"] += 1
                continue
            lower, hit, n, engine, row, m, count, fields, status = max(
                candidates, key=lambda x: (x[0], x[2], x[3]))
            if row.get(m) not in ("OK", "KO"):
                stats["invalid_outcome"] += 1
                continue
            picks.append({**dict(zip(KEY, key)), "Engine": engine,
                          "Band": row.get("Band", ""), "Score": row.get("Score", ""),
                          "Market": m, "Result": row[m], "SimilarMatches": n,
                          "HistoricalHitRate": round(hit*100, 2),
                          "WilsonLower": round(lower*100, 2),
                          "AvailableHistory": count, "DriverSet": ",".join(fields),
                          "ProfileStatus": status})
        # Never add same-day outcomes until all predictions for that date are made.
        for key, fixture in ordered[i:j]:
            for engine, row in fixture["rows"].items():
                fields, _ = profile[engine]
                if fields:
                    vec = feature(engine, key, row, values, fields)
                    if vec is not None:
                        history[engine].append((vec, row))
        i = j
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, delimiter=";")
        w.writeheader()
        w.writerows(picks)
    print(f"[WRITE] {OUT}: {len(picks)} righe")
    print(f"[GM1-V3] fixtures={len(fixtures)} excluded={stats['excluded']} "
          f"missing_vector={stats['missing_vector']} abstained={stats['abstained']}")
    report("GM1-V3", picks)
    compare(picks)
    print("[NOTE] V3 sperimentale. V30/V31 esclusi finche' non saranno "
          "disponibili tutti i loro driver prepartita. Nessun engine modificato.")


if __name__ == "__main__":
    run()
