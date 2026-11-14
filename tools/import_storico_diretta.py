"""Import storico da feed risultati di una singola competizione Diretta/Flashscore.

Il feed della competizione (NON il feed giornaliero) va fornito esplicitamente
tramite --feed-file o --feed-url: nessun endpoint o ID viene indovinato.
L'output e' una proposta separata, mai lo storico ufficiale.
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

from tools.diretta_mobile import parse_feed
from gioover25.serie_d_registry import SERIE_D_GROUPS
from tools.prepare_input import ROOT, load_registry, resolve_match


FIELDS = ["LeagueId", "Round", "MatchDate", "Home", "Away", "HG", "AG", "Status", "Notes"]


def embedded_results(html: str) -> str:
    """Extract the server-rendered results feed from a Diretta competition page."""
    pattern = r"""cjs\\.initialFeeds\\[\\s*['"]results['"]\\s*\\]\\s*=\\s*\\{\\s*data\\s*:\\s*`([^`]*)`"""
    match = re.search(pattern, html, flags=re.S)
    if not match:
        raise ValueError("Feed cjs.initialFeeds['results'] non trovato nella pagina")
    payload = match.group(1)
    if "ZA÷" not in payload:
        raise ValueError("Feed results non valido: intestazione ZA assente")
    return payload


def extract(payload: str, registry, allowed: set[str], start: date, end: date):
    rows = {}
    rejected = Counter()
    for event in parse_feed(payload):
        lid = resolve_match(registry, event.country, event.league, event.home, event.away)
        if lid not in allowed:
            rejected["LEAGUE_UNMAPPED_OR_OUTSIDE_SELECTION"] += 1
            continue
        try:
            match_date = date.fromisoformat(event.match_date)
        except ValueError:
            rejected["MISSING_DATE"] += 1
            continue
        if not start <= match_date <= end:
            rejected["OUTSIDE_DATE_RANGE"] += 1
            continue
        score = re.fullmatch(r"(\d+)-(\d+)", event.score or "")
        if not score or event.status:
            rejected["NOT_CONFIRMED_FINAL"] += 1
            continue
        key = (lid, event.match_date, event.home, event.away)
        row = dict(zip(FIELDS, [lid, "", event.match_date, event.home, event.away,
                                score.group(1), score.group(2), "Finale", ""]))
        if key in rows and rows[key] != row:
            raise ValueError(f"Risultati discordanti per {key}")
        rows[key] = row
    return sorted(rows.values(), key=lambda x: (x["MatchDate"], x["LeagueId"], x["Home"], x["Away"])), rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--girone", choices=list(SERIE_D_GROUPS), help="Scarica la pagina risultati del girone Serie D")
    source.add_argument("--feed-file", type=Path, help="Feed della competizione salvato localmente")
    source.add_argument("--feed-url", help="URL completo del feed risultati della competizione, verificato manualmente")
    parser.add_argument("--league-id", action="append", help="LeagueId consentito (ripetibile)")
    parser.add_argument("--from-date", required=True, type=date.fromisoformat)
    parser.add_argument("--to-date", required=True, type=date.fromisoformat)
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "debug" / "storico_diretta_proposta.csv")
    parser.add_argument("--write", action="store_true", help="Scrive soltanto il CSV di proposta")
    args = parser.parse_args()
    if args.from_date > args.to_date:
        parser.error("--from-date successiva a --to-date")
    registry = load_registry(ROOT / "data" / "league_registry.csv")
    known = {r.league_id for r in registry}
    allowed = {SERIE_D_GROUPS[args.girone].league_id} if args.girone else set(args.league_id or [])
    if not allowed:
        parser.error("Specificare --league-id oppure --girone")
    if not allowed <= known:
        parser.error(f"LeagueId sconosciuti: {sorted(allowed - known)}")
    if args.girone:
        url = SERIE_D_GROUPS[args.girone].source_url
        request = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "it-IT,it;q=0.9"})
        with urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", errors="replace")
        payload = embedded_results(html)
        print(f"[STORICO] Pagina {url} | feed incorporato {len(payload)} caratteri")
        print("[STORICO][NOTA] Il feed incorporato potrebbe essere paginato: non garantisce ancora tutta la stagione")
    elif args.feed_file:
        payload = args.feed_file.read_text(encoding="utf-8-sig")
    else:
        if not args.feed_url.startswith("https://"):
            parser.error("--feed-url richiede HTTPS")
        request = Request(args.feed_url, headers={
            "User-Agent": "Mozilla/5.0", "Accept": "*/*",
            "Referer": "https://www.diretta.it/",
            "x-fsign": "SW9D1eZo",
        })
        with urlopen(request, timeout=30) as response:
            payload = response.read().decode("utf-8", errors="replace")
    rows, rejected = extract(payload, registry, allowed, args.from_date, args.to_date)
    for lid, count in sorted(Counter(row["LeagueId"] for row in rows).items()):
        print(f"[STORICO] {lid}: {count} risultati")
    print(f"[STORICO] Totale: {len(rows)} | esclusi: {dict(rejected)}")
    if not rows:
        print("[STORICO][WARN] Nessun risultato valido: output non modificato")
        return
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS, delimiter=";", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        print(f"[STORICO] Proposta scritta: {args.output}")
    else:
        print("[DRY-RUN] Nessun file modificato. Aggiungere --write per esportare la proposta.")


if __name__ == "__main__":
    main()
