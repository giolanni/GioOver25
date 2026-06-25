from dataclasses import dataclass

from .match_statistics import MatchStatistics
from .ranking_gap import RankingGapResult, calculate_ranking_gap
from .registry import LeagueInfo


@dataclass
class ScoreV2Result:
    score: float
    band: str
    ranking_gap_score: float
    home_attack_score: float
    away_defense_weakness_score: float
    home_last10_over_score: float
    away_last10_over_score: float
    reason: str


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def band_from_score(score: float) -> str:
    if score >= 75:
        return "ALTA"
    if score >= 60:
        return "MEDIA-ALTA"
    if score >= 45:
        return "MEDIA"
    return "BASSA"


def calculate_score_v2(
    match_stats: MatchStatistics,
    league_info: LeagueInfo
) -> ScoreV2Result:
    ranking_gap: RankingGapResult = calculate_ranking_gap(
        match_stats,
        league_info
    )

    home_attack_score = clamp(match_stats.home.overall.gf_per_match / 2.5)
    away_defense_weakness_score = clamp(match_stats.away.overall.ga_per_match / 2.5)

    home_last10_over_score = match_stats.home.last10.over25_rate
    away_last10_over_score = match_stats.away.last10.over25_rate

    total = (
        ranking_gap.score * 20
        + home_attack_score * 25
        + away_defense_weakness_score * 25
        + home_last10_over_score * 15
        + away_last10_over_score * 15
    )

    score = round(total, 2)

    reason = (
        f"Ranking gap: {ranking_gap.score:.3f} | "
        f"Attacco casa: {match_stats.home.overall.gf_per_match:.2f}/gara | "
        f"Difesa trasferta subisce: {match_stats.away.overall.ga_per_match:.2f}/gara | "
        f"Over25 casa ultime10: {match_stats.home.last10.over25_rate:.2f} | "
        f"Over25 trasferta ultime10: {match_stats.away.last10.over25_rate:.2f}"
    )

    return ScoreV2Result(
        score=score,
        band=band_from_score(score),
        ranking_gap_score=round(ranking_gap.score * 20, 2),
        home_attack_score=round(home_attack_score * 25, 2),
        away_defense_weakness_score=round(away_defense_weakness_score * 25, 2),
        home_last10_over_score=round(home_last10_over_score * 15, 2),
        away_last10_over_score=round(away_last10_over_score * 15, 2),
        reason=reason,
    )