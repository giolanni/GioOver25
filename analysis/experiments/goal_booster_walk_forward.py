from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from analysis.experiments.goal_core_refinement import enrich, core
from analysis.experiments.goal_feature_backtest import btts_rate
from analysis.experiments.match_history_features import build_feature_rows, write_csv

OUTPUT_DEFAULT = Path("analysis/experiments/output/goal_booster_walk_forward")


def rules():
    return [
        ("CORE", lambda r: True),
        ("PPG1", lambda r: float(r["PPGGapFull"]) <= 1.0),
        ("PPG075", lambda r: float(r["PPGGapFull"]) <= 0.75),
        ("PPG05", lambda r: float(r["PPGGapFull"]) <= 0.50),
        ("DBTTS0", lambda r: float(r["DeltaBTTSL5"]) >= 0.0),
        ("OVER80", lambda r: float(r["MinOverRateFull"]) >= 0.80),
        ("PPG1_DBTTS0", lambda r: float(r["PPGGapFull"]) <= 1.0 and float(r["DeltaBTTSL5"]) >= 0.0),
        ("PPG1_OVER80", lambda r: float(r["PPGGapFull"]) <= 1.0 and float(r["MinOverRateFull"]) >= 0.80),
        ("DBTTS0_OVER80", lambda r: float(r["DeltaBTTSL5"]) >= 0.0 and float(r["MinOverRateFull"]) >= 0.80),
        ("PPG1_DBTTS0_OVER80", lambda r: float(r["PPGGapFull"]) <= 1.0 and float(r["DeltaBTTSL5"]) >= 0.0 and float(r["MinOverRateFull"]) >= 0.80),
        ("PPG075_DBTTS0", lambda r: float(r["PPGGapFull"]) <= 0.75 and float(r["DeltaBTTSL5"]) >= 0.0),
        ("PPG075_OVER80", lambda r: float(r["PPGGapFull"]) <= 0.75 and float(r["MinOverRateFull"]) >= 0.80),
        ("PPG05_DBTTS0", lambda r: float(r["PPGGapFull"]) <= 0.50 and float(r["DeltaBTTSL5"]) >= 0.0),
    ]


def main():
    p = argparse.ArgumentParser(description="Walk-forward mensile dei booster GOAL sul core stabile.")
    p.add_argument("--output-dir", default=str(OUTPUT_DEFAULT))
    p.add_argument("--min-history", type=int, default=5)
    args = p.parse_args()

    rows = build_feature_rows(min_history=args.min_history, windows=(5, 7, 8))
    enrich(rows)
    rows = [r for r in rows if core(r)]
    if not rows:
        raise RuntimeError("Nessuna partita nel core GOAL")

    months = defaultdict(list)
    for r in rows:
        months[r["MatchDate"][:7]].append(r)

    monthly = []
    summary = []
    core_rate = btts_rate(rows)
    for name, pred in rules():
        selected_all = [r for r in rows if pred(r)]
        positive_months = 0
        comparable_months = 0
        for month in sorted(months):
            base = months[month]
            selected = [r for r in base if pred(r)]
            if not selected:
                continue
            rate = btts_rate(selected)
            month_core = btts_rate(base)
            if name != "CORE":
                comparable_months += 1
                if rate > month_core:
                    positive_months += 1
            monthly.append({
                "Month": month, "Rule": name, "N": len(selected),
                "GOAL": sum(int(r["BTTS"]) for r in selected),
                "Rate": round(rate, 2), "CoreMonthRate": round(month_core, 2),
                "LiftVsCoreMonth": round(rate - month_core, 2),
            })
        rate_all = btts_rate(selected_all)
        summary.append({
            "Rule": name, "N": len(selected_all),
            "GOAL": sum(int(r["BTTS"]) for r in selected_all),
            "Rate": round(rate_all, 2), "LiftVsCore": round(rate_all - core_rate, 2),
            "PositiveMonths": positive_months,
            "ComparableMonths": comparable_months,
            "PositiveMonthPct": round(positive_months / comparable_months * 100, 2) if comparable_months else 0.0,
        })

    summary.sort(key=lambda r: (-r["Rate"], -r["N"]))
    out = Path(args.output_dir)
    write_csv(out / "summary.csv", summary)
    write_csv(out / "monthly.csv", monthly)

    print(f"CORE: {sum(int(r['BTTS']) for r in rows)}/{len(rows)} = {core_rate:.2f}%")
    print("\nConfronto booster:")
    for r in summary:
        print(f"  {r['Rule']}: {r['GOAL']}/{r['N']} = {r['Rate']}% | lift {r['LiftVsCore']:+.2f} | mesi migliori {r['PositiveMonths']}/{r['ComparableMonths']}")
    print("Output:", out)


if __name__ == "__main__":
    main()
