"""Diagnostica degli ID Diretta/Flashscore necessari al backfill.

Legge il feed gia' usato da GioOver25 e cerca una competizione in una finestra
di giorni. Non modifica registry o storici.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta

from tools.diretta_mobile import fetch_feed, parse_feed
from tools.prepare_input import norm


def main() -> None:
    parser = argparse.ArgumentParser(description="Mostra gli ID Flashscore di una competizione.")
    parser.add_argument("--country", required=True)
    parser.add_argument("--league", required=True)
    parser.add_argument("--days-before", type=int, default=7)
    parser.add_argument("--days-after", type=int, default=7)
    args = parser.parse_args()

    today = date.today()
    hits = []
    seen_matches = set()

    for offset in range(-args.days_before, args.days_after + 1):
        target = today + timedelta(days=offset)
        try:
            raw = parse_feed(fetch_feed(offset))
        except Exception as exc:
            print(f"[WARN] {target}: {exc.__class__.__name__}: {exc}")
            continue
        for match in raw:
            if norm(match.country) != norm(args.country) or norm(match.league) != norm(args.league):
                continue
            if match.match_id and match.match_id in seen_matches:
                continue
            if match.match_id:
                seen_matches.add(match.match_id)
            hits.append(match)

    print(f"[PROBE] {args.country};{args.league} -> {len(hits)} partite")
    if not hits:
        raise SystemExit("[PROBE] Competizione non trovata nella finestra richiesta.")

    tournament_ids = sorted({m.tournament_id for m in hits if m.tournament_id})
    stage_ids = sorted({m.tournament_stage_id for m in hits if m.tournament_stage_id})
    print(f"[PROBE] tournament_ids={tournament_ids or ['<assente>']}")
    print(f"[PROBE] stage_ids={stage_ids or ['<assente>']}")

    for m in hits[:10]:
        print(
            f"{m.match_date};{m.home};{m.away};{m.score};"
            f"AA={m.match_id or '-'};ZEE={m.tournament_id or '-'};"
            f"ZB={m.tournament_stage_id or '-'}"
        )

    print("[DRY-RUN] Nessuna modifica a registry o storici.")


if __name__ == "__main__":
    main()
