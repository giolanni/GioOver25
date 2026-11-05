"""GM1 laboratorio V20: scoperta profili su TRAIN, verifica VALID/TEST.

Solo pronostici V20 con fascia ALTA e risultato Over25 risolto.
Nessuna modifica agli engine. Le soglie sono scelte esclusivamente su TRAIN.
Esecuzione: python -m analysis.metrics.gm1_v20_profiles
"""
from __future__ import annotations

import csv
import math
from collections import Counter
from datetime import date
from itertools import combinations
from pathlib import Path

from .build_engine_league_high_rankings import detect_delimiter, find_engine_histories

OUT = Path("data/analysis")
DRIVERS = ("RankingGapScore", "HomeAttackScore", "AwayDefenseWeaknessScore",
           "HomeLast10OverScore", "AwayLast10OverScore")
KEY = ("LeagueId", "MatchDate", "Home", "Away")
MIN_TRAIN = 30
MIN_VALID = 15
MAX_CONDITIONS = 2
QUANTILES = (0.25, 0.5, 0.75)
FIELDS = ("Profile", "Conditions", "Split", "OK", "KO", "Totale", "Perc",
          "CoveragePct", "BaselinePct", "WilsonLower", "TrainSupport")


def numeric(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def wilson(ok, n):
    if not n:
        return 0.0
    z = 1.96
    p = ok/n
    return (p+z*z/(2*n)-z*math.sqrt((p*(1-p)+z*z/(4*n))/n))/(1+z*z/n)


def load_v20():
    paths = [path for engine, path in find_engine_histories() if engine == "v20"]
    if len(paths) != 1:
        raise RuntimeError(f"Atteso un solo storico V20, trovati {len(paths)}")
    records = {}
    counters = Counter()
    with paths[0].open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=detect_delimiter(paths[0])):
            if (r.get("Band") or "").strip().upper() != "ALTA":
                continue
            if (r.get("Over25") or "").strip().upper() not in ("OK", "KO"):
                continue
            try:
                day = date.fromisoformat((r.get("MatchDate") or "").strip())
            except ValueError:
                counters["bad_date"] += 1
                continue
            key = tuple((r.get(k) or "").strip() for k in KEY)
            if not all(key):
                counters["bad_key"] += 1
                continue
            features = tuple(numeric(r.get(k)) for k in DRIVERS)
            if any(v is None for v in features):
                counters["missing_driver"] += 1
                continue
            if key in records:
                counters["duplicate"] += 1
                if records[key]["ok"] != (r["Over25"].strip().upper() == "OK"):
                    raise RuntimeError(f"Esiti V20 discordanti: {key}")
                continue
            records[key] = {"key": key, "day": day, "features": features,
                            "ok": r["Over25"].strip().upper() == "OK"}
    print(f"[V20] eligible={len(records)} exclusions={dict(counters)}")
    return sorted(records.values(), key=lambda r: (r["day"], r["key"]))


def split(records):
    days = sorted({r["day"] for r in records})
    if len(days) < 10:
        raise RuntimeError("Troppo poche date distinte per train/validation/test")
    a = days[max(1, int(len(days)*0.60))-1]
    b = days[max(2, int(len(days)*0.80))-1]
    if a >= b or b >= days[-1]:
        raise RuntimeError("Split cronologico non valido")
    result = {
        "TRAIN": [r for r in records if r["day"] <= a],
        "VALID": [r for r in records if a < r["day"] <= b],
        "TEST": [r for r in records if r["day"] > b],
    }
    print(f"[SPLIT] TRAIN<={a} VALID<={b} TEST>{b}")
    for name, rows in result.items():
        print(f"[{name}] {describe(rows)}")
    return result


def describe(rows):
    n = len(rows)
    ok = sum(r["ok"] for r in rows)
    return f"OK={ok} KO={n-ok} Tot={n} Pct={100*ok/n:.2f}%" if n else "Tot=0"


