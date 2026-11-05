"""League Best Engine: confronto storico, affidabilita e backtest walk-forward.

python -m analysis.metrics.league_best_engine [--as-of YYYY-MM-DD] [--min-sample 20]
python -m analysis.metrics.league_best_engine --backtest [--backtest-start YYYY-MM-DD]

Non cambia gli engine; usa solo partite ALTA Over2.5 con MatchDate valida.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path
from collections import defaultdict

import pandas as pd

from .build_engine_league_high_rankings import detect_delimiter, find_engine_histories

REGISTRY = Path("data/league_registry.csv")
ROOT = Path("data/analysis")
DAILY = Path("data/output_ranking/daily_league_engine_selection.csv")
KEY = ["LeagueId", "MatchDate", "Home", "Away"]
COLUMNS = KEY + ["Engine", "Over25"]
DETAIL_COLUMNS = ["LeagueId", "Engine", "OK", "KO", "Total", "HitRate", "Eligible", "Reliability", "Rank"]
SUMMARY_COLUMNS = ["LeagueId", "AsOf", "Status", "BestEngine", "HitRate", "OK", "KO", "Total",
                   "Reliability"] + [f"Top{i}{suffix}" for i in range(1, 4) for suffix in ("Engine", "HitRate", "Total")]


def registry() -> list[str]:
    with REGISTRY.open(encoding="utf-8-sig", newline="") as stream:
        return sorted({r["LeagueId"].strip() for r in csv.DictReader(stream, delimiter=";")
                       if r.get("LeagueId", "").strip()})


def load_matches() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Deduplica su chiave partita + engine; esclude chiavi incomplete e conflitti OK/KO."""
    records = []
    rejected = []
    for engine, path in find_engine_histories():
        if engine.lower().startswith("vg"):
            continue  # BTTS separato
        with path.open(encoding="utf-8-sig", errors="replace", newline="") as stream:
            reader = csv.reader(stream, delimiter=detect_delimiter(path))
            first = next(reader, None)
            if not first:
                continue
            header = [v.strip() for v in first]
            if set(KEY + ["Band", "Over25"]).issubset(header):
                idx = {name: header.index(name) for name in KEY + ["Band", "Over25"]}
                rows = reader
            elif len(first) >= 14:
                # Layout legacy ufficiale: PredictionDate, MatchDate, LeagueId,
                # Round, Home, Away, ..., Band(7), ..., Over25(12)
                idx = {"MatchDate": 1, "LeagueId": 2, "Home": 4,
                       "Away": 5, "Band": 7, "Over25": 12}
                from itertools import chain
                rows = chain([first], reader)
            else:
                print(f"[SKIP] {engine}: intestazione non riconosciuta")
                continue
            for row in rows:
                if len(row) <= max(idx.values()):
                    continue
                d = {col: row[pos].strip() for col, pos in idx.items()}
                if d["Band"].upper() != "ALTA" or d["Over25"].upper() not in ("OK", "KO"):
                    continue
                dt = pd.to_datetime(d["MatchDate"], errors="coerce", dayfirst=True, format="mixed")
                if pd.isna(dt) or not all(d.get(k) for k in ("LeagueId", "Home", "Away")):
                    rejected.append({"Engine": engine, "Reason": "INVALID_KEY", **d})
                    continue
                records.append({"Engine": engine, "LeagueId": d["LeagueId"],
                                "MatchDate": dt.normalize(), "Home": d["Home"],
                                "Away": d["Away"], "Over25": d["Over25"].upper()})
    if not records:
        return pd.DataFrame(columns=COLUMNS), pd.DataFrame(rejected)
    raw = pd.DataFrame(records)
    # Non scegliere arbitrariamente un esito in caso di righe contraddittorie.
    group_key = ["Engine"] + KEY
    conflicts = raw.groupby(group_key)["Over25"].transform("nunique") > 1
    for d in raw.loc[conflicts].to_dict("records"):
        rejected.append({"Engine": d["Engine"], "Reason": "CONFLICTING_OUTCOME", **d})
    clean = raw.loc[~conflicts].drop_duplicates(subset=group_key).reset_index(drop=True)
    print(f"[DEDUP] raw={len(raw)} clean={len(clean)} rejected={int(conflicts.sum())} duplicates={len(raw)-int(conflicts.sum())-len(clean)}")
    return clean, pd.DataFrame(rejected)


def reliability(total: int, rate: float, min_sample: int) -> str:
    if total < min_sample:
        return "INSUFFICIENT"
    if total >= 30 and rate >= 80:
        return "HIGH"
    if rate >= 75:
        return "PROMISING"
    return "OBSERVATION"


