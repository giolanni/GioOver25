"""Prototipo SofaScore per le leghe Kolmonen non coperte da Diretta."""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from tools.prepare_input import canonical_team

ROOT = Path(__file__).resolve().parents[1]
API = "https://www.sofascore.com/api/v1"
KOLMONEN_TOURNAMENT_ID = 25914
KOLMONEN_PREFIX = "Finland_Kolmonen_"


def get_json(url: str, timeout: int = 20):
    try:
        from curl_cffi import requests
    except ImportError as exc:
        raise SystemExit(
            "SofaScore blocca i client HTTP Python standard. Installa il client TLS compatibile "
            "con Chrome con: pip install curl_cffi"
        ) from exc

    response = requests.get(
        url,
        timeout=timeout,
        impersonate="chrome",
        headers={
            "Accept": "application/json",
            "Referer": "https://www.sofascore.com/",
            "Origin": "https://www.sofascore.com",
        },
    )
    if response.status_code == 403:
        raise SystemExit(
            "SofaScore ha restituito HTTP 403 anche con TLS Chrome: sorgente non affidabile "
            "per l'automazione da questa connessione."
        )
    response.raise_for_status()
    return response.json()


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def kolmonen_ids() -> set[str]:
    path = ROOT / "data" / "league_registry.csv"
    with path.open(encoding="utf-8-sig", newline="") as f:
        return {
            row["LeagueId"] for row in csv.DictReader(f, delimiter=";")
            if row.get("LeagueId", "").startswith(KOLMONEN_PREFIX)
        }


def build_team_index(league_ids: set[str]):
    """Ricava dagli storici quali squadre appartengono a ciascun gruppo Kolmonen.

    I CSV storici non hanno la colonna LeagueId: il LeagueId canonico coincide
    con il nome del file (senza .csv).
    """
    team_groups = defaultdict(set)
    results_root = ROOT / "data" / "storico" / "risultati"
    for path in results_root.glob("Finland_Kolmonen_*.csv"):
        lid = path.stem
        if lid not in league_ids:
            continue
        try:
            with path.open(encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                for row in reader:
                    for key in ("Home", "Away"):
                        team = row.get(key, "").strip()
                        if team:
                            team_groups[norm(team)].add(lid)
        except (UnicodeDecodeError, csv.Error):
            continue
    return team_groups


def resolve_group(home: str, away: str, team_groups) -> tuple[str | None, str]:
    hg = team_groups.get(norm(canonical_team(home)), set())
    ag = team_groups.get(norm(canonical_team(away)), set())
    common = hg & ag
    if len(common) == 1:
        return next(iter(common)), "both"
    union = hg | ag
    if len(union) == 1:
        return next(iter(union)), "one-team"
    if not union:
        return None, "unknown"
    return None, "ambiguous"


def get_season_id(year: int) -> int:
    data = get_json(f"{API}/unique-tournament/{KOLMONEN_TOURNAMENT_ID}/seasons")
    for season in data.get("seasons", []):
        if str(season.get("year")) == str(year) or str(season.get("name")) == str(year):
            return int(season["id"])
    raise SystemExit(f"Stagione Kolmonen {year} non trovata su SofaScore.")


def fetch_season_events(season_id: int, direction: str):
    events = []
    page = 0
    while True:
        data = get_json(
            f"{API}/unique-tournament/{KOLMONEN_TOURNAMENT_ID}/season/"
            f"{season_id}/events/{direction}/{page}"
        )
        events.extend(data.get("events", []))
        if not data.get("hasNextPage"):
            break
        page += 1
        if page > 100:
            raise SystemExit("Troppe pagine SofaScore: interruzione di sicurezza.")
    return events


def fetch_day(day: str):
    target = date.fromisoformat(day)
    season_id = get_season_id(target.year)
    # 'last' contiene lo storico della stagione. 'next' completa eventuali date future.
    events = fetch_season_events(season_id, "last")
    if target >= date.today():
        events += fetch_season_events(season_id, "next")

    found = {}
    for event in events:
        ts = event.get("startTimestamp")
        if not ts:
            continue
        event_day = datetime.fromtimestamp(ts).astimezone().date()
        if event_day == target:
            found[event.get("id", (event.get("homeTeam", {}).get("name"), event.get("awayTeam", {}).get("name")))] = event
    return list(found.values())


def main():
    p = argparse.ArgumentParser(description="Test SofaScore -> GioOver25 per Finland Kolmonen.")
    p.add_argument("--date", required=True, help="Data YYYY-MM-DD")
    p.add_argument("--dry-run", action="store_true", help="Non scrive file (modalita prototipo).")
    args = p.parse_args()
    target = date.fromisoformat(args.date)

    lids = kolmonen_ids()
    team_groups = build_team_index(lids)
    events = fetch_day(args.date)

    print(f"[SOFASCORE] Data: {target.isoformat()}")
    print(f"[SOFASCORE] LeagueId Kolmonen nel registry: {len(lids)}")
    print(f"[SOFASCORE] Squadre indicizzate dagli storici: {len(team_groups)}")
    print(f"[SOFASCORE] Partite Kolmonen trovate: {len(events)}")

    resolved = 0
    unresolved = 0
    rows = []
    for event in sorted(events, key=lambda e: e.get("startTimestamp", 0)):
        home = event.get("homeTeam", {}).get("name", "")
        away = event.get("awayTeam", {}).get("name", "")
        ts = event.get("startTimestamp")
        dt = datetime.fromtimestamp(ts).astimezone() if ts else None
        actual_date = dt.date().isoformat() if dt else args.date
        tm = dt.strftime("%H:%M") if dt else "??:??"
        lid, method = resolve_group(home, away, team_groups)
        hs = event.get("homeScore", {}).get("current")
        aas = event.get("awayScore", {}).get("current")
        score = f"{hs}-{aas}" if hs is not None and aas is not None else "-"
        state = event.get("status", {}).get("type", "")
        marker = lid or f"NON RISOLTA:{method}"
        print(f"  {tm} {home} - {away} {score} [{marker}] status={state}")
        if lid:
            resolved += 1
            rows.append((lid, actual_date, home, away, hs, aas, state))
        else:
            unresolved += 1

    print(f"[SOFASCORE] Risolte: {resolved} | Non risolte: {unresolved}")
    if args.dry_run:
        print("[DRY-RUN] Nessun CSV modificato.")


if __name__ == "__main__":
    main()
