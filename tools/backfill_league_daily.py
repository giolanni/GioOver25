"""Backfill read-only della stagione corrente da pagina risultati Diretta.

Usa il feed stagionale incorporato nella pagina pubblica della competizione,
non il feed giornaliero. Non modifica registry o storici.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata

from tools.flashscore_history import fetch_embedded_results
from tools.prepare_input import ROOT


def slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().casefold()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--league", required=True)
    args = ap.parse_args()

    url = f"https://www.diretta.it/calcio/{slug(args.country)}/{slug(args.league)}/risultati/"
    try:
        ids, matches, payload = fetch_embedded_results(url)
    except Exception as exc:
        raise SystemExit(f"[ERROR] {url}: {type(exc).__name__}: {exc}")

    safe = "".join(ch if ch.isalnum() else "_" for ch in f"{args.country}_{args.league}").strip("_")
    out = ROOT / "data" / "debug" / f"backfill_{safe}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    matches.sort(key=lambda m: (m.date, int(m.round) if m.round.isdigit() else 9999, m.home, m.away))
    with out.open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.writer(h, delimiter=";")
        w.writerow(["Round","MatchDate","Home","Away","HG","AG","MatchId"])
        for m in matches:
            w.writerow([m.round, m.date, m.home, m.away, m.hg, m.ag, m.match_id])

    first = matches[0].date if matches else "-"
    last = matches[-1].date if matches else "-"
    print(f"[SOURCE] {url}")
    print(
        f"[IDS] template={ids.get('template_id') or '-'} | "
        f"tournament={ids.get('tournament_id') or '-'} | stage={ids.get('stage_id') or '-'}"
    )
    print(
        f"[BACKFILL] {args.country}: {args.league} | matches={len(matches)} | "
        f"{first} -> {last} | payload={len(payload)}"
    )
    print(f"[OUTPUT] {out}")
    print("[DRY-RUN] Nessuna modifica a registry o storici.")


if __name__ == "__main__":
    main()
