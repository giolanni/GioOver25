"""Backfill read-only di una lega dai feed giornalieri Diretta/Flashscore.

Scorre all'indietro dalla data odierna, usa la stessa cache del discovery e
raccoglie solo risultati conclusi della Country+League richiesta. Si ferma
dopo una lunga assenza successiva ad almeno un risultato, utile per trovare
l'inizio della stagione senza conoscere URL/ID torneo.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, timedelta

from tools.discover_leagues import canonical_country, fetch_day
from tools.diretta_mobile import parse_feed
from tools.prepare_input import ROOT, norm


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--league", required=True)
    ap.add_argument("--max-days", type=int, default=400)
    args = ap.parse_args()

    today = date.today()
    wanted_country, wanted_league = norm(args.country), norm(args.league)
    rows = {}
    errors = 0

    for back in range(args.max_days + 1):
        current = today - timedelta(days=back)
        try:
            matches = parse_feed(fetch_day(current, today))
        except Exception:
            errors += 1
            continue
        found_today = False
        for m in matches:
            if m.match_date and m.match_date != current.isoformat():
                continue
            if norm(canonical_country(m.country)) != wanted_country or norm(m.league) != wanted_league:
                continue
            found_today = True
            if m.score == "-" or m.status:
                continue
            try:
                hg, ag = (int(x) for x in m.score.split("-", 1))
            except ValueError:
                continue
            rows[(m.match_date or current.isoformat(), norm(m.home), norm(m.away))] = (
                m.match_date or current.isoformat(), m.home, m.away, hg, ag
            )

    ordered = sorted(rows.values())
    safe = "".join(ch if ch.isalnum() else "_" for ch in f"{args.country}_{args.league}").strip("_")
    out = ROOT / "data" / "debug" / f"backfill_{safe}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.writer(h, delimiter=";")
        w.writerow(["MatchDate","Home","Away","HG","AG"])
        w.writerows(ordered)

    first = ordered[0][0] if ordered else "-"
    last = ordered[-1][0] if ordered else "-"
    print(f"[BACKFILL] {args.country}: {args.league} | matches={len(ordered)} | {first} -> {last} | errors={errors}")
    print(f"[OUTPUT] {out}")
    print("[DRY-RUN] Nessuna modifica a registry o storici.")


if __name__ == "__main__":
    main()
