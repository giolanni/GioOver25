from __future__ import annotations

import argparse
import math
from itertools import combinations
from pathlib import Path
from statistics import mean

from analysis.experiments.match_history_features import build_feature_rows, write_csv

OUTPUT_DEFAULT = Path("analysis/experiments/output/goal_feature_backtest")
WINDOWS = ("Full", "L5", "L7", "L8")


def btts_rate(rows):
    return sum(int(r["BTTS"]) for r in rows) / len(rows) * 100 if rows else 0.0


def point_biserial(rows, field):
    xs = [float(r[field]) for r in rows]
    ys = [int(r["BTTS"]) for r in rows]
    if not xs or len(set(ys)) < 2:
        return 0.0
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(
        sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)
    )
    return num / den if den else 0.0


def add_combined(rows):
    """Feature semplici e interpretabili, tutte pre-match/anti-lookahead."""
    for r in rows:
        for suffix in WINDOWS:
            hgf = float(r[f"HomeGF{suffix}"])
            agf = float(r[f"AwayGF{suffix}"])
            hga = float(r[f"HomeGA{suffix}"])
            aga = float(r[f"AwayGA{suffix}"])
            hb = float(r[f"HomeBTTSRate{suffix}"])
            ab = float(r[f"AwayBTTSRate{suffix}"])
            ho = float(r[f"HomeOverRate{suffix}"])
            ao = float(r[f"AwayOverRate{suffix}"])
            hppg = float(r[f"HomePPG{suffix}"])
            appg = float(r[f"AwayPPG{suffix}"])

            r[f"MinGF{suffix}"] = min(hgf, agf)
            r[f"AvgGF{suffix}"] = mean((hgf, agf))
            r[f"MinGA{suffix}"] = min(hga, aga)
            r[f"AvgGA{suffix}"] = mean((hga, aga))
            r[f"MinBTTSRate{suffix}"] = min(hb, ab)
            r[f"AvgBTTSRate{suffix}"] = mean((hb, ab))
            r[f"MinOverRate{suffix}"] = min(ho, ao)
            r[f"AvgOverRate{suffix}"] = mean((ho, ao))
            r[f"GoalBalance{suffix}"] = mean((hgf, agf, hga, aga))
            r[f"PPGGap{suffix}"] = abs(hppg - appg)

        # Recency del profilo GOAL/offensivo: non sono gate, ma possibili booster.
        r["DeltaBTTSL5"] = float(r["AvgBTTSRateL5"]) - float(r["AvgBTTSRateFull"])
        r["DeltaGFL5"] = float(r["AvgGFL5"]) - float(r["AvgGFFull"])
        r["DeltaGAL5"] = float(r["AvgGAL5"]) - float(r["AvgGAFull"])
        r["DeltaOverL5"] = float(r["AvgOverRateL5"]) - float(r["AvgOverRateFull"])


def candidate_conditions():
    """Ampia griglia: anche piccoli lift vengono conservati, non solo i top signal."""
    conds = []

    def add(name, field, op, threshold):
        if op == ">=":
            pred = lambda r, f=field, t=threshold: float(r[f]) >= t
        else:
            pred = lambda r, f=field, t=threshold: float(r[f]) <= t
        conds.append((name, pred))

    for s in WINDOWS:
        for t in (0.8, 1.0, 1.2, 1.4, 1.6, 1.8):
            add(f"MinGF{s}>={t}", f"MinGF{s}", ">=", t)
        for t in (0.6, 0.8, 1.0, 1.2, 1.4):
            add(f"MinGA{s}>={t}", f"MinGA{s}", ">=", t)
        for t in (0.8, 1.0, 1.2, 1.4, 1.6):
            add(f"AvgGA{s}>={t}", f"AvgGA{s}", ">=", t)
        for t in (0.40, 0.50, 0.60, 0.70, 0.80):
            add(f"MinBTTS{s}>={t}", f"MinBTTSRate{s}", ">=", t)
            add(f"AvgBTTS{s}>={t}", f"AvgBTTSRate{s}", ">=", t)
        for t in (0.40, 0.50, 0.60, 0.70, 0.80):
            add(f"MinOver{s}>={t}", f"MinOverRate{s}", ">=", t)
        for t in (0.5, 1.0, 1.5, 2.0):
            add(f"PPGGap{s}<={t}", f"PPGGap{s}", "<=", t)

    for field in ("DeltaBTTSL5", "DeltaGFL5", "DeltaGAL5", "DeltaOverL5"):
        for t in (0.0, 0.10, 0.20, 0.30):
            add(f"{field}>={t}", field, ">=", t)

    return conds


def evaluate(rows, name, pred, baseline, min_n):
    selected = [r for r in rows if pred(r)]
    if len(selected) < min_n:
        return None
    ok = sum(int(r["BTTS"]) for r in selected)
    rate = ok / len(selected) * 100
    return {
        "Rule": name,
        "N": len(selected),
        "GOAL": ok,
        "NO_GOAL": len(selected) - ok,
        "BTTSRate": round(rate, 2),
        "CoveragePct": round(len(selected) / len(rows) * 100, 2),
        "LiftVsBaseline": round(rate - baseline, 2),
    }


