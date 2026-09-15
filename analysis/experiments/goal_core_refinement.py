from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from analysis.experiments.goal_feature_backtest import add_combined, btts_rate
from analysis.experiments.match_history_features import build_feature_rows, write_csv

OUTPUT_DEFAULT = Path("analysis/experiments/output/goal_core_refinement")


def enrich(rows):
    add_combined(rows)
    for r in rows:
        # Incrocio naturale: capacità di segnare di una squadra contro la
        # vulnerabilità difensiva dell'avversaria.
        for s in ("Full", "L5", "L7", "L8"):
            hgf = float(r[f"HomeGF{s}"])
            agf = float(r[f"AwayGF{s}"])
            hga = float(r[f"HomeGA{s}"])
            aga = float(r[f"AwayGA{s}"])
            r[f"HomeAttackVsAwayDef{s}"] = (hgf + aga) / 2.0
            r[f"AwayAttackVsHomeDef{s}"] = (agf + hga) / 2.0
            r[f"MinCrossGoal{s}"] = min(
                float(r[f"HomeAttackVsAwayDef{s}"]),
                float(r[f"AwayAttackVsHomeDef{s}"]),
            )
        r["Maturity"] = min(int(r["HomePlayedBefore"]), int(r["AwayPlayedBefore"]))


def core(row):
    return float(row["MinBTTSRateFull"]) >= 0.70 and float(row["MinGFL5"]) >= 1.80


def booster_conditions():
    out = []

    def ge(name, field, values):
        for t in values:
            out.append((f"{name}>={t}", lambda r, f=field, x=t: float(r[f]) >= x))

    def le(name, field, values):
        for t in values:
            out.append((f"{name}<={t}", lambda r, f=field, x=t: float(r[f]) <= x))

    for s in ("Full", "L5", "L7", "L8"):
        ge(f"MinCrossGoal{s}", f"MinCrossGoal{s}", (1.0, 1.2, 1.4, 1.6, 1.8))
        ge(f"MinGA{s}", f"MinGA{s}", (0.8, 1.0, 1.2, 1.4))
        ge(f"MinBTTS{s}", f"MinBTTSRate{s}", (0.5, 0.6, 0.7, 0.8))
        ge(f"MinOver{s}", f"MinOverRate{s}", (0.5, 0.6, 0.7, 0.8))
        le(f"PPGGap{s}", f"PPGGap{s}", (0.5, 0.75, 1.0, 1.5))

    ge("DeltaBTTSL5", "DeltaBTTSL5", (0.0, 0.1, 0.2))
    ge("DeltaGAL5", "DeltaGAL5", (0.0, 0.1, 0.2))
    ge("DeltaOverL5", "DeltaOverL5", (0.0, 0.1, 0.2))
    for t in (5, 7, 9, 13, 21):
        out.append((f"Maturity>={t}", lambda r, x=t: int(r["Maturity"]) >= x))
    return out


def evaluate_segment(rows, pred):
    selected = [r for r in rows if pred(r)]
    return len(selected), btts_rate(selected)


