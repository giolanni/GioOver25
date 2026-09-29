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

    # Diretta/Flashscore può cambiare il significato del feed relativo prima
    # della mezzanotte locale. Interroga quindi anche i feed adiacenti e usa
    # MatchDate (AD) come autorità sulla giornata reale.
    raw_by_key = {}
    feed_offsets = []
    for candidate in (offset, offset - 1, offset + 1):
        if candidate not in feed_offsets:
            feed_offsets.append(candidate)
    errors = []
    for candidate in feed_offsets:
        try:
            for r in parse_feed(fetch_feed(candidate)):
                if r.match_date != target.isoformat():
                    continue
                key = (r.country, r.league, r.match_date, r.home, r.away)
                raw_by_key[key] = r
        except Exception as exc:
            errors.append(f"{candidate}: {exc}")

    raw = list(raw_by_key.values())
    # Per i risultati conserviamo anche gli esiti amministrativi della partita.
    if mode == "results":
        import re
        from tools.prepare_input import resolve_match
        matches, unmapped, skipped = [], set(), 0
        skipped_states = {}
        skipped_scores = {}
        status_map = {
            "postponed": "Posticipata", "posticipata": "Posticipata",
            "cancelled": "Posticipata", "canceled": "Posticipata", "annullata": "Posticipata",
            "suspended": "Posticipata", "sospesa": "Posticipata",
            "rinviata": "Posticipata",
        }
        for r in raw:
            lid = resolve_match(registry, r.country, r.league, r.home, r.away)
            if not lid:
                unmapped.add((r.country, r.league))
                continue
            sm = re.fullmatch(r"(\d+)-(\d+)", r.score)
            normalized = status_map.get(r.status.strip().casefold())
            if sm and not r.status:
                matches.append(Match(lid, target.isoformat(), r.home, r.away,
                                     sm.group(1), sm.group(2), "Finale"))
            elif normalized:
                matches.append(Match(lid, target.isoformat(), r.home, r.away,
                                     "", "", normalized))
            else:
                skipped += 1
                state_key = r.status.strip() or "<vuoto>"
                skipped_states[state_key] = skipped_states.get(state_key, 0) + 1
                score_key = r.score or "<vuoto>"
                skipped_scores[score_key] = skipped_scores.get(score_key, 0) + 1
        matches = unique(matches)
        if skipped_states:
            print("[DIRETTA DEBUG] Stati/codici delle partite scartate: " +
                  ", ".join(f"{k}={v}" for k, v in sorted(skipped_states.items())))
            print("[DIRETTA DEBUG] Punteggi delle partite scartate: " +
                  ", ".join(f"{k}={v}" for k, v in sorted(skipped_scores.items())))
    else:
        matches, unmapped, _borderline, skipped = convert(raw, offset, mode, registry)
    print(
        f"[DIRETTA] {len(matches)} valide | {len(unmapped)} competizioni escluse | "
        f"{skipped} scartate | feed {','.join(map(str, feed_offsets))}"
    )
    if errors:
        print(f"[DIRETTA] Warning feed parziali: {'; '.join(errors)}")
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
            sofa_status = {
                "canceled": "Posticipata", "cancelled": "Posticipata",
                "postponed": "Posticipata", "suspended": "Posticipata",
            }
            if state in sofa_status:
                out.append(Match(lid, target.isoformat(), home, away, "", "", sofa_status[state]))
                continue
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
