"""Scopre le competizioni attive su Diretta e le confronta con league_registry.csv.

Prima fase dell'onboarding automatico GioOver25:
- legge il feed Diretta su una finestra temporale;
- deduplica Country + League;
- distingue KNOWN, NEW e AMBIGUOUS/UNSAFE;
- non modifica registry o storici.

Esempio:
    python -m tools.discover_leagues --days-before 7 --days-after 7
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from tools.diretta_mobile import fetch_feed, parse_feed
from tools.prepare_input import (
    COUNTRY_MAP,
    ROOT,
    _competition_markers,
    _exact_league_match,
    load_registry,
    norm,
    resolve,
)


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()
        return len(data)

    def flush(self):
        for stream in self.streams:
            stream.flush()


@dataclass
class Competition:
    country: str
    league: str
    matches: int = 0
    first_date: str = ""
    last_date: str = ""


def canonical_country(country: str) -> str:
    return COUNTRY_MAP.get(country.upper(), country.title())


CACHE_DIR = ROOT / "data" / "debug" / "discover_leagues_cache"


def fetch_day(current: date, today: date) -> str:
    """Riusa i feed dei giorni passati; oggi e futuro vengono sempre aggiornati."""
    offset = (current - today).days
    cache = CACHE_DIR / f"{current.isoformat()}.feed"
    if current < today and cache.exists():
        return cache.read_text(encoding="utf-8")
    payload = fetch_feed(offset)
    if current < today:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache.write_text(payload, encoding="utf-8")
    return payload


def discover(start: date, end: date) -> tuple[list[Competition], list[str]]:
    found: dict[tuple[str, str], Competition] = {}
    errors: list[str] = []
    today = date.today()
    current = start

    while current <= end:
        offset = (current - today).days
        try:
            raw = parse_feed(fetch_day(current, today))
        except Exception as exc:
            errors.append(f"{current.isoformat()}: {exc.__class__.__name__}: {exc}")
            current += timedelta(days=1)
            continue

        for match in raw:
            if match.match_date and match.match_date != current.isoformat():
                continue
            country = canonical_country(match.country)
            key = (norm(country), norm(match.league))
            item = found.get(key)
            if item is None:
                item = Competition(country=country, league=match.league)
                found[key] = item
            item.matches += 1
            actual = match.match_date or current.isoformat()
            if not item.first_date or actual < item.first_date:
                item.first_date = actual
            if not item.last_date or actual > item.last_date:
                item.last_date = actual

        current += timedelta(days=1)

    return sorted(found.values(), key=lambda x: (x.country.casefold(), x.league.casefold())), errors


TEMPORARY_WORDS = (
    "cup", "coppa", "copa", "beker", "pokal", "trophy", "trofeo", "shield",
    "qualificazione", "qualification", "play off", "play-off", "playoffs",
    "spareggio", "super finale", "partita aggiuntiva", "amichevoli", "friendly",
    "knockout",
)
INTERNATIONAL_COUNTRIES = {
    "africa", "asia", "europa", "mondo", "sud america",
    "nord e centro america",
}
YOUTH_WORDS = ("u17", "u18", "u19", "u20", "u21", "u22", "u23", "youth", "primavera")


def competition_kind(league: str, country: str = "") -> str:
    if norm(country) in {norm(x) for x in INTERNATIONAL_COUNTRIES}:
        return "INTERNATIONAL"
    n = norm(league)
    if any(norm(word) in n for word in YOUTH_WORDS):
        return "YOUTH"
    if any(norm(word) in n for word in TEMPORARY_WORDS):
        return "TEMPORARY"
    if any(word in n for word in ("women", "femmin", "donne", "damer", "frauen")):
        return "WOMEN_LEAGUE"
    return "LEAGUE"


def classify(registry, competition: Competition) -> tuple[str, str]:
    exact = _exact_league_match(registry, competition.country, competition.league)
    if exact:
        return "KNOWN", exact

    resolved = resolve(registry, competition.country, competition.league)
    if resolved:
        target = next((row for row in registry if row.league_id == resolved), None)
        source_n = norm(competition.league)
        target_n = norm(target.league) if target else ""
        identity_words = (
            "cup", "coppa", "pokal", "trophy", "trofeo", "shield",
            "women", "femmin", "donne", "damer", "frauen",
            "u17", "u18", "u19", "u20", "u21", "u22", "u23", "youth", "primavera",
            "reserve", "riserve", "next pro",
        )
        added_identity = [
            word for word in identity_words
            if norm(word) in source_n and norm(word) not in target_n
        ]
        if not added_identity:
            return "KNOWN_ALIAS", resolved

    # Il fuzzy matching non deve decidere l'identita' di una nuova competizione:
    # leghe diverse dello stesso paese possono condividere marcatori e parole.
    return "NEW", competition_kind(competition.league, competition.country)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scopre le leghe attive su Diretta/Flashscore senza modificare registry o storici."
    )
    parser.add_argument("--days-before", type=int, default=30)
    parser.add_argument("--days-after", type=int, default=30)
    parser.add_argument("--log", type=str, help="Percorso log; default data/debug/discover_leagues_<timestamp>.log")
    args = parser.parse_args()

    if args.days_before < 0 or args.days_after < 0:
        raise SystemExit("--days-before e --days-after devono essere >= 0")

    log_path = ROOT / args.log if args.log else ROOT / "data" / "debug" / f"discover_leagues_{datetime.now():%Y%m%d-%H%M%S}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = log_path.open("w", encoding="utf-8")
    sys.stdout = Tee(sys.__stdout__, log_file)
    print(f"[LOG] {log_path}")

    today = date.today()
    start = today - timedelta(days=args.days_before)
    end = today + timedelta(days=args.days_after)
    registry = load_registry(ROOT / "data" / "league_registry.csv")

    print(f"[DISCOVERY] Diretta/Flashscore {start.isoformat()} -> {end.isoformat()} (cache giorni passati)")
    competitions, errors = discover(start, end)

    buckets = defaultdict(list)
    for competition in competitions:
        status, detail = classify(registry, competition)
        buckets[status].append((competition, detail))

    print(
        "[DISCOVERY] "
        f"{len(competitions)} competizioni attive | "
        f"KNOWN={len(buckets['KNOWN'])} | "
        f"KNOWN_ALIAS={len(buckets['KNOWN_ALIAS'])} | "
        f"NEW={len(buckets['NEW'])}"
    )

    for status in ("NEW", "KNOWN_ALIAS"):
        rows = buckets[status]
        if not rows:
            continue
        print(f"\n[{status}]")
        for competition, detail in rows:
            suffix = f" -> {detail}" if detail else ""
            print(
                f"{competition.country};{competition.league};"
                f"matches={competition.matches};"
                f"{competition.first_date}..{competition.last_date}{suffix}"
            )

    if errors:
        print(f"\n[WARN] {len(errors)} giornate non lette:")
        for error in errors:
            print(f"  - {error}")

    print("\n[DRY-RUN] Nessuna modifica a league_registry.csv o agli storici.")


if __name__ == "__main__":
    main()
