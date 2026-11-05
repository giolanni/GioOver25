"""GM1 walk-forward prototype: compare engines on historically similar fixtures.

No engine is modified. Only dates strictly earlier than the target date
can enter its historical neighbor pool. The same fixture is counted once.
Usage: python -m analysis.metrics.gm1_walkforward
"""
from __future__ import annotations
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

SOURCE = Path("data/analysis/gm1_pre_match_dataset.csv")
OUT = Path("data/analysis")
FEATURES = ("HomePlayed", "AwayPlayed", "HomePPG", "AwayPPG",
            "HomeGFLast5", "AwayGFLast5", "HomeGALast5", "AwayGALast5",
            "HomeOver25Last5", "AwayOver25Last5",
            "HomeBTTSLast5", "AwayBTTSLast5",
            "HomeVenueOver25", "AwayVenueOver25")
# Fixed scaling, independent of future observations; distances are not fitted on test data.
SCALES = (20, 20, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1)
WINDOW = 500
NEIGHBORS = 50
MIN_SIMILAR = 10
KEY = ("LeagueId", "MatchDate", "Home", "Away")
COLUMNS = (*KEY, "Engine", "Band", "Score", "SimilarMatches",
           "HistoricalHitRate", "Market", "Result", "NeighborPool")


def number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def vector(row):
    values = [number(row.get(k)) for k in FEATURES]
    if any(v is None for v in values):
        return None
    return tuple(v / scale for v, scale in zip(values, SCALES))


def distance(a, b):
    return sum((x-y)**2 for x, y in zip(a, b))


def read():
    fixtures = {}
    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            try:
                day = date.fromisoformat(r["MatchDate"])
            except ValueError:
                continue
            key = tuple(r[k] for k in KEY)
            entry = fixtures.setdefault(key, {"day": day, "rows": {},
                                               "vector": vector(r)})
            if entry["vector"] is None:
                entry["vector"] = vector(r)
            entry["rows"][r["Engine"]] = r
    return sorted(fixtures.items(), key=lambda x: (x[1]["day"], x[0]))


def market_for_band(band):
    band = (band or "").upper()
    # Preserve original band: IMM-/PROX- and suffixes are NOT silently promoted.
    if band == "ALTA":
        return "Over25", "Over25"
    if band == "MEDIA":
        return "Over15", "Over15"
    return None


def run():
    fixtures = read()
    past = []
    selections = []
    stats = defaultdict(lambda: [0, 0])
    eligible = 0
    i = 0
    while i < len(fixtures):
        day = fixtures[i][1]["day"]
        j = i
        while j < len(fixtures) and fixtures[j][1]["day"] == day:
            j += 1
        for key, entry in fixtures[i:j]:
            v = entry["vector"]
            if v is None:
                stats["missing_vector"][0] += 1
                continue
            ranked = sorted(
                ((distance(v, previous["vector"]), previous)
                 for previous in past if previous["vector"] is not None),
                key=lambda x: x[0],
            )[:NEIGHBORS]
            # Each candidate engine is judged on exactly the same neighbors.
            # Missing historical prediction is not a failure: count only eligible
            # predictions in the chosen market.
            candidates = []
            for engine, row in entry["rows"].items():
                market = market_for_band(row.get("Band"))
                if market is None:
                    continue
                eligible += 1
                outcome_field, label = market
                observations = [
                    old["rows"][engine][outcome_field] == "OK"
                    for _, old in ranked
                    if engine in old["rows"]
                    and market_for_band(old["rows"][engine].get("Band")) == market
                    and old["rows"][engine].get(outcome_field) in ("OK", "KO")
                ]
                if len(observations) < MIN_SIMILAR:
                    continue
                hits = sum(observations)
                candidates.append((hits / len(observations), len(observations),
                                   engine, row, label))
            if not candidates:
                stats["abstained"][0] += 1
                continue
            # Rank by empirical hit rate; prefer larger sample for ties.
            hit_rate, sample, engine, row, market = max(
                candidates, key=lambda c: (c[0], c[1], c[2]))
            outcome = row.get(market, "")
            if outcome not in ("OK", "KO"):
                stats["missing_outcome"][0] += 1
                continue
            stats[market][0] += 1
            stats[market][1] += outcome == "OK"
            stats["all"][0] += 1
            stats["all"][1] += outcome == "OK"
            selections.append(dict(zip(KEY, key), Engine=engine,
                                   Band=row["Band"], Score=row["Score"],
                                   SimilarMatches=sample,
                                   HistoricalHitRate=round(100*hit_rate, 2),
                                   Market=market, Result=outcome,
                                   NeighborPool=len(ranked)))
        # Update only AFTER all fixtures of this date have been evaluated.
        past.extend(entry for _, entry in fixtures[i:j])
        if len(past) > WINDOW:
            past = past[-WINDOW:]
        i = j
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "gm1_walkforward_selections.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, delimiter=";", fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(selections)
    print(f"[WRITE] {path}: {len(selections)} righe")
    print(f"[GM1] fixtures={len(fixtures)} eligible_candidates={eligible}")
    for market in ("Over25", "Over15", "all", "abstained", "missing_vector"):
        n, ok = stats[market]
        print(f"[GM1] {market}: OK={ok} KO={n-ok} Total={n} "
              f"Pct={100*ok/n:.2f}%" if n else f"[GM1] {market}: Total=0")
    print("[GM1] Sperimentale: nearest-neighbor e parametri NON ottimizzati; "
          "non è una validazione out-of-sample indipendente.")


if __name__ == "__main__":
    run()
