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
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

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


@dataclass
class Competition:
    country: str
    league: str
    matches: int = 0
    first_date: str = ""
    last_date: str = ""


def canonical_country(country: str) -> str:
    return COUNTRY_MAP.get(country.upper(), country.title())


def discover(start: date, end: date) -> tuple[list[Competition], list[str]]:
    found: dict[tuple[str, str], Competition] = {}
    errors: list[str] = []
    today = date.today()
    current = start

    while current <= end:
        offset = (current - today).days
        try:
            raw = parse_feed(fetch_feed(offset))
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


def classify(registry, competition: Competition) -> tuple[str, str]:
    exact = _exact_league_match(registry, competition.country, competition.league)
    if exact:
        return "KNOWN", exact

    resolved = resolve(registry, competition.country, competition.league)
    if resolved:
        return "KNOWN_ALIAS", resolved

    candidates = [
        row for row in registry
        if norm(row.country) == norm(competition.country)
    ]
    source_markers = _competition_markers(competition.league)

    # Se esistono leghe dello stesso paese con marcatori strutturali compatibili,
    # non inventiamo un LeagueId: richiediamo revisione prima dell'onboarding.
    compatible = []
    for row in candidates:
        target_markers = _competition_markers(row.league) | _competition_markers(row.league_id)
        if source_markers == target_markers:
            compatible.append(row.league_id)

    if compatible:
        preview = ",".join(compatible[:5])
        if len(compatible) > 5:
            preview += ",..."
        return "REVIEW", preview

    return "NEW", ""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scopre le leghe attive su Diretta senza modificare registry o storici."
    )
    parser.add_argument("--days-before", type=int, default=7)
    parser.add_argument("--days-after", type=int, default=7)
    args = parser.parse_args()

    if args.days_before < 0 or args.days_after < 0:
        raise SystemExit("--days-before e --days-after devono essere >= 0")

    today = date.today()
    start = today - timedelta(days=args.days_before)
    end = today + timedelta(days=args.days_after)
    registry = load_registry(ROOT / "data" / "league_registry.csv")

    print(f"[DISCOVERY] Diretta {start.isoformat()} -> {end.isoformat()}")
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
        f"REVIEW={len(buckets['REVIEW'])} | "
        f"NEW={len(buckets['NEW'])}"
    )

    for status in ("NEW", "REVIEW", "KNOWN_ALIAS"):
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
