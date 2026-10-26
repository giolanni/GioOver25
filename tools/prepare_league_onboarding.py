"""Prepara i campionati NEW scoperti da discover_leagues per l'onboarding.

Legge un log di discovery (di default il piu' recente), considera soltanto
le righe NEW classificate LEAGUE, propone un LeagueId e controlla collisioni
con league_registry.csv.

Non modifica il registry e non crea storici.

Esempio:
    python -m tools.prepare_league_onboarding
    python -m tools.prepare_league_onboarding --log data/debug/discover_leagues_....log
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from tools.prepare_input import ROOT, load_registry, norm


@dataclass
class Candidate:
    country: str
    league: str
    matches: int
    first_date: str
    last_date: str
    league_id: str = ""
    status: str = ""


def ascii_token(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "", value)


def proposed_league_id(country: str, league: str) -> str:
    return f"{ascii_token(country)}_{ascii_token(league)}"


def latest_discovery_log() -> Path:
    logs = sorted((ROOT / "data" / "debug").glob("discover_leagues_*.log"))
    if not logs:
        raise SystemExit("Nessun log discover_leagues trovato in data/debug")
    return logs[-1]


def parse_new_leagues(path: Path) -> list[Candidate]:
    candidates: list[Candidate] = []
    in_new = False
    pattern = re.compile(
        r"^(?P<country>[^;]+);(?P<league>[^;]+);matches=(?P<matches>\d+);"
        r"(?P<first>\d{4}-\d{2}-\d{2})\.\.(?P<last>\d{4}-\d{2}-\d{2}) -> LEAGUE$"
    )
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if line == "[NEW]":
            in_new = True
            continue
        if in_new and line.startswith("["):
            break
        if not in_new:
            continue
        match = pattern.match(line)
        if not match:
            continue
        candidates.append(
            Candidate(
                country=match.group("country"),
                league=match.group("league"),
                matches=int(match.group("matches")),
                first_date=match.group("first"),
                last_date=match.group("last"),
            )
        )
    return candidates


def classify(candidates: list[Candidate], registry) -> None:
    ids = {row.league_id.casefold(): row for row in registry}
    exact_names = {(norm(row.country), norm(row.league)): row for row in registry}
    proposed_seen: dict[str, Candidate] = {}

    for item in candidates:
        item.league_id = proposed_league_id(item.country, item.league)
        key = (norm(item.country), norm(item.league))
        if key in exact_names:
            item.status = f"EXISTS:{exact_names[key].league_id}"
            continue
        if item.league_id.casefold() in ids:
            item.status = f"ID_COLLISION:{ids[item.league_id.casefold()].league_id}"
            continue
        folded = item.league_id.casefold()
        if folded in proposed_seen:
            item.status = f"NEW_COLLISION:{proposed_seen[folded].league}"
            continue
        proposed_seen[folded] = item
        item.status = "READY"


def write_csv(candidates: list[Candidate], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(
            ["Country", "League", "ProposedLeagueId", "MatchesInWindow",
             "FirstDate", "LastDate", "Status"]
        )
        for item in candidates:
            writer.writerow(
                [item.country, item.league, item.league_id, item.matches,
                 item.first_date, item.last_date, item.status]
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepara i NEW LEAGUE per onboarding, senza modificare il registry.")
    parser.add_argument("--log", type=str, help="Log discovery; default: il piu' recente in data/debug")
    parser.add_argument("--output", type=str, help="CSV output opzionale")
    args = parser.parse_args()

    source = ROOT / args.log if args.log else latest_discovery_log()
    if not source.exists():
        raise SystemExit(f"Log non trovato: {source}")

    registry = load_registry(ROOT / "data" / "league_registry.csv")
    candidates = parse_new_leagues(source)
    classify(candidates, registry)

    output = (
        ROOT / args.output
        if args.output
        else ROOT / "data" / "debug" / f"league_onboarding_{datetime.now():%Y%m%d-%H%M%S}.csv"
    )
    write_csv(candidates, output)

    counts: dict[str, int] = {}
    for item in candidates:
        base = item.status.split(":", 1)[0]
        counts[base] = counts.get(base, 0) + 1

    print(f"[ONBOARDING] source={source}")
    print(f"[ONBOARDING] candidati NEW LEAGUE={len(candidates)}")
    print("[ONBOARDING] " + " | ".join(f"{key}={value}" for key, value in sorted(counts.items())))
    print(f"[ONBOARDING] output={output}")
    print("[DRY-RUN] Nessuna modifica a league_registry.csv o agli storici.")


if __name__ == "__main__":
    main()
