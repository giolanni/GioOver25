"""Probe read-only di una pagina lega Flashscore.

Estrae tournament ID e candidati season ID dall'HTML, quindi prova i feed
tr_1 cercando un match ID noto. Non modifica registry o storici.
"""
from __future__ import annotations

import argparse
import re
from urllib.request import Request, urlopen

from tools.prepare_input import ROOT

FSIGN = "SW9D1eZo"

TOURNAMENT_PATTERNS = (
    r'["\']?tournament_id["\']?\s*[:=]\s*["\']?([A-Za-z0-9]+)',
    r'["\']?tournamentId["\']?\s*[:=]\s*["\']?([A-Za-z0-9]+)',
)
SEASON_PATTERNS = (
    r'["\']?season_id["\']?\s*[:=]\s*["\']?([A-Za-z0-9]+)',
    r'["\']?seasonId["\']?\s*[:=]\s*["\']?([A-Za-z0-9]+)',
    r'["\']?season["\']?\s*:\s*\{[^{}]{0,500}?["\']?id["\']?\s*:\s*["\']?([A-Za-z0-9]+)',
)


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


def first_match(html: str, patterns: tuple[str, ...]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def season_candidates(html: str, tournament_id: str | None) -> list[str]:
    found: set[str] = set()

    # Prima cerca vicino al tournament ID: riduce drasticamente i falsi
    # positivi presenti nel grande HTML della pagina.
    chunks = []
    if tournament_id:
        for match in re.finditer(re.escape(tournament_id), html):
            start = max(0, match.start() - 12000)
            end = min(len(html), match.end() + 12000)
            chunks.append(html[start:end])

    # Poi amplia all'intera pagina come fallback.
    chunks.append(html)
    for chunk in chunks:
        for pattern in SEASON_PATTERNS:
            for value in re.findall(pattern, chunk, re.IGNORECASE):
                if value and value != "0":
                    found.add(value)
        if found:
            break
    return sorted(found)


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

    tournament_id = args.tournament_id or first_match(html, TOURNAMENT_PATTERNS)
    seasons = [args.season_id] if args.season_id else season_candidates(html, tournament_id)

    print(f"[DISCOVERY] tournament_id={tournament_id or 'NOT_FOUND'}")
    print(f"[DISCOVERY] season_candidates={','.join(seasons) if seasons else 'NOT_FOUND'}")

    if tournament_id:
        for match in re.finditer(re.escape(tournament_id), html):
            context = html[max(0, match.start()-350):min(len(html), match.end()+350)]
            with (outdir / "tournament_context.txt").open("a", encoding="utf-8") as fh:
                fh.write(context + "\n\n---\n\n")

    if not tournament_id or not seasons:
        print(f"[PROBE] output={outdir}")
        print("[DRY-RUN] Nessuna modifica a registry o storici.")
        print("[NEXT] Aprire tournament_context.txt: serve identificare il vero season ID.")
        return

    hits = 0
    useful: list[tuple[str, str, int]] = []
    for season_id in seasons[:20]:
        for page in range(0, 3):
            for feed_type in (2, 3):
                endpoint = f"tr_1_{tournament_id}_{season_id}_{page}_{feed_type}_en_1"
                url = f"https://global.flashscore.ninja/2/x/feed/{endpoint}"
                code, body = fetch(url, args.league_url)
                contains = bool(args.match_id and args.match_id in body)
                if code == 200 and len(body) > 1:
                    useful.append((season_id, endpoint, len(body)))
                    (outdir / f"{endpoint}.txt").write_text(body, encoding="utf-8")
                    print(
                        f"[FEED] {code} len={len(body)} "
                        f"match_id={'YES' if contains else 'NO'} {endpoint}"
                    )
                if contains:
                    hits += 1

    print(f"[PROBE] useful_feeds={len(useful)} match_hits={hits}")
    print(f"[PROBE] output={outdir}")
    print("[DRY-RUN] Nessuna modifica a registry o storici.")
    if not useful:
        print("[NEXT] Nessun tr_1 utile: usare tournament_context.txt per ricavare il season ID reale.")


if __name__ == "__main__":
    main()
