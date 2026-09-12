from __future__ import annotations

from collections import defaultdict
from datetime import date
from pathlib import Path

from analysis.experiments.match_history_features import build_feature_rows, write_csv

OUT = Path("analysis/experiments/output/v30_v31_full_backtest")


def enrich(row):
    maturity = int(row["MinPlayedBefore"])
    min_over = min(float(row["HomeOverRateL5"]), float(row["AwayOverRateL5"]))
    min_gf = min(float(row["HomeGFFull"]), float(row["AwayGFFull"]))
    avg_l5 = (float(row["HomeGFL5"]) + float(row["AwayGFL5"])) / 2.0
    avg_full = (float(row["HomeGFFull"]) + float(row["AwayGFFull"])) / 2.0
    delta = avg_l5 - avg_full
    young = 7 <= maturity <= 8

    v30 = young and min_over >= 0.70 and delta >= 0.20
    v31 = young and min_over >= 0.70 and min_gf >= 1.40

    if v31 and delta >= 0.30:
        level = "STRONG"
    elif v31 and delta >= 0.20:
        level = "BOOST"
    elif v31:
        level = "BASE"
    else:
        level = "NO-SIGNAL"

    row = dict(row)
    row.update({
        "Maturity": maturity,
        "MinOverL5": round(min_over, 6),
        "MinGFFull": round(min_gf, 6),
        "DeltaGFL5": round(delta, 6),
        "V30": int(v30),
        "V31": int(v31),
        "V31Level": level,
    })
    row["Relation"] = (
        "COMMON" if v30 and v31 else
        "V30_ONLY" if v30 else
        "V31_ONLY" if v31 else
        "NEITHER"
    )
    return row


def stats(rows):
    n = len(rows)
    ok = sum(int(r["Over25"]) for r in rows)
    return ok, n, (100.0 * ok / n if n else 0.0)


def item(scope, name, rows, **extra):
    ok, n, pct = stats(rows)
    out = {"Scope": scope, "Name": name, "OK": ok, "KO": n-ok, "N": n, "Rate": round(pct, 2)}
    out.update(extra)
    return out


def main():
    rows = [enrich(r) for r in build_feature_rows(min_history=5, windows=(5, 7, 8))]

    groups = {
        "V30": [r for r in rows if r["V30"]],
        "V31": [r for r in rows if r["V31"]],
        "V31_BASE": [r for r in rows if r["V31Level"] == "BASE"],
        "V31_BOOST": [r for r in rows if r["V31Level"] == "BOOST"],
        "V31_STRONG": [r for r in rows if r["V31Level"] == "STRONG"],
        "COMMON": [r for r in rows if r["Relation"] == "COMMON"],
        "V30_ONLY": [r for r in rows if r["Relation"] == "V30_ONLY"],
        "V31_ONLY": [r for r in rows if r["Relation"] == "V31_ONLY"],
    }

    print(f"Feature storiche disponibili: {len(rows)}")
    print(f"Maturita 7-8: {sum(7 <= int(r['Maturity']) <= 8 for r in rows)}")
    print("\nTOTALE")
    summary = []
    for name, selected in groups.items():
        ok, n, pct = stats(selected)
        print(f"{name:<12} {ok}/{n} = {pct:.2f}%")
        summary.append(item("TOTAL", name, selected))

    months = sorted({str(r["MatchDate"])[:7] for r in rows})
    monthly = []
    print("\nMESE PER MESE")
    for month in months:
        current = [r for r in rows if str(r["MatchDate"])[:7] == month]
        v30 = [r for r in current if r["V30"]]
        v31 = [r for r in current if r["V31"]]
        extra = [r for r in current if r["Relation"] == "V31_ONLY"]
        if not v30 and not v31:
            continue
        aok, an, ap = stats(v30)
        bok, bn, bp = stats(v31)
        eok, en, ep = stats(extra)
        print(f"{month}: V30 {aok}/{an}={ap:.1f}% | V31 {bok}/{bn}={bp:.1f}% | V31-only {eok}/{en}={ep:.1f}%")
        for name, selected in (("V30", v30), ("V31", v31), ("V31_ONLY", extra)):
            if selected:
                monthly.append(item("MONTH", name, selected, Month=month))

    league_rows = []
    leagues = defaultdict(list)
    for row in rows:
        leagues[row["LeagueId"]].append(row)
    for league_id, current in sorted(leagues.items()):
        for name, predicate in (
            ("V30", lambda r: r["V30"]),
            ("V31", lambda r: r["V31"]),
            ("V31_ONLY", lambda r: r["Relation"] == "V31_ONLY"),
        ):
            selected = [r for r in current if predicate(r)]
            if selected:
                league_rows.append(item("LEAGUE", name, selected, LeagueId=league_id))

    write_csv(OUT / "summary.csv", summary)
    write_csv(OUT / "monthly.csv", monthly)
    write_csv(OUT / "league.csv", league_rows)
    write_csv(OUT / "matches.csv", rows)

    print("\nOutput:", OUT)


if __name__ == "__main__":
    main()
