"""Risoluzione read-only dei tornei Flashscore a partire dai SampleMatchId.

Usato dall'onboarding: interroga il feed header del match e stampa gli ID
tournament/template/stage disponibili. Non modifica registry o storici.
"""
from __future__ import annotations

import argparse
import re
from urllib.request import Request, urlopen

MATCH_FEEDS = (
    "https://global.flashscore.ninja/323/x/feed/df_sui_1_{match_id}",
    "https://global.flashscore.ninja/323/x/feed/df_scr_1_{match_id}",
)
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Accept-Language": "it-IT,it;q=0.9",
    "Referer": "https://www.diretta.it/",
    "Origin": "https://www.diretta.it",
    "x-fsign": "SW9D1eZo",
}


def fetch(url: str, timeout: int = 20) -> str:
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def fields(payload: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in re.split(r"[¬~]", payload):
        if "÷" in item:
            key, value = item.split("÷", 1)
            if key and value and key not in out:
                out[key] = value
    return out


def resolve(match_id: str) -> dict[str, str]:
    merged: dict[str, str] = {}
    for pattern in MATCH_FEEDS:
        payload = fetch(pattern.format(match_id=match_id))
        merged.update({k: v for k, v in fields(payload).items() if v})
    return {
        "match_id": match_id,
        "tournament_template_id": merged.get("ZEE", ""),
        "tournament_stage_id": merged.get("ZB", "") or merged.get("ZC", ""),
        "tournament_id": merged.get("ZE", ""),
        "country": merged.get("ZB", "") if merged.get("ZB", "").isalpha() else "",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("match_ids", nargs="+")
    args = ap.parse_args()
    print("MatchId;TournamentTemplateId;TournamentId;TournamentStageId")
    for match_id in args.match_ids:
        try:
            row = resolve(match_id)
            print(f'{match_id};{row["tournament_template_id"]};{row["tournament_id"]};{row["tournament_stage_id"]}')
        except Exception as exc:
            print(f"{match_id};ERROR:{exc.__class__.__name__};;")
    print("[DRY-RUN] Nessuna modifica a registry o storici.")


if __name__ == "__main__":
    main()
