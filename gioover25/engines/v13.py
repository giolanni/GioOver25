import hashlib

from gioover25.scoring_v2 import ScoreV2Result
from gioover25.config import WEIGHTS, NORMALIZATION


ENGINE_NAME = "v13"
ENGINE_VERSION = "1.3.0"


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def _deterministic_random(home: str, away: str) -> float:
    key = f"{home}-{away}".encode("utf-8")
    digest = hashlib.md5(key).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def _identify_strong_weak(match_stats):
    if match_stats.home.position <= match_stats.away.position:
        return match_stats.home, match_stats.away
    return match_stats.away, match_stats.home


def _ranking_gap_score(strong, weak, teams_count: int) -> float:
    if teams_count <= 1:
        teams_count = max(strong.position, weak.position, 20)

    position_gap = abs(strong.position - weak.position)
    position_gap_ratio = position_gap / max(teams_count - 1, 1)

    ppg_gap = abs(strong.ppg - weak.ppg)
    ppg_gap_ratio = clamp(ppg_gap / 1.50)

    return clamp(
        position_gap_ratio * 0.35 +
        ppg_gap_ratio * 0.65
    )


def _last10_team_profile(team) -> float:
    over_component = team.last10.over25_rate
    attack_component = clamp(team.last10.gf_per_match / 1.6)
    defensive_openness = clamp(team.last10.ga_per_match / 2.0)

    return clamp(
        over_component * 0.35 +
        attack_component * 0.45 +
        defensive_openness * 0.20
    )


def _last10_match_profile(home, away) -> float:
    home_profile = _last10_team_profile(home)
    away_profile = _last10_team_profile(away)

    combined = (home_profile + away_profile) / 2

    both_low_attack = (
        home.last10.gf_per_match < 0.6
        and away.last10.gf_per_match < 0.6
    )

    if both_low_attack:
        combined *= 0.55

    return clamp(combined)


def _band(score: float) -> str:
    if score >= 75:
        return "ALTA"
    if score >= 60:
        return "MEDIA-ALTA"
    if score >= 45:
        return "MEDIA"
    return "BASSA"


def calculate_score(match_stats, league_info) -> ScoreV2Result:
    strong, weak = _identify_strong_weak(match_stats)

    ranking_score = _ranking_gap_score(strong, weak, league_info.teams)

    strong_gf_score = clamp(
        strong.overall.gf_per_match / NORMALIZATION["excellent_gf_per_match"]
    )

    weak_ga_score = clamp(
        weak.overall.ga_per_match / NORMALIZATION["bad_ga_per_match"]
    )

    strong_ga_score = clamp(
        strong.overall.ga_per_match / NORMALIZATION["useful_ga_per_match_strong"]
    )

    weak_gf_score = clamp(
        weak.overall.gf_per_match / NORMALIZATION["useful_gf_per_match_weak"]
    )

    last10_score = _last10_match_profile(match_stats.home, match_stats.away)

    real_over_index = clamp(
        (
            match_stats.home.last10.over25_rate
            + match_stats.away.last10.over25_rate
        ) / 2
    )

    random_score = _deterministic_random(
        match_stats.home.team,
        match_stats.away.team
    )

    ranking_component = ranking_score * WEIGHTS["ranking_gap"]
    strong_gf_component = strong_gf_score * WEIGHTS["strong_team_goals_for"]
    weak_ga_component = weak_ga_score * WEIGHTS["weak_team_goals_against"]
    strong_ga_component = strong_ga_score * WEIGHTS["strong_team_goals_against"]
    weak_gf_component = weak_gf_score * WEIGHTS["weak_team_goals_for"]
    last10_component = last10_score * WEIGHTS["last10_over_profile"]
    real_over_component = real_over_index * WEIGHTS["real_over_index"]
    random_component = random_score * WEIGHTS["random_component"]

    total = (
        ranking_component
        + strong_gf_component
        + weak_ga_component
        + strong_ga_component
        + weak_gf_component
        + last10_component
        + real_over_component
        + random_component
    )

    score = round(total, 2)

    reason = (
        f"Engine v1.3 | "
        f"Squadra alta: {strong.team} ({strong.position}ª), "
        f"squadra bassa: {weak.team} ({weak.position}ª) | "
        f"GF alta: {strong.overall.gf_per_match:.2f}/gara | "
        f"GS bassa: {weak.overall.ga_per_match:.2f}/gara | "
        f"Profilo ultime 10: {last10_score:.2f} | "
        f"Real over index: {real_over_index:.2f}"
    )

    return ScoreV2Result(
        score=score,
        band=_band(score),
        ranking_gap_score=round(ranking_component, 2),
        home_attack_score=round(strong_gf_component, 2),
        away_defense_weakness_score=round(weak_ga_component, 2),
        home_last10_over_score=round(last10_component, 2),
        away_last10_over_score=round(real_over_component, 2),
        reason=reason,
    )