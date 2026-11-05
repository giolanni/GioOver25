"""GM1: dataset sperimentale di feature prepartita, senza leakage.

Uso: python -m analysis.metrics.gm1_build_dataset
Legge storici ranking e risultati, non li modifica. La prima versione
supporta le leghe con storico risultati diretto; CompetitionGroup e MLS Next
Pro sono esclusi esplicitamente fino alla ricostruzione multi-lega.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

from gioover25.team_names import normalize_team_name
from .build_engine_league_high_rankings import detect_delimiter, find_engine_histories

RESULTS = Path("data/storico/risultati")
REGISTRY = Path("data/league_registry.csv")
OUTPUT = Path("data/analysis/gm1_pre_match_dataset.csv")
KEY = ("LeagueId", "MatchDate", "Home", "Away")
FIELDS = (*KEY, "Engine", "Band", "Score", "Over25", "Over15",
          "HomePlayed", "AwayPlayed", "HomePPG", "AwayPPG",
          "HomeGFLast5", "AwayGFLast5", "HomeGALast5", "AwayGALast5",
          "HomeOver25Last5", "AwayOver25Last5",
          "HomeBTTSLast5", "AwayBTTSLast5", "HomeVenueOver25",
          "AwayVenueOver25", "SampleStatus")


def read_groups():
    with REGISTRY.open(encoding="utf-8-sig", newline="") as f:
        return {r["LeagueId"]: (r.get("CompetitionGroup") or "").strip()
                for r in csv.DictReader(f, delimiter=";")}


def load_results(league):
    path = RESULTS / f"{league}.csv"
    if not path.exists():
        return None
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            try:
                day = date.fromisoformat((row.get("MatchDate") or row.get("Date") or "").strip())
                hg, ag = int(row["HG"]), int(row["AG"])
                home = normalize_team_name(league, row["Home"])
                away = normalize_team_name(league, row["Away"])
            except (ValueError, KeyError, TypeError):
                continue
            rows.append((day, home, away, hg, ag))
    return sorted(set(rows))


def metrics(rows, team, day, venue):
    past = []
    for d, h, a, hg, ag in rows:
        if d >= day:
            break
        if team == h:
            past.append((d, hg, ag, True))
        elif team == a:
            past.append((d, ag, hg, False))
    n = len(past)
    points = sum(3 if gf > ga else 1 if gf == ga else 0 for _, gf, ga, _ in past)
    recent = past[-5:]
    def avg(index):
        return round(sum(row[index] for row in recent) / len(recent), 4) if recent else ""
    def rate(items, fn):
        return round(sum(fn(x) for x in items) / len(items), 4) if items else ""
    venue_past = [r for r in past if r[3] == venue]
    return {
        "Played": n,
        "PPG": round(points / n, 4) if n else "",
        "GFLast5": avg(1), "GALast5": avg(2),
        "Over25Last5": rate(recent, lambda r: r[1] + r[2] >= 3),
        "BTTSLast5": rate(recent, lambda r: r[1] > 0 and r[2] > 0),
        "VenueOver25": rate(venue_past, lambda r: r[1] + r[2] >= 3),
    }


def build(limit=None):
    groups = read_groups()
    cache = {}
    counts = defaultdict(int)
    seen = set()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, delimiter=";", fieldnames=FIELDS)
        writer.writeheader()
        for engine, path in find_engine_histories():
            if engine.lower().startswith("vg"):
                continue
            with path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream, delimiter=detect_delimiter(path))
                for r in reader:
                    if limit is not None and counts["written"] >= limit:
                        break
                    league = (r.get("LeagueId") or "").strip()
                    try:
                        day = date.fromisoformat((r.get("MatchDate") or "").strip())
                    except ValueError:
                        counts["invalid_date"] += 1
                        continue
                    home, away = (r.get("Home") or "").strip(), (r.get("Away") or "").strip()
                    if not league or not home or not away:
                        counts["invalid_key"] += 1
                        continue
                    outcome = (r.get("Over25") or "").strip().upper()
                    if outcome not in ("OK", "KO"):
                        counts["unresolved"] += 1
                        continue
                    key = (engine, league, day, normalize_team_name(league, home),
                           normalize_team_name(league, away))
                    if key in seen:
                        counts["duplicate"] += 1
                        continue
                    seen.add(key)
                    if groups.get(league) or league.startswith("USA_MLSNextPro_"):
                        counts["grouped_skipped"] += 1
                        continue
                    if league not in cache:
                        cache[league] = load_results(league)
                    rows = cache[league]
                    if rows is None:
                        counts["missing_results"] += 1
                        continue
                    hm = metrics(rows, key[3], day, True)
                    am = metrics(rows, key[4], day, False)
                    try:
                        hg, ag = int(r["HG"]), int(r["AG"])
                    except (ValueError, KeyError, TypeError):
                        counts["missing_goals"] += 1
                        continue
                    if (hg + ag >= 3) != (outcome == "OK"):
                        counts["outcome_conflict"] += 1
                        continue
                    record = {"LeagueId": league, "MatchDate": day.isoformat(),
                              "Home": home, "Away": away, "Engine": engine,
                              "Band": r.get("Band", ""), "Score": r.get("Score", ""),
                              "Over25": outcome, "Over15": "OK" if hg + ag >= 2 else "KO",
                              "SampleStatus": "READY" if hm["Played"] >= 5 and am["Played"] >= 5
                              else "IMMATURE"}
                    record.update({"Home" + k: v for k, v in hm.items()})
                    record.update({"Away" + k: v for k, v in am.items()})
                    writer.writerow(record)
                    counts["written"] += 1
            print(f"[GM1] {engine}: righe cumulative={counts['written']}")
            if limit is not None and counts["written"] >= limit:
                break
    print(f"[GM1] {OUTPUT}")
    for k, v in sorted(counts.items()):
        print(f"[GM1] {k}={v}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    build(args.limit)