def comparison(matches: pd.DataFrame, cutoff: pd.Timestamp, min_sample: int) -> pd.DataFrame:
    past = matches.loc[matches["MatchDate"] < cutoff]
    if past.empty:
        return pd.DataFrame(columns=DETAIL_COLUMNS)
    counts = past.groupby(["LeagueId", "Engine", "Over25"]).size().unstack(fill_value=0)
    for name in ("OK", "KO"):
        if name not in counts:
            counts[name] = 0
    result = counts.reset_index()[["LeagueId", "Engine", "OK", "KO"]]
    result["Total"] = result["OK"] + result["KO"]
    result["HitRate"] = (100 * result["OK"] / result["Total"]).round(2)
    result["Eligible"] = result["Total"] >= min_sample
    result["Reliability"] = [reliability(int(t), float(h), min_sample)
                             for t, h in zip(result["Total"], result["HitRate"])]
    result = result.sort_values(["LeagueId", "Eligible", "HitRate", "Total", "Engine"],
                                ascending=[True, False, False, False, True]).reset_index(drop=True)
    result["Rank"] = result.groupby("LeagueId").cumcount() + 1
    return result[DETAIL_COLUMNS]


def summary_for_leagues(details: pd.DataFrame, leagues: list[str], as_of: date) -> pd.DataFrame:
    by_league = {league: frame.loc[frame["Eligible"]].head(3)
                 for league, frame in details.groupby("LeagueId")}
    records = []
    for league in leagues:
        eligible = by_league.get(league)
        record = dict.fromkeys(SUMMARY_COLUMNS, "")
        record.update(LeagueId=league, AsOf=as_of.isoformat(), Status="INSUFFICIENT_DATA")
        if eligible is not None and not eligible.empty:
            record["Status"] = "READY"
            for n, (_, item) in enumerate(eligible.iterrows(), 1):
                record.update({f"Top{n}Engine": item["Engine"], f"Top{n}HitRate": item["HitRate"],
                               f"Top{n}Total": int(item["Total"])})
                if n == 1:
                    record.update(BestEngine=item["Engine"], HitRate=item["HitRate"],
                                  OK=int(item["OK"]), KO=int(item["KO"]), Total=int(item["Total"]),
                                  Reliability=item["Reliability"])
        records.append(record)
    return pd.DataFrame(records, columns=SUMMARY_COLUMNS)


def backtest(matches: pd.DataFrame, min_sample: int, start: date | None) -> pd.DataFrame:
    """Per ogni giornata sceglie l'engine sui soli giorni precedenti.
    Valuta solo incontri effettivamente pronosticati ALTA dall'engine selezionato.
    """
    results = []
    if matches.empty:
        return pd.DataFrame(columns=["MatchDate", "LeagueId", "Engine", "Home", "Away", "Over25",
                                     "PriorTotal", "PriorHitRate"])
    dates = sorted(matches["MatchDate"].unique())
    for day in dates:
        current_date = pd.Timestamp(day)
        if start and current_date < pd.Timestamp(start):
            continue
        today = matches.loc[matches["MatchDate"] == current_date]
        historical = comparison(matches, current_date, min_sample)
        if historical.empty:
            continue
        winners = historical.loc[historical["Eligible"]].drop_duplicates("LeagueId").set_index("LeagueId")
        for league, frame in today.groupby("LeagueId"):
            if league not in winners.index:
                continue
            chosen = winners.loc[league]
            selected = frame.loc[frame["Engine"] == chosen["Engine"]]
            for _, match in selected.iterrows():
                results.append({"MatchDate": current_date.date().isoformat(), "LeagueId": league,
                                "Engine": chosen["Engine"], "Home": match["Home"], "Away": match["Away"],
                                "Over25": match["Over25"], "PriorTotal": int(chosen["Total"]),
                                "PriorHitRate": float(chosen["HitRate"])})
    return pd.DataFrame(results, columns=["MatchDate", "LeagueId", "Engine", "Home", "Away",
                                          "Over25", "PriorTotal", "PriorHitRate"])


def write(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, sep=";", index=False, encoding="utf-8-sig")
    print(f"[WRITE] {path}: {len(frame)} righe")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--min-sample", type=int, default=20)
    parser.add_argument("--backtest", action="store_true")
    parser.add_argument("--backtest-start", type=date.fromisoformat)
    args = parser.parse_args()
    if args.min_sample < 1:
        parser.error("--min-sample deve essere >= 1")
    matches, rejected = load_matches()
    write(ROOT / "league_engine_rejected_rows.csv", rejected if not rejected.empty else
          pd.DataFrame(columns=["Engine", "Reason"] + KEY + ["Over25"]))
    details = comparison(matches, pd.Timestamp(args.as_of), args.min_sample)
    write(ROOT / "league_engine_comparison.csv", details)
    summary = summary_for_leagues(details, registry(), args.as_of)
    write(ROOT / "league_best_engine.csv", summary)
    # Il file daily contiene solo le leghe con incontri previsti oggi negli storici
    # (anche senza esito). Per il calendario reale usare --daily-input.
    write(DAILY, summary)
    print(f"[READY] {(summary['Status'] == 'READY').sum()}/{len(summary)} leghe")
    if args.backtest:
        bt = backtest(matches.loc[matches["MatchDate"] < pd.Timestamp(args.as_of)],
                      args.min_sample, args.backtest_start)
        write(ROOT / "league_best_engine_backtest.csv", bt)
        ok = int((bt["Over25"] == "OK").sum())
        print(f"[BACKTEST] OK={ok} KO={len(bt)-ok} Total={len(bt)} HitRate={100*ok/len(bt):.2f}%" if len(bt) else "[BACKTEST] Nessuna selezione valutabile")


if __name__ == "__main__":
    main()
