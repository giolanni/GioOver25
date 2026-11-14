"""Read-only per-day reconciliation of ranking fixtures and historical results.

Coverage is limited to matches present in ranking histories. It cannot prove
that the external provider contains no other games.
"""
from __future__ import annotations
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path
from tools.prepare_input import norm, canonical_team

def _rows(path):
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            yield from csv.DictReader(handle, delimiter=";")
    except (OSError, UnicodeError, csv.Error):
        return

def _key(league, day, home, away):
    return (league.strip().casefold(), day.strip(),
            norm(canonical_team(home)), norm(canonical_team(away)))

def inspect(root: Path, *, until=None):
    """Return per-date coverage and outstanding fixture detail.

    'downloaded' means available in persistent results history, not a
    verified successful getresults execution. Ranking registration is
    checked independently on every engine that selected a fixture.
    """
    until = until or date.today().isoformat()
    ranking_root = root / "data/storico/ranking"
    result_root = root / "data/storico/risultati"
    selected = defaultdict(list)
    for path in ranking_root.glob("*/storico_ranking_*.csv"):
        engine = path.parent.name
        for row in _rows(path):
            day = (row.get("MatchDate") or "").strip()
            if not day or day >= until:
                continue
            league, home, away = ((row.get(field) or "").strip() for field in ("LeagueId", "Home", "Away"))
            if not all((league, home, away)):
                continue
            selected[_key(league, day, home, away)].append((engine, row))
    known = {}
    for path in result_root.glob("*.csv"):
        for row in _rows(path):
            league = (row.get("LeagueId") or path.stem).strip()
            day = (row.get("MatchDate") or "").strip()
            home, away = (row.get("Home") or "").strip(), (row.get("Away") or "").strip()
            if not all((league, day, home, away)):
                continue
            if str(row.get("HG", "")).strip().isdigit() and str(row.get("AG", "")).strip().isdigit():
                known[_key(league, day, home, away)] = row
    # Allow a single fixture result on a different date (rescheduled matches),
    # but do not guess if the pairing appears multiple times.
    by_pair = defaultdict(list)
    for key, row in known.items():
        by_pair[(key[0], key[2], key[3])].append(row)
    postponed = set()
    for row in _rows(root / "data/storico/partite_posticipate.csv"):
        league, day, home, away = ((row.get(x) or "").strip() for x in ("LeagueId", "MatchDate", "Home", "Away"))
        if all((league, day, home, away)):
            postponed.add(_key(league, day, home, away))
    grouped = defaultdict(lambda: dict(total=0, available=0, missing=0, postponed=0,
                                       registered=0, unregistered=0, details=[]))
    for key, predictions in selected.items():
        day = key[1]
        item = grouped[day]
        item["total"] += 1
        result = known.get(key)
        if result is None:
            pair = by_pair.get((key[0], key[2], key[3]), [])
            if len(pair) == 1:
                result = pair[0]
        if result is None:
            if key in postponed:
                item["postponed"] += 1
            else:
                item["missing"] += 1
                item["details"].append((key, "Risultato non trovato", len(predictions)))
            continue
        item["available"] += 1
        pending = [engine for engine, row in predictions
                   if ((row.get("BTTS") if engine.lower().startswith("vg")
                       else row.get("Over25")) or "").strip().upper() not in ("OK", "KO")]
        if pending:
            item["unregistered"] += 1
            item["details"].append((key, "Esito ranking da verificare: " + ", ".join(pending[:5]), len(predictions)))
        else:
            item["registered"] += 1
    return dict(sorted(grouped.items(), reverse=True))
