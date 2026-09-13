"""
===============================================================================
GioOver2.5 - match_statistics.py
===============================================================================

Costruisce tutte le statistiche disponibili prima di una partita, senza usare
informazioni future. Oltre alle finestre storiche esistenti espone ora last7 e
last8 per gli esperimenti recent-history. Gli engine esistenti restano
invariati finche non leggono esplicitamente questi campi.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .history import MatchResult
from .statistics import StatsSummary, get_team_statistics
from .standings import calculate_standings_after_round

LONG_BREAK_DAYS = 21
MIN_MATCHES_BEFORE_LONG_BREAK = 5
MIN_MATCHES_TO_BE_RESTART_READY = 3
EARLY_READY_MIN_MATCHES = 2
EARLY_READY_GF_AVG = 2.0


@dataclass
class TeamMatchContext:
    team: str
    overall: StatsSummary
    last5: StatsSummary
    last10: StatsSummary
    home: StatsSummary
    away: StatsSummary
    position: int
    points: int
    ppg: float
    last7: StatsSummary | None = None
    last8: StatsSummary | None = None
    long_break_detected: int = 0
    long_break_days: int = 0
    matches_since_restart: int = 0
    gf_avg_since_restart: float = 0.0
    over_rate_since_restart: float = 0.0
    restart_ready: int = 1
    restart_not_ready: int = 0


@dataclass
class MatchStatistics:
    home: TeamMatchContext
    away: TeamMatchContext
    position_gap: int
    points_gap: int
    ppg_gap: float


def _get_standing_map(matches, before_round, included_teams=None):
    standings = calculate_standings_after_round(
        matches, before_round - 1, included_teams=included_teams
    )
    return {
        standing.team: {
            "position": position,
            "points": standing.points,
            "ppg": standing.ppg,
        }
        for position, standing in enumerate(standings, start=1)
    }


def _as_date(value) -> date:
    return value if isinstance(value, date) else date.fromisoformat(str(value))


def _team_matches_before_round(matches, team, before_round):
    previous = [
        m for m in matches
        if m.round < before_round and team in {m.home, m.away}
    ]
    previous.sort(key=lambda m: (_as_date(m.date), m.round))
    return previous


def _goals_for(match, team):
    return match.home_goals if match.home == team else match.away_goals


def _restart_context(matches, team, before_round):
    previous = _team_matches_before_round(matches, team, before_round)
    neutral = {
        "long_break_detected": 0,
        "long_break_days": 0,
        "matches_since_restart": 0,
        "gf_avg_since_restart": 0.0,
        "over_rate_since_restart": 0.0,
        "restart_ready": 1,
        "restart_not_ready": 0,
    }
    if len(previous) <= MIN_MATCHES_BEFORE_LONG_BREAK:
        return neutral

    break_index = None
    break_days = 0
    for idx in range(1, len(previous)):
        gap = (_as_date(previous[idx].date) - _as_date(previous[idx - 1].date)).days
        if idx >= MIN_MATCHES_BEFORE_LONG_BREAK and gap >= LONG_BREAK_DAYS:
            break_index, break_days = idx, gap
    if break_index is None:
        return neutral

    since = previous[break_index:]
    n = len(since)
    gf = sum(_goals_for(m, team) for m in since)
    over = sum(1 for m in since if m.home_goals + m.away_goals >= 3)
    gf_avg = gf / n if n else 0.0
    over_rate = over / n if n else 0.0
    ready = int(
        n >= MIN_MATCHES_TO_BE_RESTART_READY
        or (n >= EARLY_READY_MIN_MATCHES and over == n)
        or (n >= 1 and gf_avg >= EARLY_READY_GF_AVG)
    )
    return {
        "long_break_detected": 1,
        "long_break_days": break_days,
        "matches_since_restart": n,
        "gf_avg_since_restart": round(gf_avg, 3),
        "over_rate_since_restart": round(over_rate, 3),
        "restart_ready": ready,
        "restart_not_ready": int(not ready),
    }


def build_team_context(matches, team, before_round, standing_teams=None):
    standing = _get_standing_map(
        matches, before_round, included_teams=standing_teams
    ).get(team, {"position": 999, "points": 0, "ppg": 0.0})
    restart = _restart_context(matches, team, before_round)
    return TeamMatchContext(
        team=team,
        overall=get_team_statistics(matches, team, before_round=before_round),
        last5=get_team_statistics(matches, team, before_round=before_round, last_n=5),
        last10=get_team_statistics(matches, team, before_round=before_round, last_n=10),
        home=get_team_statistics(matches, team, before_round=before_round, venue="home"),
        away=get_team_statistics(matches, team, before_round=before_round, venue="away"),
        position=standing["position"],
        points=standing["points"],
        ppg=standing["ppg"],
        last7=get_team_statistics(matches, team, before_round=before_round, last_n=7),
        last8=get_team_statistics(matches, team, before_round=before_round, last_n=8),
        long_break_detected=int(restart["long_break_detected"]),
        long_break_days=int(restart["long_break_days"]),
        matches_since_restart=int(restart["matches_since_restart"]),
        gf_avg_since_restart=float(restart["gf_avg_since_restart"]),
        over_rate_since_restart=float(restart["over_rate_since_restart"]),
        restart_ready=int(restart["restart_ready"]),
        restart_not_ready=int(restart["restart_not_ready"]),
    )


def build_match_statistics(
    matches,
    home_team,
    away_team,
    before_round,
    standing_teams=None,
    home_standing_teams=None,
    away_standing_teams=None,
):
    home_set = home_standing_teams if home_standing_teams is not None else standing_teams
    away_set = away_standing_teams if away_standing_teams is not None else standing_teams
    home = build_team_context(matches, home_team, before_round, home_set)
    away = build_team_context(matches, away_team, before_round, away_set)

    home_has = home.overall.played > 0
    away_has = away.overall.played > 0
    if not home_has and away_has:
        home.position, home.points, home.ppg = away.position, away.points, away.ppg
    elif not away_has and home_has:
        away.position, away.points, away.ppg = home.position, home.points, home.ppg
    elif not home_has and not away_has:
        home.position = away.position = 1
        home.points = away.points = 0
        home.ppg = away.ppg = 0.0

    return MatchStatistics(
        home=home,
        away=away,
        position_gap=abs(home.position - away.position),
        points_gap=abs(home.points - away.points),
        ppg_gap=abs(home.ppg - away.ppg),
    )
