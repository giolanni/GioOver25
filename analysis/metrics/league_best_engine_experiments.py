"""Confronto walk-forward di varianti del selettore e baseline fisse.

Uso: python -m analysis.metrics.league_best_engine_experiments
     python -m analysis.metrics.league_best_engine_experiments --start 2026-08-01

Produce data/analysis/league_best_engine_experiments_{selections,summary,common}.csv
Nessuna modifica agli engine o ai ranking.
"""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import pandas as pd

from .league_best_engine import KEY, comparison, load_matches, write

OUT = Path("data/analysis")
STRATEGIES = {
    "DYNAMIC_20": (20, 0),
    "DYNAMIC_30": (30, 0),
    "DYNAMIC_30_75": (30, 75),
}
BASELINES = ("v20", "v24", "v25", "v26")


def run(matches: pd.DataFrame, start: date | None, end: date) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    matches = matches.loc[matches["MatchDate"] < pd.Timestamp(end)].copy()
    if matches.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    records = []
    for day in sorted(matches["MatchDate"].unique()):
        day = pd.Timestamp(day)
        if start and day < pd.Timestamp(start):
            continue
        today = matches.loc[matches["MatchDate"] == day]
        history = comparison(matches, day, 20)
        for name, (min_sample, min_rate) in STRATEGIES.items():
            eligible = history.loc[(history["Total"] >= min_sample) &
                                   (history["HitRate"] >= min_rate)]
            # Re-rank from scratch for each variant; never filter the 20-match choices.
            winners = eligible.drop_duplicates("LeagueId").set_index("LeagueId")
            for league, frame in today.groupby("LeagueId"):
                if league not in winners.index:
                    continue
                winner = winners.loc[league]
                for _, match in frame.loc[frame["Engine"] == winner["Engine"]].iterrows():
                    records.append({"Strategy": name, "Engine": winner["Engine"],
                                    "MatchDate": day.date().isoformat(),
                                    "LeagueId": league, "Home": match["Home"], "Away": match["Away"],
                                    "Over25": match["Over25"], "PriorTotal": int(winner["Total"]),
                                    "PriorHitRate": float(winner["HitRate"])})
        for engine in BASELINES:
            for _, match in today.loc[today["Engine"] == engine].iterrows():
                records.append({"Strategy": f"FIXED_{engine}", "Engine": engine,
                                "MatchDate": day.date().isoformat(),
                                "LeagueId": match["LeagueId"], "Home": match["Home"],
                                "Away": match["Away"], "Over25": match["Over25"],
                                "PriorTotal": "", "PriorHitRate": ""})
    selections = pd.DataFrame(records, columns=["Strategy", "Engine", "MatchDate",
                                                 "LeagueId", "Home", "Away", "Over25",
                                                 "PriorTotal", "PriorHitRate"])
    if selections.empty:
        return selections, pd.DataFrame(), pd.DataFrame()
    stats = selections.groupby("Strategy")["Over25"].agg(
        OK=lambda x: int((x == "OK").sum()),
        KO=lambda x: int((x == "KO").sum())).reset_index()
    stats["Total"] = stats["OK"] + stats["KO"]
    stats["HitRate"] = (100 * stats["OK"] / stats["Total"]).round(2)
    stats = stats.sort_values(["HitRate", "Total"], ascending=[False, False])
    # Paired comparison: for each dynamic strategy vs each fixed engine, only
    # matches predicted by BOTH. Different coverage is reported separately.
    paired = []
    for dynamic in STRATEGIES:
        a = selections.loc[selections["Strategy"] == dynamic, KEY + ["Over25"]]
        for engine in BASELINES:
            b = selections.loc[selections["Strategy"] == f"FIXED_{engine}", KEY + ["Over25"]]
            joined = a.merge(b, on=KEY, suffixes=("_Dynamic", "_Fixed"), validate="one_to_one")
            if joined.empty:
                continue
            paired.append({"Dynamic": dynamic, "Fixed": engine, "CommonMatches": len(joined),
                           "DynamicOK": int((joined["Over25_Dynamic"] == "OK").sum()),
                           "FixedOK": int((joined["Over25_Fixed"] == "OK").sum()),
                           "DynamicHitRate": round(100 * (joined["Over25_Dynamic"] == "OK").mean(), 2),
                           "FixedHitRate": round(100 * (joined["Over25_Fixed"] == "OK").mean(), 2),
                           "DifferentOutcomeRows": int((joined["Over25_Dynamic"] != joined["Over25_Fixed"]).sum())})
    common = pd.DataFrame(paired)
    return selections, stats, common


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    matches, _ = load_matches()
    selections, summary, common = run(matches, args.start, args.as_of)
    write(OUT / "league_best_engine_experiments_selections.csv", selections)
    write(OUT / "league_best_engine_experiments_summary.csv", summary)
    write(OUT / "league_best_engine_experiments_common.csv", common)
    if not summary.empty:
        print(summary.to_string(index=False))
    if not common.empty:
        print("\n[COMMON MATCHES]\n" + common.to_string(index=False))


if __name__ == "__main__":
    main()
