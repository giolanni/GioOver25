"""Scopre riferimenti torneo/stagione Flashscore partendo da un match ID.

Diagnostica soltanto: non modifica registry o storici.
Salva le risposte grezze in data/debug per poter aggiungere nuovi pattern
senza perdere le prove gia' effettuate.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.request import Request, urlopen

from tools.prepare_input import ROOT

FSIGN = "SW9D1eZo"
BASES = (
    "https://global.flashscore.ninja/323/x/feed",
    "https://global.flashscore.ninja/2/x/feed",
)

# Feed di dettaglio osservati/usati dalla web app. I primi quattro sono gia'
# verificati da probe_flashscore_match; gli altri servono a cercare metadati
# e collegamenti che possano contenere tournament/stage/season IDs.
MATCH_PATTERNS = (
    "df_sui_1_{mid}",
    "df_scr_1_{mid}",
    "df_st_1_{mid}",
    "df_li_1_{mid}",
    "df_dc_1_{mid}",
    "df_dos_1_{mid}",
    "df_od_1_{mid}",
    "df_hh_1_{mid}",
)

ID_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9]{8}(?![A-Za-z0-9])")
URL_ID_RE = re.compile(
    r"(?:tournament|league|stage|season)[^A-Za-z0-9]{0,20}([A-Za-z0-9]{6,16})",
    re.IGNORECASE,
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


def candidate_ids(body: str, match_id: str) -> list[str]:
    """Estrae ID candidati senza pretendere di conoscerne ancora la semantica."""
    found = set(URL_ID_RE.findall(body))
    # I payload Flashscore usano spesso ID opachi di 8 caratteri.
    # Li riportiamo come candidati, escludendo il match-id di partenza.
    found.update(ID_TOKEN_RE.findall(body))
    found.discard(match_id)
    return sorted(found)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Probe read-only dei riferimenti torneo/stagione Flashscore."
    )
    ap.add_argument("--match-id", required=True)
    args = ap.parse_args()

    outdir = ROOT / "data" / "debug" / f"flashscore_tournament_from_{args.match_id}"
    outdir.mkdir(parents=True, exist_ok=True)

    useful = 0
    all_candidates: set[str] = set()

    for base in BASES:
        locale = base.split("/")[-3]
        for pattern in MATCH_PATTERNS:
            endpoint = pattern.format(mid=args.match_id)
            url = f"{base}/{endpoint}"
            status, body = fetch(url)
            (outdir / f"{locale}_{endpoint}.txt").write_text(body, encoding="utf-8")

            candidates = candidate_ids(body, args.match_id) if status == 200 else []
            all_candidates.update(candidates)
            preview = " ".join(body[:160].split())
            print(f"[PROBE] {status or 'ERR'} {url}")
            print(
                f"        len={len(body)} candidates={len(candidates)} "
                f"preview={preview!r}"
            )
            if candidates:
                print(f"        ids={','.join(candidates[:20])}")
            if status == 200 and len(body) > 20:
                useful += 1

    ids_file = outdir / "candidate_ids.txt"
    ids_file.write_text("\n".join(sorted(all_candidates)), encoding="utf-8")

    print(f"[PROBE] risposte_utili={useful}")
    print(f"[PROBE] candidate_ids={len(all_candidates)}")
    print(f"[PROBE] ids_file={ids_file}")
    print(f"[PROBE] output={outdir}")
    print("[DRY-RUN] Nessuna modifica a registry o storici.")
    print(
        "[NEXT] Se emergono ID candidati, il passo successivo e' provarli "
        "sui feed torneo/calendario e cercare il match-id di partenza."
    )


if __name__ == "__main__":
    main()
