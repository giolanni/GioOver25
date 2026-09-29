"""Orchestratori provider per generare gli input GioOver25."""
from __future__ import annotations

from datetime import date, timedelta

from tools.diretta_mobile import fetch_feed, parse_feed, convert
from tools.prepare_input import Match, canonical_team, load_registry, norm, unique


def target_offset(target: date) -> int | None:
    delta = (target - date.today()).days
    return delta if delta in (-1, 0, 1) else None


def diretta_matches(target: date, mode: str, registry):
    offset = target_offset(target)
    if offset is None:
        print(f"[DIRETTA] {target}: feed disponibile solo per ieri/oggi/domani; salto provider.")
        return []
    raw = parse_feed(fetch_feed(offset))
    matches, unmapped, _borderline, skipped = convert(raw, offset, mode, registry)
    print(f"[DIRETTA] {len(matches)} valide | {len(unmapped)} competizioni escluse | {skipped} scartate")
    return matches


def sofascore_matches(target: date, mode: str):
    from tools.sofascore import kolmonen_ids, build_team_index, fetch_day, resolve_group

    groups = build_team_index(kolmonen_ids())
    out = []
    unresolved = 0
    for event in fetch_day(target.isoformat()):
        home_raw = event.get("homeTeam", {}).get("name", "")
        away_raw = event.get("awayTeam", {}).get("name", "")
        lid, _method = resolve_group(home_raw, away_raw, groups)
        if not lid:
            unresolved += 1
            continue
        home = canonical_team(home_raw)
        away = canonical_team(away_raw)
        state = event.get("status", {}).get("type", "")
        if mode == "rank":
            if state not in ("notstarted", "scheduled"):
                continue
            out.append(Match(lid, target.isoformat(), home, away))
        else:
            if state != "finished":
                continue
            hg = event.get("homeScore", {}).get("current")
            ag = event.get("awayScore", {}).get("current")
            if hg is None or ag is None:
                continue
            out.append(Match(lid, target.isoformat(), home, away, str(hg), str(ag), "Finale"))
    print(f"[SOFASCORE] {len(out)} valide | {unresolved} non risolte")
    return unique(out)


def merge_matches(*sources):
    """Unisce provider; la chiave canonica è LeagueId+MatchDate+Home+Away."""
    merged = {}
    for matches in sources:
        for m in matches:
            key = (m.league_id, m.date, norm(canonical_team(m.home)), norm(canonical_team(m.away)))
            # Il provider successivo completa solo se la partita non esiste già.
            if key not in merged:
                m.home = canonical_team(m.home)
                m.away = canonical_team(m.away)
                merged[key] = m
    return list(merged.values())
