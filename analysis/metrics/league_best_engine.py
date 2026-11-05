"""Seleziona per ogni lega gli engine Over 2.5 migliori usando solo esiti precedenti alla data di calcolo.

Esecuzione: python -m analysis.metrics.league_best_engine [--as-of YYYY-MM-DD] [--min-sample 20]
Non modifica ranking o pronostici esistenti. VG/BTTS esclusi: mercato distinto.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from .build_engine_league_high_rankings import (
    detect_delimiter, find_engine_histories, load_history_columns,
)

REGISTRY = Path("data/league_registry.csv")
ANALYSIS_OUT = Path("data/analysis/league_best_engine.csv")
DAILY_OUT = Path("data/output_ranking/daily_league_engine_selection.csv")
DETAIL_OUT = Path("data/analysis/league_engine_comparison.csv")


def read_registry() -> list[str]:
    with REGISTRY.open(encoding="utf-8-sig", newline="") as handle:
        return sorted({row["LeagueId"].strip() for row in csv.DictReader(handle, delimiter=";")
                       if row.get("LeagueId", "").strip()})


def engine_stats(engine: str, path: Path, cutoff: pd.Timestamp) -> pd.DataFrame:
    # I file aggregati league_high_ranking non conservano le date di ciascun esito:
    # ricalcoliamo dagli stessi storici per garantire il taglio temporale.
    history, missing = load_history_columns(path, detect_delimiter(path))
    if missing or history.empty or "MatchDate" not in history.columns:
        print(f"[SKIP] {engine}: storico senza MatchDate o colonne richieste")
        return pd.DataFrame()
    for col in ("LeagueId", "Band", "Over25"):
        history[col] = history[col].fillna("").astype(str).str.strip()
    history["Band"] = history["Band"].str.upper()
    history["Over25"] = history["Over25"].str.upper()
    history["MatchDate"] = pd.to_datetime(history["MatchDate"], errors="coerce", format="mixed", dayfirst=True)
    history = history.loc[
        (history["MatchDate"] < cutoff)
        & (history["LeagueId"] != "")
        & (history["Band"] == "ALTA")
        & history["Over25"].isin(["OK", "KO"])
    ].copy()
    if history.empty:
        return pd.DataFrame()
    # Evita duplicati identici; una stessa partita con righe divergenti resta
    # esclusa dalla selezione solo se non è possibile identificarla qui.
    history = history.drop_duplicates()
    grouped = history.groupby("LeagueId")["Over25"].agg(
        OK=lambda x: int((x == "OK").sum()),
        KO=lambda x: int((x == "KO").sum()),
    ).reset_index()
    grouped["Total"] = grouped["OK"] + grouped["KO"]
    grouped["HitRate"] = (100 * grouped["OK"] / grouped["Total"]).round(2)
    grouped["Engine"] = engine
    return grouped


def build(as_of: date, min_sample: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    cutoff = pd.Timestamp(as_of)
    frames = []
    for engine, path in find_engine_histories():
        if engine.lower().startswith("vg"):
            continue  # VG1 e varianti sono BTTS, non confrontabili con Over 2.5
        frame = engine_stats(engine, path, cutoff)
        if not frame.empty:
            frames.append(frame)
    details = (pd.concat(frames, ignore_index=True) if frames else
               pd.DataFrame(columns=["LeagueId", "OK", "KO", "Total", "HitRate", "Engine"]))
    details["Eligible"] = details["Total"] >= min_sample
    details = details.sort_values(
        ["LeagueId", "Eligible", "HitRate", "Total", "Engine"],
        ascending=[True, False, False, False, True],
    ).reset_index(drop=True)
    details["Rank"] = details.groupby("LeagueId").cumcount() + 1

    output = []
    for league in read_registry():
        subset = details.loc[(details["LeagueId"] == league) & details["Eligible"]].head(3)
        record = {"LeagueId": league, "AsOf": as_of.isoformat(),
                  "Status": "READY" if not subset.empty else "INSUFFICIENT_DATA",
                  "BestEngine": "", "HitRate": "", "OK": "", "KO": "", "Total": ""}
        for rank, (_, item) in enumerate(subset.iterrows(), 1):
            record[f"Top{rank}Engine"] = item["Engine"]
            record[f"Top{rank}HitRate"] = item["HitRate"]
            record[f"Top{rank}Total"] = int(item["Total"])
            if rank == 1:
                record.update(BestEngine=item["Engine"], HitRate=item["HitRate"],
                              OK=int(item["OK"]), KO=int(item["KO"]), Total=int(item["Total"]))
        output.append(record)
    summary = pd.DataFrame(output)
    for rank in range(1, 4):
        for suffix in ("Engine", "HitRate", "Total"):
            col = f"Top{rank}{suffix}"
            if col not in summary:
                summary[col] = ""
    return summary, details


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today(),
                        help="Data del pronostico: usa esclusivamente MatchDate precedenti")
    parser.add_argument("--min-sample", type=int, default=20)
    args = parser.parse_args()
    if args.min_sample < 1:
        parser.error("--min-sample deve essere >= 1")
    summary, details = build(args.as_of, args.min_sample)
    for path, frame in ((ANALYSIS_OUT, summary), (DAILY_OUT, summary), (DETAIL_OUT, details)):
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, sep=";", index=False, encoding="utf-8-sig")
        print(f"[WRITE] {path}: {len(frame)} righe")
    print(f"[READY] {int((summary['Status'] == 'READY').sum())}/{len(summary)} leghe")


if __name__ == "__main__":
    main()
