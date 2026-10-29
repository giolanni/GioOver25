"""ExpectedGoals v2 laboratory: read-only historical Over 2.5 filter experiments.

Run: python -m analysis.expected_goals_v2_lab
Uses local results and existing ExpectedGoals backtest; does not modify engines.
"""
import argparse
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

from gioover25.history import read_results_file
from gioover25.team_names import normalize_team_name


def number(value):
    return float(str(value).replace(",", "."))


def summary(rows):
    n = len(rows)
    ok = sum(r["over"] for r in rows)
    return (ok, n - ok, n, round(100 * ok / n, 2) if n else 0)


def recent_features(matches, league):
    """Only matches with strictly earlier MatchDate contribute to each feature."""
    ordered = sorted(matches, key=lambda m: m.date)
    history = defaultdict(list)
    features = {}
    i = 0
    while i < len(ordered):
        j = i
        while j < len(ordered) and ordered[j].date == ordered[i].date:
            j += 1
        for m in ordered[i:j]:
            h = normalize_team_name(league, m.home)
            a = normalize_team_name(league, m.away)
            home = history[h][-5:]
            away = history[a][-5:]
            if len(home) < 5 or len(away) < 5:
                continue
            def avg(rows, idx):
                return sum(x[idx] for x in rows) / len(rows)
            def over(rows):
                return sum(x[1] + x[2] >= 3 for x in rows) / len(rows)
            home_all = history[h]
            away_all = history[a]
            maturity = min(len(home_all), len(away_all))
            avg_gf_l5 = (avg(home, 1) + avg(away, 1)) / 2
            avg_gf_full = (avg(home_all, 1) + avg(away_all, 1)) / 2
            features[(m.date, h, a)] = {
                "maturity": maturity,
                "delta_gf_l5": avg_gf_l5 - avg_gf_full,
                "v30_core": int(7 <= maturity <= 8 and min(over(home), over(away)) >= .70 and avg_gf_l5 - avg_gf_full >= .20),
                "v30_strong": int(7 <= maturity <= 8 and min(over(home), over(away)) >= .70 and avg_gf_l5 - avg_gf_full >= .30),
                "min_gf": min(avg(home, 1), avg(away, 1)),
                "max_ga": max(avg(home, 2), avg(away, 2)),
                "min_ga": min(avg(home, 2), avg(away, 2)),
                "min_over": min(over(home), over(away)),
                "avg_over": (over(home) + over(away)) / 2,
                "sum_gf": avg(home, 1) + avg(away, 1),
                "sum_ga": avg(home, 2) + avg(away, 2),
            }
        for m in ordered[i:j]:
            h = normalize_team_name(league, m.home)
            a = normalize_team_name(league, m.away)
            history[h].append((m.date, m.home_goals, m.away_goals))
            history[a].append((m.date, m.away_goals, m.home_goals))
        i = j
    return features


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--backtest", default="data/analysis/expected_goals_backtest.csv")
    p.add_argument("--results-dir", default="data/storico/risultati")
    p.add_argument("--output", default="data/analysis/expected_goals_v2_candidates.csv")
    p.add_argument("--min-train", type=int, default=80)
    p.add_argument("--min-validation", type=int, default=30)
    p.add_argument("--min-test", type=int, default=30)
    args = p.parse_args()

    baseline = {}
    with open(args.backtest, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            try:
                key = (r["LeagueId"], r["MatchDate"],
                       normalize_team_name(r["LeagueId"], r["Home"]),
                       normalize_team_name(r["LeagueId"], r["Away"]))
                baseline[key] = (number(r["ExpectedGoals"]), int(r["Over25"]))
            except (ValueError, KeyError):
                continue

    rows = []
    for path in sorted(Path(args.results_dir).glob("*.csv")):
        league = path.stem
        try:
            matches = read_results_file(path)
            features = recent_features(matches, league)
        except (ValueError, OSError) as exc:
            print(f"[WARN] {path}: {exc}")
            continue
        for (day, home, away), f in features.items():
            value = baseline.get((league, day, home, away))
            if value is not None:
                eg, over = value
                rows.append(dict(day=date.fromisoformat(day), eg=eg,
                                 over=over, league=league, **f))

    if len(rows) < 300:
        raise SystemExit(f"Only {len(rows)} joined matches; check results and backtest.")
    days = sorted({r["day"] for r in rows})
    if len(days) < 30:
        raise SystemExit("Not enough distinct dates for chronological evaluation.")
    cut1 = days[int(len(days) * 0.60)]
    cut2 = days[int(len(days) * 0.80)]
    train = [r for r in rows if r["day"] < cut1]
    valid = [r for r in rows if cut1 <= r["day"] < cut2]
    test = [r for r in rows if r["day"] >= cut2]
    print(f"Joined={len(rows)}; train={len(train)} before {cut1}; "
          f"validation={len(valid)} before {cut2}; test={len(test)}")

    # Candidate features are already computed from past matches only.
    # No model fitting or threshold selection ever uses the test segment.
    rules = [("baseline", "eg", t, None, None)
             for t in (3.0, 3.5, 4.0, 4.5, 5.0)]
    specs = {
        "min_gf": (1.0, 1.5, 2.0, 2.5),
        "max_ga": (1.0, 1.5, 2.0, 2.5),
        "min_ga": (0.8, 1.2, 1.6, 2.0),
        "min_over": (0.4, 0.6, 0.8, 1.0),
        "avg_over": (0.5, 0.7, 0.9),
        "sum_gf": (2.5, 3.5, 4.5, 5.5),
        "sum_ga": (2.5, 3.5, 4.5, 5.5),
    }
    for eg in (3.0, 3.5, 4.0, 4.5, 5.0):
        for feature, thresholds in specs.items():
            for threshold in thresholds:
                rules.append(("single", "eg", eg, feature, threshold))

    def selected(data, rule):
        _, _, eg, feature, threshold = rule
        return [r for r in data if r["eg"] >= eg and
                (feature is None or r[feature] >= threshold)]

    candidates = []
    for rule in rules:
        a = summary(selected(train, rule))
        b = summary(selected(valid, rule))
        if a[2] >= args.min_train and b[2] >= args.min_validation:
            candidates.append((rule, a, b))
    candidates.sort(key=lambda item: (item[2][3], item[2][2]), reverse=True)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Rule", "EGMin", "Feature", "FeatureMin",
                         "TrainOK", "TrainKO", "TrainTot", "TrainPct",
                         "ValidationOK", "ValidationKO", "ValidationTot", "ValidationPct"])
        for rule, a, b in candidates:
            writer.writerow([rule[0], rule[2], rule[3] or "", rule[4] if rule[4] is not None else "",
                             *a, *b])
    print(f"Candidate rules: {len(candidates)}; CSV: {out}")
    if not candidates:
        return
    rule, a, b = candidates[0]
    c = summary(selected(test, rule))
    print(f"Best VALIDATION rule: EG >= {rule[2]}; {rule[3]} >= {rule[4]}")
    for label, stat in (("TRAIN", a), ("VALIDATION", b), ("UNSEEN TEST", c)):
        print(f"{label}: OK={stat[0]} KO={stat[1]} Tot={stat[2]} %={stat[3]:.2f}")
    if c[2] < args.min_test:
        print("TEST INCONCLUSIVE: insufficient selected matches.")
    else:
        print("TEST TARGET 90%:", "YES" if c[3] >= 90 else "NO")
    print("Exploratory analysis only: repeat on future dates before deployment.")


if __name__ == "__main__":
    main()