def temporal_boosters(core_rows, min_n=25, test_days=60):
    latest = max(date.fromisoformat(r["MatchDate"]) for r in core_rows)
    cutoff = latest - timedelta(days=test_days - 1)
    train = [r for r in core_rows if date.fromisoformat(r["MatchDate"]) < cutoff]
    test = [r for r in core_rows if date.fromisoformat(r["MatchDate"]) >= cutoff]
    train_base, test_base = btts_rate(train), btts_rate(test)
    results = []
    for name, pred in booster_conditions():
        tr_n, tr_rate = evaluate_segment(train, pred)
        te_n, te_rate = evaluate_segment(test, pred)
        if tr_n < min_n or te_n < max(10, min_n // 3):
            continue
        results.append({
            "Booster": name,
            "TrainN": tr_n,
            "TrainRate": round(tr_rate, 2),
            "TrainLiftVsCore": round(tr_rate - train_base, 2),
            "TestN": te_n,
            "TestRate": round(te_rate, 2),
            "TestLiftVsCore": round(te_rate - test_base, 2),
            "StablePositive": "YES" if tr_rate > train_base and te_rate > test_base else "NO",
        })
    results.sort(key=lambda r: (r["StablePositive"] != "YES", -r["TestLiftVsCore"], -r["TestN"]))
    return results, train_base, test_base


def league_analysis(core_rows, min_n=10):
    grouped = defaultdict(list)
    for r in core_rows:
        grouped[r["LeagueId"]].append(r)
    out = []
    overall = btts_rate(core_rows)
    for league, rs in grouped.items():
        if len(rs) < min_n:
            continue
        rate = btts_rate(rs)
        out.append({
            "LeagueId": league, "N": len(rs),
            "GOAL": sum(int(r["BTTS"]) for r in rs),
            "Rate": round(rate, 2), "LiftVsCore": round(rate - overall, 2),
        })
    out.sort(key=lambda r: (-r["Rate"], -r["N"]))
    return out


def maturity_analysis(core_rows):
    bands = ((5, 6), (7, 8), (9, 12), (13, 20), (21, 999))
    out = []
    overall = btts_rate(core_rows)
    for lo, hi in bands:
        rs = [r for r in core_rows if lo <= int(r["Maturity"]) <= hi]
        if not rs:
            continue
        rate = btts_rate(rs)
        out.append({
            "Band": f"{lo}-{hi if hi < 999 else '+'}", "N": len(rs),
            "GOAL": sum(int(r["BTTS"]) for r in rs), "Rate": round(rate, 2),
            "LiftVsCore": round(rate - overall, 2),
        })
    return out


def monthly_analysis(core_rows):
    grouped = defaultdict(list)
    for r in core_rows:
        grouped[r["MatchDate"][:7]].append(r)
    out = []
    for month in sorted(grouped):
        rs = grouped[month]
        out.append({
            "Month": month, "N": len(rs), "GOAL": sum(int(r["BTTS"]) for r in rs),
            "Rate": round(btts_rate(rs), 2),
        })
    return out


def main():
    p = argparse.ArgumentParser(description="Raffina il core GOAL stabile cercando piccoli booster scommettibili.")
    p.add_argument("--output-dir", default=str(OUTPUT_DEFAULT))
    p.add_argument("--min-history", type=int, default=5)
    p.add_argument("--min-n", type=int, default=25)
    p.add_argument("--test-days", type=int, default=60)
    args = p.parse_args()

    rows = build_feature_rows(min_history=args.min_history, windows=(5, 7, 8))
    enrich(rows)
    core_rows = [r for r in rows if core(r)]
    if not core_rows:
        raise RuntimeError("Nessuna partita nel core GOAL.")

    boosters, train_base, test_base = temporal_boosters(core_rows, args.min_n, args.test_days)
    leagues = league_analysis(core_rows)
    maturity = maturity_analysis(core_rows)
    monthly = monthly_analysis(core_rows)

    out = Path(args.output_dir)
    write_csv(out / "core_matches.csv", core_rows)
    write_csv(out / "booster_validation.csv", boosters)
    write_csv(out / "league_analysis.csv", leagues)
    write_csv(out / "maturity_analysis.csv", maturity)
    write_csv(out / "monthly_analysis.csv", monthly)

    print(f"CORE MinBTTSFull>=0.70 + MinGFL5>=1.80: {sum(int(r['BTTS']) for r in core_rows)}/{len(core_rows)} = {btts_rate(core_rows):.2f}%")
    print(f"Temporal core: train {train_base:.2f}% | test {test_base:.2f}%")
    print("\nBooster stabili (anche lift piccoli):")
    stable = [r for r in boosters if r["StablePositive"] == "YES"]
    for r in stable[:25]:
        print(f"  {r['Booster']}: train {r['TrainRate']}% N={r['TrainN']} ({r['TrainLiftVsCore']:+.2f}) | test {r['TestRate']}% N={r['TestN']} ({r['TestLiftVsCore']:+.2f})")
    print("\nMaturita:")
    for r in maturity:
        print(f"  {r['Band']}: {r['GOAL']}/{r['N']} = {r['Rate']}% | vs core {r['LiftVsCore']:+.2f}")
    print("\nMesi:")
    for r in monthly:
        print(f"  {r['Month']}: {r['GOAL']}/{r['N']} = {r['Rate']}%")
    print("Output:", out)


if __name__ == "__main__":
    main()
