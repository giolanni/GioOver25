"""Rigenera esclusivamente i PDF usando dati già salvati, senza ricalcolare pronostici.

python -m tools.rigenera_pdf --tipo pronostici --data 2026-11-15
python -m tools.rigenera_pdf --tipo risultati --data 2026-11-14
"""
from __future__ import annotations
import argparse
from datetime import date
from pathlib import Path
from gioover25 import daily_report as dr
from gioover25.results_report import generate_results_report
from gioover25.engines.factory import get_available_engines

ROOT = Path(__file__).resolve().parents[1]


def predictions(day: date):
    day_str = day.isoformat()
    output = ROOT / "data/output_ranking"
    results = {}
    for engine in get_available_engines():
        rows = []
        for path in sorted((output / engine).glob("*.csv")):
            rows.extend(r for r in dr._read_csv(path) if r.get("MatchDate") == day_str)
        # If there are no current output rows, use the original archived predictions,
        # never calculate new ones with hindsight.
        if not rows:
            rows = [r for r in dr._history(engine)
                    if r.get("MatchDate") == day_str
                    and str(r.get("PredictionDate", "")) <= day_str]
        unique = {}
        for row in rows:
            key = (row.get("LeagueId"), row.get("MatchDate"), row.get("Home"), row.get("Away"))
            unique.setdefault(key, row)
        results[engine] = list(unique.values())
    gs1 = [r for r in dr._read_csv(ROOT / "data/storico/gs1_over/storico_gs1_over.csv")
           if r.get("MatchDate") == day_str]
    near = [r for r in dr._read_csv(ROOT / "data/storico/gs1_over/storico_gs1_over_near.csv")
            if r.get("MatchDate") == day_str]
    if not any(results.values()) and not gs1 and not near:
        raise SystemExit(f"Nessuna previsione salvata per {day_str}; PDF non generato")
    dr.generate_daily_report(results_by_engine=results, gs1_rows=gs1,
                             gs1_near_rows=near, report_date=day)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tipo", choices=["pronostici", "risultati"], required=True)
    parser.add_argument("--data", type=date.fromisoformat, required=True,
                        help="MatchDate in formato AAAA-MM-GG")
    args = parser.parse_args()
    if args.tipo == "risultati":
        generate_results_report(args.data)
    else:
        predictions(args.data)


if __name__ == "__main__":
    main()
