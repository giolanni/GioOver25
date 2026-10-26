"""Sonda i feed pubblici Flashscore/Livesport partendo da un match ID.

Diagnostica soltanto: non modifica registry o storici.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from urllib.request import Request, urlopen

from tools.prepare_input import ROOT

FSIGN = "SW9D1eZo"
BASES = (
    "https://global.flashscore.ninja/323/x/feed",
    "https://global.flashscore.ninja/2/x/feed",
)
# Endpoint noti della web app per dati collegati alla singola partita.
PATTERNS = (
    "df_sui_1_{mid}",
    "df_scr_1_{mid}",
    "df_st_1_{mid}",
    "df_li_1_{mid}",
)


def fetch(url: str) -> tuple[int, str]:
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Accept-Language": "it-IT,it;q=0.9",
        "Referer": "https://www.diretta.it/",
        "Origin": "https://www.diretta.it",
        "x-fsign": FSIGN,
    })
    try:
        with urlopen(req, timeout=20) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return 0, f"{exc.__class__.__name__}: {exc}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--match-id", required=True)
    args = ap.parse_args()

    outdir = ROOT / "data" / "debug" / f"flashscore_match_{args.match_id}"
    outdir.mkdir(parents=True, exist_ok=True)

    useful = 0
    for base in BASES:
        for pattern in PATTERNS:
            endpoint = pattern.format(mid=args.match_id)
            url = f"{base}/{endpoint}"
            status, body = fetch(url)
            filename = outdir / f"{base.split('/')[-3]}_{endpoint}.txt"
            filename.write_text(body, encoding="utf-8")
            preview = " ".join(body[:180].split())
            print(f"[PROBE] {status or 'ERR'} {url}")
            print(f"        len={len(body)} preview={preview!r}")
            if status == 200 and len(body) > 20:
                useful += 1

    print(f"[PROBE] risposte_utili={useful}")
    print(f"[PROBE] output={outdir}")
    print("[DRY-RUN] Nessuna modifica a registry o storici.")


if __name__ == "__main__":
    main()
