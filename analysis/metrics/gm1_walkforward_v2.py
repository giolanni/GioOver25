"""GM1 v2: walk-forward con somiglianza specifica per engine.

Utilizza i driver storici prodotti dall'engine stesso, senza imporre
a v20 i driver di v25. Non modifica ranking o engine.
Esecuzione: python -m analysis.metrics.gm1_walkforward_v2
"""
from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict, deque
from datetime import date
from pathlib import Path

from .build_engine_league_high_rankings import detect_delimiter, find_engine_histories

DATASET = Path("data/analysis/gm1_pre_match_dataset.csv")
OUTPUT = Path("data/analysis/gm1_walkforward_v2_selections.csv")
KEY = ("LeagueId", "MatchDate", "Home", "Away")
DRIVERS = ("RankingGapScore", "HomeAttackScore", "AwayAttackScore",
           "HomeDefenseWeaknessScore", "AwayDefenseWeaknessScore",
           "HomeLast10OverScore", "AwayLast10OverScore",
           "HomeVenueOverScore", "AwayVenueOverScore", "BTTSProfileScore")
# V20: esattamente i cinque driver presenti in scoring_v2.py.
V20_DRIVERS = ("RankingGapScore", "HomeAttackScore",
               "AwayDefenseWeaknessScore", "HomeLast10OverScore",
               "AwayLast10OverScore")
# V25: eredita da V22; PPG usato nella penalita' contestuale.
V25_EXTRA = ("HomePPG", "AwayPPG")
SCALE = {k: 25.0 for k in DRIVERS}
SCALE.update({"RankingGapScore": 20.0, "HomeLast10OverScore": 15.0,
              "AwayLast10OverScore": 15.0,
              "HomePPG": 3.0, "AwayPPG": 3.0})
MIN_SIMILAR = 10
NEIGHBORS = 50
HISTORY_WINDOW = 500
FIELDS = (*KEY, "Engine", "Band", "Score", "Market", "Result",
          "SimilarMatches", "HistoricalHitRate", "WilsonLower",
          "AvailableHistory", "DriverSet")


def numeric(value):
    try:
        x = float(value)
        return x if math.isfinite(x) else None
    except (ValueError, TypeError):
        return None


def market(band):
    if band == "ALTA":
        return "Over25"
    if band == "MEDIA":
        return "Over15"
    return None


def wilson_lower(ok, n, z=1.96):
    p = ok / n
    d = 1 + z*z/n
    return (p + z*z/(2*n) - z*math.sqrt((p*(1-p)+z*z/(4*n))/n))/d


def read_dataset():
    fixtures = {}
    with DATASET.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream, delimiter=";"):
            try:
                day = date.fromisoformat(row["MatchDate"])
            except (ValueError, KeyError):
                continue
            key = tuple(row[k] for k in KEY)
            fixture = fixtures.setdefault(key, {"day": day, "rows": {}})
            fixture["rows"][row["Engine"]] = row
    return fixtures


def read_drivers(fixtures):
    # Preserve engine-specific driver values. Never interpret missing as zero.
    observed = defaultdict(Counter)
    values = {}
    for engine, path in find_engine_histories():
        if engine.lower().startswith("vg"):
            continue
        with path.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream, delimiter=detect_delimiter(path)):
                key = tuple((row.get(k) or "").strip() for k in KEY)
                if key not in fixtures or engine not in fixtures[key]["rows"]:
                    continue
                parsed = {d: numeric(row.get(d)) for d in DRIVERS}
                values[(engine, key)] = parsed
                for d, value in parsed.items():
                    if value is not None:
                        observed[engine][d] += 1
    # Driver sets are determined by engine definitions or historical presence,
    # never by outcomes. V20 is explicit, other engines use only sufficiently
    # populated drivers (>=95% of available historical predictions).
    selected = {}
    for engine in {e for f in fixtures.values() for e in f["rows"]}:
        if engine == "v20":
            selected[engine] = V20_DRIVERS
        elif engine == "v13":
            selected[engine] = V20_DRIVERS
        else:
            count = sum(engine in f["rows"] for f in fixtures.values())
            selected[engine] = tuple(
                d for d in DRIVERS if observed[engine][d] >= count * 0.95)
            if engine in ("v25", "v26", "v31"):
                selected[engine] += V25_EXTRA
        print(f"[GM1-V2] {engine}: {','.join(selected[engine]) or 'NESSUN_DRIVER'}")
    return values, selected


