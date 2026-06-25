from dataclasses import dataclass

from .match_statistics import MatchStatistics
from .registry import LeagueInfo


@dataclass
class RankingGapResult:
    normalized_position_gap: float
    normalized_points_gap: float
    ppg_gap: float
    confidence: float
    score: float


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def calculate_ranking_gap(
    match_stats: MatchStatistics,
    league_info: LeagueInfo
) -> RankingGapResult:
    max_position_gap = max(league_info.teams - 1, 1)

    normalized_position_gap = clamp(
        match_stats.position_gap / max_position_gap
    )

    max_points_gap = max(league_info.expected_rounds * 3, 1)

    normalized_points_gap = clamp(
        match_stats.points_gap / max_points_gap
    )

    ppg_gap = clamp(
        match_stats.ppg_gap / 3.0
    )

    avg_played = (
        match_stats.home.overall.played
        + match_stats.away.overall.played
    ) / 2

    confidence = clamp(
        avg_played / max(league_info.expected_rounds, 1)
    )

    raw_score = (
        normalized_position_gap * 0.40
        + normalized_points_gap * 0.25
        + ppg_gap * 0.35
    )

    final_score = raw_score * confidence

    return RankingGapResult(
        normalized_position_gap=round(normalized_position_gap, 3),
        normalized_points_gap=round(normalized_points_gap, 3),
        ppg_gap=round(ppg_gap, 3),
        confidence=round(confidence, 3),
        score=round(final_score, 3),
    )