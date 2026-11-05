"""VEG90: independent experimental Over2.5 engine-like selection and immutable history.

Run AFTER the standard rankings:
    python -m analysis.veg90 --ranking data/output_ranking/v25/ranking_v25.csv
Or supply --ranking pointing to the day's ranking CSV with ExpectedGoals.
"""
import argparse
import csv
from datetime import date
from pathlib import Path
from gioover25.history import read_results_file
from gioover25.team_names import normalize_team_name

ROOT = Path("data")
HISTORY = ROOT / "storico" / "ranking" / "veg90" / "storico_ranking_veg90.csv"
OUTPUT = ROOT / "output_ranking" / "veg90"
FIELDS = ["LeagueId", "MatchDate", "Home", "Away", "ExpectedGoals",
          "MinGA", "MinOverL5", "Score", "Band", "AlgorithmVersion", "Status", "HG", "AG", "Outcome"]
VERSION = "VEG90-1.0"
def key(r):
    league = r["LeagueId"]
    return (league, r["MatchDate"], normalize_team_name(league, r["Home"]),
            normalize_team_name(league, r["Away"]))

def load(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))

def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def histories(league, cache):
    if league not in cache:
        p = ROOT / "storico" / "risultati" / (league + ".csv")
        cache[league] = read_results_file(p) if p.exists() else []
    return cache[league]

def drivers(league, day, home, away, cache):
    matches = histories(league, cache)
    hk = normalize_team_name(league, home)
    ak = normalize_team_name(league, away)
    def team_rows(name):
        result = []
        for m in matches:
            if m.date >= day:
                continue
            h = normalize_team_name(league, m.home)
            a = normalize_team_name(league, m.away)
            if name == h:
                result.append((m.date, m.home_goals, m.away_goals))
            elif name == a:
                result.append((m.date, m.away_goals, m.home_goals))
        return sorted(result, key=lambda x: x[0])[-5:]
    h, a = team_rows(hk), team_rows(ak)
    if len(h) < 5 or len(a) < 5:
        return None
    min_ga = min(sum(x[2] for x in h) / 5, sum(x[2] for x in a) / 5)
    min_over = min(sum(x[1] + x[2] >= 3 for x in h) / 5,
                   sum(x[1] + x[2] >= 3 for x in a) / 5)
    return min_ga, min_over

def results_map(leagues, cache):
    found = {}
    for league in leagues:
        for m in histories(league, cache):
            k = (league, m.date, normalize_team_name(league, m.home),
                 normalize_team_name(league, m.away))
            found[k] = (m.home_goals, m.away_goals)
    return found

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ranking", required=True, help="Existing ranking CSV containing ExpectedGoals")
    p.add_argument("--date", help="Only evaluate fixtures on YYYY-MM-DD (default: all rows in ranking)")
    args = p.parse_args()
    input_rows = load(Path(args.ranking))
    if not input_rows:
        raise SystemExit("Ranking CSV missing or empty")
    required = {"LeagueId", "MatchDate", "Home", "Away", "ExpectedGoals"}
    if not required.issubset(input_rows[0]):
        raise SystemExit("Missing ranking columns: " + str(sorted(required - set(input_rows[0]))))
    cache = {}
    candidates = []
    for r in input_rows:
        if args.date and r["MatchDate"] != args.date:
            continue
        try:
            eg = float(r["ExpectedGoals"].replace(",", "."))
        except (ValueError, AttributeError):
            continue
        if eg < 5:
            continue
        d = drivers(r["LeagueId"], r["MatchDate"], r["Home"], r["Away"], cache)
        if d is None or d[0] < 1.2 or d[1] < .8:
            continue
        candidates.append(dict(LeagueId=r["LeagueId"], MatchDate=r["MatchDate"],
                               Home=r["Home"], Away=r["Away"], ExpectedGoals=eg,
                               MinGA=round(d[0], 2), MinOverL5=round(d[1], 2),
                               Score=90, Band="ALTA", AlgorithmVersion=VERSION,
                               Status="SCHEDULED", HG="", AG="", Outcome=""))
    # Freeze selections. Re-running never adds a past prediction for a match
    # already played; this prevents backfilled predictions from contaminating forward stats.
    existing = {key(r): r for r in load(HISTORY)}
    known = results_map({r["LeagueId"] for r in candidates} | {r["LeagueId"] for r in existing.values()}, cache)
    added = 0
    for r in candidates:
        k = key(r)
        if k not in existing and k not in known and r["MatchDate"] >= date.today().isoformat():
            existing[k] = r
            added += 1
    for k, r in existing.items():
        if k in known:
            hg, ag = known[k]
            r.update(Status="FINISHED", HG=str(hg), AG=str(ag),
                     Outcome="OK" if hg + ag >= 3 else "KO")
    all_rows = sorted(existing.values(), key=lambda r: (r["MatchDate"], r["LeagueId"], r["Home"], r["Away"]))
    write(HISTORY, all_rows)
    today_rows = [r for r in all_rows if r["MatchDate"] == (args.date or date.today().isoformat())]
    write(OUTPUT / "ranking_veg90.csv", today_rows)
    done = [r for r in all_rows if r["Outcome"] in ("OK", "KO")]
    ok = sum(r["Outcome"] == "OK" for r in done)
    print(f"[VEG90] New={added}; history={len(all_rows)}; resolved={len(done)}; OK={ok} KO={len(done)-ok} Pct={100*ok/len(done):.2f}%" if done else
          f"[VEG90] New={added}; history={len(all_rows)}; no resolved predictions yet")
    print(f"[WRITE] {HISTORY}")
    print(f"[WRITE] {OUTPUT / 'ranking_veg90.csv'}")

if __name__ == "__main__":
    main()