def vector(engine, key, row, values, selected):
    fields = selected[engine]
    if not fields:
        return None
    raw = values.get((engine, key), {})
    result = []
    for field in fields:
        val = numeric(row.get(field)) if field in V25_EXTRA else raw.get(field)
        if val is None:
            return None
        result.append(val / SCALE[field])
    return tuple(result)


def distance(a, b):
    return sum((x-y)*(x-y) for x, y in zip(a, b))


def run():
    fixtures = read_dataset()
    values, selected = read_drivers(fixtures)
    ordered = sorted(fixtures.items(), key=lambda pair: (pair[1]["day"], pair[0]))
    history = defaultdict(lambda: deque(maxlen=HISTORY_WINDOW))
    stats = defaultdict(lambda: [0, 0])
    picks = []
    i = 0
    while i < len(ordered):
        day = ordered[i][1]["day"]
        j = i
        while j < len(ordered) and ordered[j][1]["day"] == day:
            j += 1
        for key, fixture in ordered[i:j]:
            candidates = []
            for engine, row in fixture["rows"].items():
                target_market = market(row.get("Band"))
                if not target_market:
                    continue
                vec = vector(engine, key, row, values, selected)
                if vec is None:
                    stats["missing_driver"][0] += 1
                    continue
                pool = history[engine]
                closest = sorted(
                    ((distance(vec, v), prior) for v, prior in pool
                     if market(prior.get("Band")) == target_market),
                    key=lambda x: x[0])[:NEIGHBORS]
                observations = [prior[target_market] == "OK"
                                for _, prior in closest
                                if prior.get(target_market) in ("OK", "KO")]
                n = len(observations)
                if n < MIN_SIMILAR:
                    continue
                ok = sum(observations)
                candidates.append((wilson_lower(ok, n), ok/n, n,
                                   engine, row, target_market, len(pool)))
            if not candidates:
                stats["abstained"][0] += 1
                continue
            lower, hit, n, engine, row, target_market, pool_count = max(
                candidates, key=lambda x: (x[0], x[2], x[3]))
            outcome = row.get(target_market)
            if outcome not in ("OK", "KO"):
                stats["invalid_outcome"][0] += 1
                continue
            stats[target_market][0] += 1
            stats[target_market][1] += outcome == "OK"
            picks.append(dict(zip(KEY, key), Engine=engine,
                              Band=row.get("Band", ""), Score=row.get("Score", ""),
                              Market=target_market, Result=outcome,
                              SimilarMatches=n,
                              HistoricalHitRate=round(100*hit, 2),
                              WilsonLower=round(100*lower, 2),
                              AvailableHistory=pool_count,
                              DriverSet=",".join(selected[engine])))
        # Strictly older MatchDate: all same-day fixtures enter history together.
        for key, fixture in ordered[i:j]:
            for engine, row in fixture["rows"].items():
                vec = vector(engine, key, row, values, selected)
                if vec is not None:
                    history[engine].append((vec, row))
        i = j
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, delimiter=";", fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(picks)
    print(f"[WRITE] {OUTPUT}: {len(picks)} righe")
    print(f"[GM1-V2] unique_fixtures={len(fixtures)}")
    for label in ("Over25", "Over15", "abstained", "missing_driver"):
        n, ok = stats[label]
        print(f"[GM1-V2] {label}: OK={ok} KO={n-ok} Tot={n} "
              f"Pct={100*ok/n:.2f}%" if n else f"[GM1-V2] {label}: Tot=0")
    print("[GM1-V2] Esplorativo: mapping dei driver da validare per le varianti "
          "e confronti su identiche partite ancora necessari.")


if __name__ == "__main__":
    run()
