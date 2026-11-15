"""Statistiche Over 1.5 / Over 2.5 dei nove gironi Serie D, dagli archivi ufficiali.

Eseguire: python -m analysis.statistiche_serie_d_over
"""
from __future__ import annotations

from pathlib import Path
from gioover25.history import read_results_file

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/storico/risultati"


def main():
    records = []
    for letter in "ABCDEFGHI":
        league_id = f"Italy_SerieD_Girone{letter}"
        path = RESULTS / f"{league_id}.csv"
        if not path.is_file():
            print(f"[ATTENZIONE] Archivio mancante: {path}")
            continue
        matches = read_results_file(path)
        total = len(matches)
        over15 = sum(m.home_goals + m.away_goals >= 2 for m in matches)
        over25 = sum(m.home_goals + m.away_goals >= 3 for m in matches)
        records.append((letter, total, over15, over25))
    if not records:
        raise SystemExit("Nessuno storico Serie D trovato")
    print("Girone | Partite | Over 2.5 | Under 2.5 | Over 2.5 % | Over 1.5 | Over 1.5 %")
    print("-" * 88)
    for letter, total, over15, over25 in sorted(records, key=lambda r: (-r[3] / r[1] if r[1] else 0, r[0])):
        print(f"{letter:^6} | {total:>7} | {over25:>8} | {total-over25:>9} | {over25/total*100 if total else 0:>9.2f}% | {over15:>8} | {over15/total*100 if total else 0:>9.2f}%")
    total = sum(r[1] for r in records)
    over15 = sum(r[2] for r in records)
    over25 = sum(r[3] for r in records)
    print("-" * 88)
    print(f"{'TOTALE':^6} | {total:>7} | {over25:>8} | {total-over25:>9} | {over25/total*100:>9.2f}% | {over15:>8} | {over15/total*100:>9.2f}%")


if __name__ == "__main__":
    main()