def candidates(train):
    # Candidate boundaries are calculated ONLY from training observations.
    thresholds = []
    for idx, name in enumerate(DRIVERS):
        ordered = sorted(r["features"][idx] for r in train)
        for q in QUANTILES:
            value = ordered[min(len(ordered)-1, int(q*(len(ordered)-1)))]
            for operator in (">=", "<="):
                thresholds.append((idx, name, operator, value))
    unique = {(idx, op, value): (idx, name, op, value)
              for idx, name, op, value in thresholds}
    singles = list(unique.values())
    for item in singles:
        yield (item,)
    if MAX_CONDITIONS >= 2:
        for left, right in combinations(singles, 2):
            if left[0] != right[0]:
                yield (left, right)


def matches(row, conditions):
    return all((row["features"][idx] >= value if op == ">="
                else row["features"][idx] <= value)
               for idx, _, op, value in conditions)


def label(conditions):
    return " & ".join(f"{name}{op}{value:.4g}" for _, name, op, value in conditions)


def score_profile(rows, conditions):
    selected = [r for r in rows if matches(r, conditions)]
    n = len(selected)
    ok = sum(r["ok"] for r in selected)
    return n, ok, wilson(ok, n)


def metrics(name, conditions, split_name, rows, train_support):
    n, ok, low = score_profile(rows, conditions)
    base_ok = sum(r["ok"] for r in rows)
    return {"Profile": name, "Conditions": label(conditions),
            "Split": split_name, "OK": ok, "KO": n-ok, "Totale": n,
            "Perc": round(100*ok/n, 2) if n else 0,
            "CoveragePct": round(100*n/len(rows), 2) if rows else 0,
            "BaselinePct": round(100*base_ok/len(rows), 2) if rows else 0,
            "WilsonLower": round(100*low, 2),
            "TrainSupport": train_support}


def run():
    records = load_v20()
    if not records:
        raise RuntimeError("Nessuna partita V20 ALTA con driver ed esito")
    splits = split(records)
    train, valid, test = (splits[k] for k in ("TRAIN", "VALID", "TEST"))
    baseline = wilson(sum(r["ok"] for r in train), len(train))
    ranked = []
    seen_masks = set()
    for conditions in candidates(train):
        # Remove equivalent filters; avoid selecting the same subset repeatedly.
        mask = tuple(i for i, r in enumerate(train) if matches(r, conditions))
        n = len(mask)
        if n < MIN_TRAIN or n == len(train) or mask in seen_masks:
            continue
        seen_masks.add(mask)
        ok = sum(train[i]["ok"] for i in mask)
        lower = wilson(ok, n)
        if lower <= baseline:
            continue
        ranked.append((lower, ok/n, n, conditions))
    ranked.sort(key=lambda x: (-x[0], -x[1], -x[2], label(x[3])))
    print(f"[SEARCH] candidates_qualified={len(ranked)} "
          f"baseline_train_wilson={100*baseline:.2f}%")
    # Freeze the highest-ranked profile based ONLY on training data.
    # VALID and TEST are inspected but NEVER used to choose a profile.
    chosen = ranked[0][3] if ranked else None
    rows = []
    for rank, (_, _, support, conditions) in enumerate(ranked[:20], 1):
        for part in ("TRAIN", "VALID", "TEST"):
            rows.append(metrics(f"TRAIN_RANK_{rank}", conditions,
                                part, splits[part], support))
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "gm1_v20_profile_report.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    print(f"[WRITE] {path}: {len(rows)} righe")
    if chosen is None:
        print("[RESULT] Nessun profilo supera il baseline Wilson sul TRAIN.")
        return
    print(f"[FROZEN_PROFILE] {label(chosen)}")
    for part in ("TRAIN", "VALID", "TEST"):
        selected = [r for r in splits[part] if matches(r, chosen)]
        print(f"[PROFILE {part}] {describe(selected)} "
              f"coverage={100*len(selected)/len(splits[part]):.2f}%")
    print("[NOTE] Studio retrospettivo esplorativo: anche il profilo congelato "
          "non costituisce una validazione prospettica. "
          "Non ottimizzare dopo aver visto TEST.")


if __name__ == "__main__":
    run()
