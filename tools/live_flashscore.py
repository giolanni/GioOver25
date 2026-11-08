"""Refresh GioOver2.5 LIVE snapshot using existing Diretta provider.

Only fixtures already present in today's ranking histories are eligible.
Never changes official ranking or result CSVs.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

from gioover25.live_monitor import FIELDS, save_snapshot
from tools.diretta_mobile import fetch_feed, parse_feed
from tools.prepare_input import ROOT, canonical_team, load_registry, norm, resolve_match

HISTORY = ROOT / "data" / "storico" / "ranking"
OUTPUT = ROOT / "data" / "live" / "partite_live.csv"
REGISTRY = ROOT / "data" / "league_registry.csv"
SCORE = re.compile(r"^(\d+)-(\d+)$")


def key(league, day, home, away):
    return (league.casefold(), day, norm(canonical_team(home)),
            norm(canonical_team(away)))


def ranking_fixtures(day):
    fixtures = {}
    for path in HISTORY.glob("*/storico_ranking_*.csv"):
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle, delimiter=";"):
                if row.get("MatchDate", "").strip() != day:
                    continue
                if not all(row.get(k, "").strip() for k in ("LeagueId", "Home", "Away")):
                    continue
                k = key(row["LeagueId"], day, row["Home"], row["Away"])
                # Reject ambiguous canonical collisions.
                fixture = (row["LeagueId"], day, row["Home"], row["Away"])
                if k in fixtures and fixtures[k] != fixture:
                    fixtures[k] = None
                elif k not in fixtures:
                    fixtures[k] = fixture
    return fixtures


def fetch_day(day):
    target = date.fromisoformat(day)
    offset = (target - date.today()).days
    raw = {}
    errors = []
    for n in dict.fromkeys((offset, offset - 1, offset + 1)):
        try:
            for match in parse_feed(fetch_feed(n)):
                if match.match_date != day:
                    continue
                k = (match.country, match.league, match.match_date,
                     match.home, match.away)
                # Prefer most informative state, but reject conflicting scores
                if k not in raw or (raw[k].score == "-" and match.score != "-"):
                    raw[k] = match
        except Exception as exc:
            errors.append(f"offset={n}: {exc}")
    if not raw and errors:
        raise RuntimeError("No Diretta fixtures retrieved: " + "; ".join(errors))
    return list(raw.values()), errors


def classify(match):
    """Only provider code 3 is treated as final; 2 as live.

    Unknown codes are never interpreted as FINAL.
    """
    code = match.state_code.strip()
    score = SCORE.fullmatch(match.score.strip())
    if match.status.casefold() in ("posticipata", "rinviata", "sospesa"):
        return "POSTPONED", "", ""
    if not score:
        return "SCHEDULED", "", ""
    if code == "3":
        return "FINAL", score.group(1), score.group(2)
    if code == "2":
        return "LIVE", score.group(1), score.group(2)
    return "UNKNOWN", score.group(1), score.group(2)


def collect(output=OUTPUT, day=None):
    day = day or date.today().isoformat()
    fixtures = ranking_fixtures(day)
    if not fixtures:
        print(f"[LIVE] Nessun ranking disponibile per MatchDate={day}.")
        return 0
    registry = load_registry(REGISTRY)
    raw, errors = fetch_day(day)
    candidates = {}
    ambiguous = set()
    skipped = 0
    for match in raw:
        lid = resolve_match(registry, match.country, match.league,
                            match.home, match.away)
        if not lid:
            skipped += 1
            continue
        k = key(lid, day, match.home, match.away)
        fixture = fixtures.get(k)
        if fixture is None:
            continue
        status, hg, ag = classify(match)
        if status == "UNKNOWN":
            skipped += 1
            continue
        row = dict(zip(("LeagueId", "MatchDate", "Home", "Away"), fixture))
        row.update({"MatchId": match.match_id, "Minute": "",
                    "HG": hg, "AG": ag, "Status": status,
                    "LastUpdate": datetime.now(timezone.utc).isoformat()})
        if k in candidates and candidates[k] != row:
            ambiguous.add(k)
        else:
            candidates[k] = row
    for k in ambiguous:
        candidates.pop(k, None)
    if not candidates:
        print(f"[LIVE] Nessuna corrispondenza verificata per {day}; CSV precedente conservato.")
        return 0
    with tempfile.NamedTemporaryFile("w", suffix=".csv", encoding="utf-8",
                                     newline="", delete=False) as handle:
        temp = Path(handle.name)
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter=";")
        writer.writeheader()
        writer.writerows(candidates.values())
    try:
        count = save_snapshot(temp, output)
    finally:
        temp.unlink(missing_ok=True)
    print(f"[LIVE] {day}: ranking={len(fixtures)} provider={len(raw)} "
          f"aggiornate={count} ambigue={len(ambiguous)} escluse={skipped}")
    if errors:
        print("[LIVE] Feed parziali: " + "; ".join(errors), file=sys.stderr)
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="MatchDate YYYY-MM-DD (default: oggi)")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    collect(args.output, args.date)


if __name__ == "__main__":
    main()
