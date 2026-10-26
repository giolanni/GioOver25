"""Probe read-only di una pagina lega Flashscore.

Estrae tournament/season ID dalla pagina HTML e, quando li trova, prova i
feed tr_1 dei risultati/calendario. Non modifica registry o storici.
"""
from __future__ import annotations

import argparse
import re
from urllib.request import Request, urlopen

from tools.prepare_input import ROOT

FSIGN = "SW9D1eZo"

ID_PATTERNS = {
    "tournament_id": (
        r'["\']?tournament_id["\']?\s*[:=]\s*["\']?([A-Za-z0-9]+)',
        r'["\']?tournamentId["\']?\s*[:=]\s*["\']?([A-Za-z0-9]+)',
    ),
    "season_id": (
        r'["\']?season_id["\']?\s*[:=]\s*["\']?([A-Za-z0-9]+)',
        r'["\']?seasonId["\']?\s*[:=]\s*["\']?([A-Za-z0-9]+)',
    ),
}


def fetch(url: str, referer: str = "https://www.flashscore.com/") -> tuple[int, str]:
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": referer,
        "Origin": "https://www.flashscore.com",
        "x-fsign": FSIGN,
    })
    try:
        with urlopen(req, timeout=20) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return 0, f"{exc.__class__.__name__}: {exc}"


def extract_id(html: str, kind: str) -> str | None:
    for pattern in ID_PATTERNS[kind]:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--league-url", required=True)
    ap.add_argument("--match-id", help="ID noto da cercare nei feed tr_1")
    ap.add_argument("--tournament-id")
    ap.add_argument("--season-id")
    args = ap.parse_args()

    slug = re.sub(r"[^A-Za-z0-9]+", "_", args.league_url).strip("_")[-80:]
    outdir = ROOT / "data" / "debug" / f"flashscore_league_{slug}"
    outdir.mkdir(parents=True, exist_ok=True)

    status, html = fetch(args.league_url, args.league_url)
    (outdir / "league.html").write_text(html, encoding="utf-8")
    print(f"[PAGE] {status or 'ERR'} {args.league_url} len={len(html)}")

    tournament_id = args.tournament_id or extract_id(html, "tournament_id")
    season_id = args.season_id or extract_id(html, "season_id")
    print(f"[DISCOVERY] tournament_id={tournament_id or 'NOT_FOUND'}")
    print(f"[DISCOVERY] season_id={season_id or 'NOT_FOUND'}")

    if not tournament_id or not season_id:
        print(f"[PROBE] output={outdir}")
        print("[DRY-RUN] Nessuna modifica a registry o storici.")
        print("[NEXT] ID non trovati nell'HTML: ispezionare league.html/config della pagina.")
        return

    # Formati osservati nella web app/librerie esistenti. Proviamo entrambe
    # le varianti senza assumere a priori quale sia attiva.
    endpoints = []
    for page in range(0, 3):
        endpoints.extend((
            f"tr_1_{tournament_id}_{season_id}_{page}_2_en_1",
            f"tr_1_{tournament_id}_{season_id}_{page}_3_en_1",
        ))

    hits = 0
    for endpoint in endpoints:
        url = f"https://global.flashscore.ninja/2/x/feed/{endpoint}"
        code, body = fetch(url, args.league_url)
        (outdir / f"{endpoint}.txt").write_text(body, encoding="utf-8")
        contains = bool(args.match_id and args.match_id in body)
        if contains:
            hits += 1
        print(
            f"[FEED] {code or 'ERR'} len={len(body)} "
            f"match_id={'YES' if contains else 'NO'} {endpoint}"
        )

    print(f"[PROBE] match_hits={hits}")
    print(f"[PROBE] output={outdir}")
    print("[DRY-RUN] Nessuna modifica a registry o storici.")


if __name__ == "__main__":
    main()
