from dataclasses import dataclass

from .history import MatchResult
from .statistics import StatsSummary, get_team_statistics
from .standings import calculate_standings_after_round


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


@dataclass
class MatchStatistics:
    home: TeamMatchContext
    away: TeamMatchContext
    position_gap: int
    points_gap: int
    ppg_gap: float


def _get_standing_map(matches: list[MatchResult], before_round: int) -> dict[str, dict]:
    standings = calculate_standings_after_round(matches, before_round - 1)

    result = {}

    for position, standing in enumerate(standings, start=1):
        result[standing.team] = {
            "position": position,
            "points": standing.points,
            "ppg": standing.ppg,
        }

    return result


def build_team_context(
    matches: list[MatchResult],
    team: str,
    before_round: int
) -> TeamMatchContext:
    standing_map = _get_standing_map(matches, before_round)

    standing = standing_map.get(
        team,
        {
            "position": 999,
            "points": 0,
            "ppg": 0.0,
        }
    )

    return TeamMatchContext(
        team=team,
        overall=get_team_statistics(
            matches,
            team,
            before_round=before_round,
        ),
        last5=get_team_statistics(
            matches,
            team,
            before_round=before_round,
            last_n=5,
        ),
        last10=get_team_statistics(
            matches,
            team,
            before_round=before_round,
            last_n=10,
        ),
        home=get_team_statistics(
            matches,
            team,
            before_round=before_round,
            venue="home",
        ),
        away=get_team_statistics(
            matches,
            team,
            before_round=before_round,
            venue="away",
        ),
        position=standing["position"],
        points=standing["points"],
        ppg=standing["ppg"],
    )


def build_match_statistics(
    matches: list[MatchResult],
    home_team: str,
    away_team: str,
    before_round: int
) -> MatchStatistics:
    home = build_team_context(matches, home_team, before_round)
    away = build_team_context(matches, away_team, before_round)

    return MatchStatistics(
        home=home,
        away=away,
        position_gap=abs(home.position - away.position),
        points_gap=abs(home.points - away.points),
        ppg_gap=abs(home.ppg - away.ppg),
    )