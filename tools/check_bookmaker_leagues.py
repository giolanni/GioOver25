"""Verifica sui bookmaker pubblici le leghe NEW scoperte da discover_leagues.

Non modifica registry o storici. Produce un CSV di audit.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from tools.prepare_input import ROOT, norm

DEBUG = ROOT / "data" / "debug"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = value.casefold().replace("&", " e ")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


COUNTRY_SLUG = {
    "england": "inghilterra", "italy": "italia", "germany": "germania",
    "spain": "spagna", "france": "francia", "netherlands": "olanda",
    "south korea": "corea-del-sud", "saudi arabia": "arabia-saudita",
    "czech republic": "repubblica-ceca", "north macedonia": "macedonia-del-nord",
}


def country_slug(country: str) -> str:
    return COUNTRY_SLUG.get(norm(country), slug(country))


def fetch(url: str, timeout: int = 15) -> tuple[int, str]:
    req = Request(url, headers={"User-Agent": UA, "Accept-Language": "it-IT,it;q=0.9,en;q=0.7"})
    try:
        with urlopen(req, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        return exc.code, ""
    except (URLError, TimeoutError, OSError):
        return 0, ""


def bookmaker_urls(country: str, league: str) -> dict[str, str]:
    c, l = country_slug(country), slug(league)
    return {
        "SNAI": f"https://www.snai.it/scommesse/quote/calcio/{c}/{l}",
        "BETSSON": f"https://www.betsson.it/scommesse/calcio/{c}",
        "DAZNBET": f"https://www2.daznbet.it/scommesse/calcio/{c}/{l}/",
    }


def present(book: str, league: str, status: int, body: str) -> bool:
    if status != 200 or not body:
        return False
    text = re.sub(r"<[^>]+>", " ", body)
    text = re.sub(r"\\s+", " ", text)
    needle = norm(league)
    hay = norm(text)
    if needle and needle in hay:
        return True
    # SNAI/DAZN: una pagina valida di competizione con mercati/eventi e URL specifico
    if book in {"SNAI", "DAZNBET"}:
        markers = ("1x2", "under over", "doppia chance", "eventi")
        return sum(marker in hay for marker in markers) >= 2
    return False


def latest_discovery() -> Path:
    files = sorted(DEBUG.glob("discover_leagues_*.csv"))
    if not files:
        raise SystemExit("Nessun discover_leagues_*.csv trovato in data/debug")
    return files[-1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Verifica le NEW league sui bookmaker pubblici.")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--include-women", action="store_true")
    args = parser.parse_args()

    source = args.input or latest_discovery()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output = DEBUG / f"bookmaker_leagues_{stamp}.csv"

    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))

    allowed = {"LEAGUE"}
    if args.include_women:
        allowed.add("WOMEN_LEAGUE")
    candidates = [r for r in rows if r["Status"] == "NEW" and r["KindOrLeagueId"] in allowed]

    cache: dict[tuple[str, str], tuple[int, str]] = {}
    results = []
    for idx, row in enumerate(candidates, 1):
        urls = bookmaker_urls(row["Country"], row["League"])
        found = {}
        for book, url in urls.items():
            # Betsson e' una pagina paese: una sola richiesta viene riusata per tutte le leghe del paese.
            key = (book, url)
            if key not in cache:
                cache[key] = fetch(url)
            status, body = cache[key]
            found[book] = present(book, row["League"], status, body)
        score = sum(found.values())
        results.append({
            **row,
            "SNAI": "YES" if found["SNAI"] else "NO",
            "BETSSON": "YES" if found["BETSSON"] else "NO",
            "DAZNBET": "YES" if found["DAZNBET"] else "NO",
            "Bookmakers": f"{score}/3",
            "Bookable": "YES" if score else "NO",
        })
        if idx % 25 == 0 or idx == len(candidates):
            print(f"[CHECK] {idx}/{len(candidates)}")

    fields = list(results[0].keys()) if results else [
        "Status", "KindOrLeagueId", "Country", "League", "Matches", "FirstDate", "LastDate",
        "SNAI", "BETSSON", "DAZNBET", "Bookmakers", "Bookable",
    ]
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";")
        writer.writeheader()
        writer.writerows(results)

    yes = sum(r["Bookable"] == "YES" for r in results)
    print(f"[DONE] candidati={len(results)} bookable={yes} non_trovati={len(results)-yes}")
    print(f"[OUTPUT] {output}")
    print("[DRY-RUN] Nessuna modifica a registry o storici.")


if __name__ == "__main__":
    main()
