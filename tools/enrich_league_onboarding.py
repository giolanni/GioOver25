"""Arricchisce i candidati onboarding cercando il torneo su SofaScore.

Input: CSV prodotto da prepare_league_onboarding.py.
Output: CSV dry-run con identificativo torneo/URL quando il match web e' univoco.

La ricerca usa l'indice pubblico del sito SofaScore (DuckDuckGo HTML), non
inventa tournament id e non modifica registry/storici.
"""
from __future__ import annotations

import argparse
import csv
import html
import re
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from tools.prepare_input import ROOT, norm


@dataclass
class Hit:
    tournament_id: str
    url: str
    title: str
    score: int


COUNTRY_ALIASES = {
    "brasile": ("brazil", "brasile"),
    "cile": ("chile", "cile"),
    "cina": ("china", "cina"),
    "egitto": ("egypt", "egitto"),
    "grecia": ("greece", "grecia"),
    "irlanda": ("ireland", "irlanda"),
    "israele": ("israel", "israele"),
    "malesia": ("malaysia", "malesia"),
    "marocco": ("morocco", "marocco"),
    "sudafrica": ("south africa", "sudafrica"),
    "thailandia": ("thailand", "thailandia"),
}


def latest_onboarding() -> Path:
    files = sorted((ROOT / "data" / "debug").glob("league_onboarding_*.csv"))
    if not files:
        raise SystemExit("Nessun league_onboarding_*.csv trovato in data/debug")
    return files[-1]


def tokens(value: str) -> set[str]:
    return {x for x in re.split(r"[^a-z0-9]+", value.casefold()) if len(x) > 1}


def fetch_search(query: str) -> str:
    try:
        from curl_cffi import requests
    except ImportError as exc:
        raise SystemExit("Installa curl_cffi: pip install curl_cffi") from exc
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    response = requests.get(url, timeout=20, impersonate="chrome")
    response.raise_for_status()
    return response.text


def parse_hits(body: str, country: str, league: str) -> list[Hit]:
    # URL pubblico SofaScore: /football/tournament/<country>/<slug>/<id>
    rx = re.compile(
        r'href="(?P<url>https?://(?:www\.)?sofascore\.com/[^"]*?/football/tournament/[^"]+?/(?P<id>\d+))"[^>]*>(?P<title>.*?)</a>',
        re.I | re.S,
    )
    wanted = tokens(league)
    country_words = set()
    for alias in COUNTRY_ALIASES.get(norm(country), (country,)):
        country_words |= tokens(alias)
    out: dict[str, Hit] = {}
    for match in rx.finditer(body):
        title = re.sub(r"<[^>]+>", " ", html.unescape(match.group("title")))
        title = re.sub(r"\s+", " ", title).strip()
        hay = tokens(title + " " + html.unescape(match.group("url")))
        overlap = len(wanted & hay)
        country_ok = bool(country_words & hay)
        score = overlap * 10 + (5 if country_ok else 0)
        if overlap == 0:
            continue
        hit = Hit(match.group("id"), html.unescape(match.group("url")), title, score)
        old = out.get(hit.tournament_id)
        if old is None or hit.score > old.score:
            out[hit.tournament_id] = hit
    return sorted(out.values(), key=lambda x: (-x.score, x.tournament_id))


def discover(country: str, league: str) -> tuple[str, Hit | None, str]:
    # Query volutamente semplice: i motori ignorano spesso le query site:
    # troppo restrittive. Il parser accetta comunque esclusivamente URL
    # /football/tournament/... di sofascore.com.
    aliases = COUNTRY_ALIASES.get(norm(country), (country,))
    search_country = aliases[0]
    query = f'Sofascore {search_country} {league}'
    try:
        hits = parse_hits(fetch_search(query), country, league)
    except Exception as exc:
        return "ERROR", None, f"{exc.__class__.__name__}: {exc}"
    if not hits:
        return "NOT_FOUND", None, ""
    best = hits[0]
    tied = [x for x in hits if x.score == best.score]
    # Match automatico solo con copertura lessicale forte e senza pareggi.
    wanted_count = max(1, len(tokens(league)))
    if len(tied) == 1 and best.score >= max(15, wanted_count * 7):
        return "FOUND", best, ""
    return "AMBIGUOUS", best, f"hits={len(hits)} best_score={best.score}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Source discovery SofaScore per onboarding GioOver25.")
    parser.add_argument("--input", help="CSV onboarding; default ultimo in data/debug")
    parser.add_argument("--limit", type=int, default=0, help="Limita i READY da testare; 0=tutti")
    parser.add_argument("--output", help="CSV output")
    args = parser.parse_args()

    source = ROOT / args.input if args.input else latest_onboarding()
    with source.open(encoding="utf-8-sig", newline="") as handle:
        rows = [r for r in csv.DictReader(handle, delimiter=";") if r.get("Status") == "READY"]
    if args.limit > 0:
        rows = rows[:args.limit]

    output = ROOT / args.output if args.output else ROOT / "data" / "debug" / f"league_enrichment_{datetime.now():%Y%m%d-%H%M%S}.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}

    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        fields = list(rows[0].keys()) + ["SourceStatus", "SofaTournamentId", "SofaUrl", "SourceDetail"] if rows else []
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";")
        if fields:
            writer.writeheader()
        for index, row in enumerate(rows, 1):
            status, hit, detail = discover(row["Country"], row["League"])
            counts[status] = counts.get(status, 0) + 1
            row.update({
                "SourceStatus": status,
                "SofaTournamentId": hit.tournament_id if hit else "",
                "SofaUrl": hit.url if hit else "",
                "SourceDetail": detail,
            })
            writer.writerow(row)
            print(f"[{index}/{len(rows)}] {row['Country']};{row['League']} -> {status}" + (f" id={hit.tournament_id}" if hit else ""))

    print("[ENRICHMENT] " + " | ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"[ENRICHMENT] output={output}")
    print("[DRY-RUN] Nessuna modifica a league_registry.csv o agli storici.")


if __name__ == "__main__":
    main()
