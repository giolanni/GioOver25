"""Verifica storica Serie D A-I senza modificare gli storici ufficiali.

Esempio:
  python -m tools.import_storico_serie_d --from-date 2026-09-01 --to-date 2026-11-15
  python -m tools.import_storico_serie_d --from-date 2026-09-01 --to-date 2026-11-15 --write
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

from gioover25.serie_d_registry import SERIE_D_GROUPS
from tools.import_storico_diretta import FIELDS, embedded_results, extract
from tools.prepare_input import ROOT, load_registry


def summarize(rows):
    by_date = Counter(r["MatchDate"] for r in rows)
    if not rows:
        return "-", "-", 0, ""
    return (min(by_date), max(by_date), len(by_date),
            ", ".join(f"{day}:{count}" for day, count in sorted(by_date.items())))


def fetch_group(letter: str, registry, start: date, end: date):
    group = SERIE_D_GROUPS[letter]
    req = Request(group.source_url, headers={
        "User-Agent": "Mozilla/5.0", "Accept-Language": "it-IT,it;q=0.9",
    })
    with urlopen(req, timeout=30) as response:
        page = response.read().decode("utf-8", errors="replace")
    payload = embedded_results(page)
    if group.source_title not in payload:
        raise ValueError(f"Intestazione torneo inattesa: atteso {group.source_title}")
    rows, rejected = extract(payload, registry, {group.league_id}, start, end)
    return rows, rejected


def write_csv(path: Path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-date", type=date.fromisoformat, required=True)
    parser.add_argument("--to-date", type=date.fromisoformat, required=True)
    parser.add_argument("--gironi", default="ABCDEFGHI", help="Lettere da verificare, es. ABC")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "debug" / "storico_serie_d")
    parser.add_argument("--write", action="store_true", help="Esporta solo proposte e riepilogo")
    args = parser.parse_args()
    letters = args.gironi.upper()
    if not letters or len(set(letters)) != len(letters) or any(c not in SERIE_D_GROUPS for c in letters):
        parser.error("--gironi deve contenere lettere distinte da A a I")
    if args.from_date > args.to_date:
        parser.error("Intervallo date non valido")
    registry = load_registry(ROOT / "data" / "league_registry.csv")
    known = {r.league_id for r in registry}
    summary = []
    for letter in letters:
        group = SERIE_D_GROUPS[letter]
        print(f"\n[SERIE D] Girone {letter} | {group.source_url}")
        if group.league_id not in known:
            error = f"LeagueId assente nel registro: {group.league_id}"
            summary.append({"Girone": letter, "LeagueId": group.league_id, "Risultati": 0,
                            "PrimaData": "", "UltimaData": "", "DateDistinte": 0,
                            "Esclusi": "", "Stato": "ERRORE", "Dettaglio": error})
            print(f"[ERRORE] {error}")
            continue
        try:
            rows, rejected = fetch_group(letter, registry, args.from_date, args.to_date)
            first, last, days, distribution = summarize(rows)
            print(f"[SERIE D] {len(rows)} risultati | {days} date | prima={first} | ultima={last}")
            print(f"[SERIE D] Per data: {distribution or '-'}")
            print(f"[SERIE D] Esclusi: {dict(rejected)}")
            status = "OK" if rows else "VUOTO"
            summary.append({"Girone": letter, "LeagueId": group.league_id,
                            "Risultati": len(rows), "PrimaData": first, "UltimaData": last,
                            "DateDistinte": days, "Esclusi": str(dict(rejected)),
                            "Stato": status, "Dettaglio": ""})
            if args.write and rows:
                dest = args.output_dir / f"proposta_serie_d_girone_{letter.lower()}.csv"
                write_csv(dest, rows, FIELDS)
                print(f"[PROPOSTA] {dest}")
        except (OSError, ValueError, TimeoutError) as exc:
            print(f"[ERRORE] {type(exc).__name__}: {exc}")
            summary.append({"Girone": letter, "LeagueId": group.league_id, "Risultati": 0,
                            "PrimaData": "", "UltimaData": "", "DateDistinte": 0,
                            "Esclusi": "", "Stato": "ERRORE", "Dettaglio": str(exc)})
    print("\n[RIEPILOGO] " + " | ".join(f"{r['Girone']}={r['Risultati']}({r['Stato']})" for r in summary))
    print("[NOTA] Il feed incorporato potrebbe essere paginato: completezza stagionale non ancora verificata")
    if args.write:
        dest = args.output_dir / "riepilogo.csv"
        write_csv(dest, summary, ["Girone", "LeagueId", "Risultati", "PrimaData",
                                  "UltimaData", "DateDistinte", "Esclusi", "Stato", "Dettaglio"])
        print(f"[RIEPILOGO] {dest}")
    else:
        print("[DRY-RUN] Nessun CSV modificato")


if __name__ == "__main__":
    main()
