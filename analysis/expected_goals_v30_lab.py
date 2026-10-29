"""Compare frozen EG/min_ga rule against V30-derived filters (research only).

Run: python -m analysis.expected_goals_v30_lab
Never selects thresholds from the holdout; reports holdout only for fixed rules.
"""
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

from analysis.expected_goals_v2_lab import recent_features, summary
from gioover25.history import read_results_file
from gioover25.team_names import normalize_team_name


def main():
    base = {}
    with open("data/analysis/expected_goals_backtest.csv", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            try:
                league = r["LeagueId"]
                key = (league, r["MatchDate"],
                       normalize_team_name(league, r["Home"]),
                       normalize_team_name(league, r["Away"]))
                base[key] = (float(r["ExpectedGoals"].replace(",", ".")), int(r["Over25"]))
            except (ValueError, KeyError):
                continue

    rows = []
    for path in sorted(Path("data/storico/risultati").glob("*.csv")):
        league = path.stem
        try:
            feats = recent_features(read_results_file(path), league)
        except (OSError, ValueError) as e:
            print(f"[WARN] {path}: {e}")
            continue
        for (day, h, a), f in feats.items():
            pair = base.get((league, day, h, a))
            if pair is not None:
                eg, over = pair
                rows.append(dict(day=date.fromisoformat(day), league=league, eg=eg, over=over, **f))
    days = sorted({r["day"] for r in rows})
    if len(days) < 30:
        raise SystemExit("Insufficient distinct dates")
    cut1, cut2 = days[int(len(days) * .60)], days[int(len(days) * .80)]
    groups = [("TRAIN", [r for r in rows if r["day"] < cut1]),
              ("VALIDATION", [r for r in rows if cut1 <= r["day"] < cut2]),
              ("HOLDOUT", [r for r in rows if r["day"] >= cut2])]
    # Fixed hypotheses based on existing V30 criteria; no holdout optimization.
    rules = {
        "EG5_MIN_GA1.2": lambda r: r["eg"] >= 5 and r["min_ga"] >= 1.2,
        "PLUS_V30_MIN_OVER_0.6": lambda r: r["eg"] >= 5 and r["min_ga"] >= 1.2 and r["min_over"] >= .6,
        "PLUS_V30_MIN_OVER_0.8": lambda r: r["eg"] >= 5 and r["min_ga"] >= 1.2 and r["min_over"] >= .8,
        "PLUS_DELTA_GF_0.2": lambda r: r["eg"] >= 5 and r["min_ga"] >= 1.2 and r["delta_gf_l5"] >= .2,
        "PLUS_DELTA_GF_0.3": lambda r: r["eg"] >= 5 and r["min_ga"] >= 1.2 and r["delta_gf_l5"] >= .3,
        "PLUS_V30_CORE": lambda r: r["eg"] >= 5 and r["min_ga"] >= 1.2 and bool(r["v30_core"]),
        "PLUS_V30_STRONG": lambda r: r["eg"] >= 5 and r["min_ga"] >= 1.2 and bool(r["v30_strong"]),
        "PLUS_OVER_0.6_DELTA_0.2": lambda r: r["eg"] >= 5 and r["min_ga"] >= 1.2 and r["min_over"] >= .6 and r["delta_gf_l5"] >= .2,
        "PLUS_OVER_0.8_DELTA_0.2": lambda r: r["eg"] >= 5 and r["min_ga"] >= 1.2 and r["min_over"] >= .8 and r["delta_gf_l5"] >= .2,
    }
    output = Path("data/analysis/expected_goals_v30_comparison.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Rule", "Period", "OK", "KO", "Total", "Pct", "Australia"])
        for name, predicate in rules.items():
            for period, data in groups:
                for australia, subset in (
                    ("ALL", data),
                    ("EX_AUSTRALIA", [r for r in data if not r["league"].lower().startswith("australia_")]),
                ):
                    ok, ko, total, pct = summary([r for r in subset if predicate(r)])
                    w.writerow([name, period, ok, ko, total, pct, australia])
    print(f"Joined={len(rows)}; train before {cut1}; validation before {cut2}; holdout from {cut2}")
    print("HOLDOUT comparison (fixed hypotheses; not a new unseen test):")
    results = []
    for name, predicate in rules.items():
        ok, ko, n, pct = summary([r for r in groups[2][1] if predicate(r)])
        results.append((pct, n, name, ok, ko))
    for pct, n, name, ok, ko in sorted(results, reverse=True):
        print(f"{name}: OK={ok} KO={ko} Tot={n} %={pct:.2f}" + (" [SMALL SAMPLE]" if n < 30 else ""))
    print(f"CSV: {output}")
    print("CAUTION: holdout was already inspected in prior research. These comparisons are exploratory, not independent confirmation.")


if __name__ == "__main__":
    main()