def discover_rules(rows, min_n=40, pair_pool=80):
    """Single + coppie di condizioni. Non elimina i lift piccoli positivi."""
    baseline = btts_rate(rows)
    conditions = candidate_conditions()
    singles = []
    for name, pred in conditions:
        result = evaluate(rows, name, pred, baseline, min_n)
        if result is not None:
            singles.append((result, pred))

    # Per limitare il costo quadratico, le coppie partono dalle condizioni single
    # con miglior compromesso lift/N; non richiediamo un lift minimo.
    singles.sort(
        key=lambda x: (x[0]["LiftVsBaseline"], math.log1p(x[0]["N"])),
        reverse=True,
    )
    pool = singles[:pair_pool]
    pairs = []
    for (a, pa), (b, pb) in combinations(pool, 2):
        name = f"{a['Rule']} AND {b['Rule']}"
        result = evaluate(
            rows,
            name,
            lambda r, x=pa, y=pb: x(r) and y(r),
            baseline,
            min_n,
        )
        if result is not None:
            pairs.append(result)

    single_rows = [x[0] for x in singles]
    all_rules = single_rows + pairs
    all_rules.sort(key=lambda r: (-r["BTTSRate"], -r["N"]))
    return single_rows, pairs, all_rules


def temporal_validation(rows, rules, test_days=60, min_test_n=10):
    """Valida le regole già scoperte su una coda temporale separata."""
    dates = sorted({r["MatchDate"] for r in rows})
    if not dates:
        return []
    latest = dates[-1]
    from datetime import date, timedelta
    cutoff = (date.fromisoformat(latest) - timedelta(days=test_days - 1)).isoformat()
    train = [r for r in rows if r["MatchDate"] < cutoff]
    test = [r for r in rows if r["MatchDate"] >= cutoff]
    if not train or not test:
        return []

    # Ricostruiamo i predicati dal nome evitando di serializzare lambda.
    cond_map = {name: pred for name, pred in candidate_conditions()}
    out = []
    train_base, test_base = btts_rate(train), btts_rate(test)
    for rule in rules:
        parts = rule["Rule"].split(" AND ")
        if any(p not in cond_map for p in parts):
            continue
        pred = lambda r, ps=parts: all(cond_map[p](r) for p in ps)
        tr = [r for r in train if pred(r)]
        te = [r for r in test if pred(r)]
        if len(te) < min_test_n or not tr:
            continue
        tr_rate, te_rate = btts_rate(tr), btts_rate(te)
        out.append({
            "Rule": rule["Rule"],
            "TrainN": len(tr), "TrainBTTSRate": round(tr_rate, 2),
            "TrainLift": round(tr_rate - train_base, 2),
            "TestN": len(te), "TestBTTSRate": round(te_rate, 2),
            "TestLift": round(te_rate - test_base, 2),
            "StablePositive": "YES" if tr_rate > train_base and te_rate > test_base else "NO",
        })
    out.sort(key=lambda r: (r["StablePositive"] != "YES", -r["TestLift"], -r["TestN"]))
    return out


def feature_scan(rows):
    fields = []
    for s in WINDOWS:
        fields += [
            f"MinGF{s}", f"AvgGF{s}", f"MinGA{s}", f"AvgGA{s}",
            f"MinBTTSRate{s}", f"AvgBTTSRate{s}", f"MinOverRate{s}",
            f"AvgOverRate{s}", f"GoalBalance{s}", f"PPGGap{s}",
        ]
    fields += ["DeltaBTTSL5", "DeltaGFL5", "DeltaGAL5", "DeltaOverL5"]
    return [
        {"Feature": f, "PointBiserial": round(point_biserial(rows, f), 5)}
        for f in sorted(fields, key=lambda x: abs(point_biserial(rows, x)), reverse=True)
    ]


def main():
    parser = argparse.ArgumentParser(
        description="Laboratorio GOAL/BTTS orientato alla selezione di segnali scommettibili."
    )
    parser.add_argument("--output-dir", default=str(OUTPUT_DEFAULT))
    parser.add_argument("--min-history", type=int, default=5)
    parser.add_argument("--min-n", type=int, default=40)
    parser.add_argument("--pair-pool", type=int, default=80)
    parser.add_argument("--test-days", type=int, default=60)
    args = parser.parse_args()

    rows = build_feature_rows(min_history=args.min_history, windows=(5, 7, 8))
    if not rows:
        raise RuntimeError("Nessuna partita storica eleggibile.")
    add_combined(rows)

    singles, pairs, rules = discover_rules(rows, args.min_n, args.pair_pool)
    validation = temporal_validation(rows, rules, args.test_days)
    correlations = feature_scan(rows)

    out = Path(args.output_dir)
    write_csv(out / "goal_single_signals.csv", singles)
    write_csv(out / "goal_pair_signals.csv", pairs)
    write_csv(out / "goal_all_signals.csv", rules)
    write_csv(out / "goal_temporal_validation.csv", validation)
    write_csv(out / "goal_feature_correlations.csv", correlations)
    write_csv(out / "goal_dataset.csv", rows)

    baseline = btts_rate(rows)
    print(f"Partite eleggibili: {len(rows)} | GOAL baseline: {baseline:.2f}%")
    print("\nMigliori segnali complessivi:")
    for r in rules[:20]:
        print(
            f"  {r['Rule']}: {r['GOAL']}/{r['N']} = {r['BTTSRate']}% "
            f"| lift {r['LiftVsBaseline']:+.2f} | coverage {r['CoveragePct']}%"
        )
    print("\nMigliori segnali temporalmente positivi:")
    stable = [r for r in validation if r["StablePositive"] == "YES"]
    for r in stable[:20]:
        print(
            f"  {r['Rule']}: train {r['TrainBTTSRate']}% ({r['TrainN']}) "
            f"| test {r['TestBTTSRate']}% ({r['TestN']}) "
            f"| test lift {r['TestLift']:+.2f}"
        )
    print("Output:", out)


if __name__ == "__main__":
    main()
