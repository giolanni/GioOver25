"""Diagnostica non distruttiva degli identificativi Flashscore di una pagina risultati.

Uso: python -m tools.probe_storico_diretta --girone A
Non importa risultati e non modifica file.
"""
from __future__ import annotations

import argparse
import re
from urllib.request import Request, urlopen

from gioover25.serie_d_registry import SERIE_D_GROUPS


def inspect_html(page: str) -> dict[str, list[str]]:
    patterns = {
        "feed_paths": r"(?:tf|tr|p|t|pr)_1_[A-Za-z0-9_]+",
        "tournament_id": r'(?:tournamentId|tournament_id|tournamentTemplateId|tournamentStageId|tournamentCurrentId)["\\\s:=]+["\\\']?([A-Za-z0-9]{6,20})',
        "stage_id": r'(?:stageId|stage_id|stageTournamentId)["\\\s:=]+["\\\']?([A-Za-z0-9]{6,20})',
        "results_links": r'https?[^"\\\s<>]{0,200}(?:/results/|/risultati/)',
    }
    return {name: sorted(set(re.findall(pattern, page, flags=re.I)))[:30]
            for name, pattern in patterns.items()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--girone", choices=list(SERIE_D_GROUPS), required=True)
    args = p.parse_args()
    url = SERIE_D_GROUPS[args.girone].source_url
    print(f"[PROBE] {url}")
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "it-IT,it;q=0.9",
    })
    try:
        with urlopen(req, timeout=25) as response:
            page = response.read().decode("utf-8", errors="replace")
            print(f"[PROBE] HTTP {response.status} | HTML {len(page)} caratteri")
    except Exception as exc:
        print(f"[PROBE][ERROR] {type(exc).__name__}: {exc}")
        return
    found = inspect_html(page)
    for category, values in found.items():
        print(f"[PROBE] {category}: {len(values)} indizi")
        for value in values:
            print(f"  {value}")
    for candidate in sorted(set(found["tournament_id"] + found["stage_id"])):
        for match in list(re.finditer(re.escape(candidate), page))[:5]:
            context = page[max(0, match.start()-180):min(len(page), match.end()+180)]
            context = re.sub(r"\\s+", " ", context)
            print(f"[PROBE][CONTEXT] {candidate}: {context[:380]}")
    if not any(found.values()):
        print("[PROBE] Nessun ID nel documento HTML: occorre ispezionare le richieste XHR del browser.")


if __name__ == "__main__":
    main()
