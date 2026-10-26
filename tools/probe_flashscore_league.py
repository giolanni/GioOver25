"""Probe read-only della pagina lega Flashscore."""
from __future__ import annotations
import argparse
import re
from urllib.request import Request, urlopen
from tools.prepare_input import ROOT

def fetch(url: str) -> tuple[int, str]:
    req = Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"*/*","Accept-Language":"en-US,en;q=0.9","Referer":url})
    try:
        with urlopen(req, timeout=20) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return 0, f"{exc.__class__.__name__}: {exc}"

def grab(html: str, pattern: str) -> str | None:
    m = re.search(pattern, html, re.IGNORECASE)
    return m.group(1) if m else None

def initial_feed(html: str, name: str) -> str | None:
    pattern = "cjs\\.initialFeeds\\[['\\\"]" + re.escape(name) + "['\\\"]\\]\\s*=\\s*\\{\\s*data:\\s*" + chr(96) + "(.*?)" + chr(96)
    m = re.search(pattern, html, re.DOTALL)
    return m.group(1) if m else None

def match_ids(feed: str) -> list[str]:
    return re.findall(r"(?:^|¬~)AA÷([A-Za-z0-9]+)", feed)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--league-url", required=True)
    ap.add_argument("--match-id")
    args = ap.parse_args()
    slug = re.sub(r"[^A-Za-z0-9]+", "_", args.league_url).strip("_")[-80:]
    outdir = ROOT / "data" / "debug" / f"flashscore_league_{slug}"
    outdir.mkdir(parents=True, exist_ok=True)
    status, html = fetch(args.league_url)
    (outdir / "league.html").write_text(html, encoding="utf-8")
    print(f"[PAGE] {status or 'ERR'} {args.league_url} len={len(html)}")
    template_id = grab(html, r'tournamentTemplateId:\s*["\x27]([A-Za-z0-9]+)')
    tournament_id = grab(html, r'tournamentId:\s*["\x27]([A-Za-z0-9]+)')
    stage_id = grab(html, r'tournamentStageId:\s*["\x27]([A-Za-z0-9]+)')
    data_service = grab(html, r'dataServiceBaseUrl:\s*["\x27]([^"\x27]+)')
    print(f"[IDS] template={template_id or 'NOT_FOUND'}")
    print(f"[IDS] tournament={tournament_id or 'NOT_FOUND'}")
    print(f"[IDS] stage={stage_id or 'NOT_FOUND'}")
    print(f"[IDS] data_service={data_service or 'NOT_FOUND'}")
    total = 0
    hit = False
    for name in ("results","fixtures","summary-results","summary-fixtures"):
        feed = initial_feed(html, name)
        if feed is None:
            print(f"[INITIAL] {name}=NOT_FOUND")
            continue
        ids = match_ids(feed)
        total += len(ids)
        contains = bool(args.match_id and args.match_id in ids)
        hit = hit or contains
        (outdir / f"initial_{name}.txt").write_text(feed, encoding="utf-8")
        print(f"[INITIAL] {name} len={len(feed)} matches={len(ids)} match_id={'YES' if contains else 'NO'}")
        if ids:
            print(f"          ids={','.join(ids[:20])}")
    print(f"[PROBE] extracted_matches={total} match_hit={'YES' if hit else 'NO'}")
    print(f"[PROBE] output={outdir}")
    print("[DRY-RUN] Nessuna modifica a registry o storici.")
    if not hit and args.match_id:
        print("[NEXT] Match non nella porzione iniziale: interrogare il data service con tournament/stage ID.")

if __name__ == "__main__":
    main()
