"""Scheduled kickoff times shared by GUI and PDF reports.

Stored separately from prediction histories; all times are Europe/Rome.
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tools.prepare_input import ROOT, load_registry, resolve_match
from gioover25.team_names import normalize_team_name

PATH = ROOT / "data" / "operational" / "kickoff_times.csv"
FIELDS = ("LeagueId", "MatchDate", "Home", "Away", "Kickoff", "MatchId")
ROME = ZoneInfo("Europe/Rome")


def key(league, day, home, away):
    return (str(league).strip(), str(day).strip(),
            normalize_team_name(league, home), normalize_team_name(league, away))


def index():
    if not PATH.exists():
        return {}
    with PATH.open(encoding="utf-8-sig", newline="") as handle:
        return {key(r["LeagueId"], r["MatchDate"], r["Home"], r["Away"]): r
                for r in csv.DictReader(handle, delimiter=";")}


def kickoff(row, lookup=None):
    lookup = index() if lookup is None else lookup
    item = lookup.get(key(row.get("LeagueId", ""), row.get("MatchDate", ""),
                          row.get("Home", ""), row.get("Away", "")))
    return item.get("Kickoff", "") if item else ""


def update_from_feed(raw, payload):
    """Save scheduled kickoff from feed AD timestamps; do not infer from AO."""
    registry = load_registry(ROOT / "data" / "league_registry.csv")
    rows = index()
    changed = 0
    for record in payload.split("~"):
        fields = dict(part.split("÷", 1) for part in record.split("¬") if "÷" in part)
        mid = fields.get("AA", "")
        if not mid or not fields.get("AD"):
            continue
        match = raw.get(mid)
        if match is None:
            continue
        league = resolve_match(registry, match.country, match.league, match.home, match.away)
        if not league:
            continue
        try:
            dt = datetime.fromtimestamp(int(fields["AD"]), ROME)
        except (ValueError, OverflowError, OSError):
            continue
        day = dt.date().isoformat()
        k = key(league, day, match.home, match.away)
        value = dict(LeagueId=league, MatchDate=day, Home=match.home,
                     Away=match.away, Kickoff=dt.strftime("%H:%M"), MatchId=mid)
        if rows.get(k) != value:
            rows[k] = value
            changed += 1
    if changed:
        PATH.parent.mkdir(parents=True, exist_ok=True)
        with PATH.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter=";")
            writer.writeheader()
            writer.writerows(sorted(rows.values(), key=lambda r:
                (r["MatchDate"], r["Kickoff"], r["LeagueId"], r["Home"], r["Away"])))
    return changed


def capture(payload, matches):
    by_id = {m.match_id: m for m in matches if m.match_id}
    return update_from_feed(by_id, payload)
