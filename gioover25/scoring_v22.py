from gioover25.scoring_v21dev import (
    ScoreV21DevResult,
    _attack_score,
    _band,
    _btts_score,
    _build_reason,
    _clamp,
    _defense_weakness_score,
    _last10_over_score,
    _venue_over_score,
)


def calculate_score_v22(match_stats, league_info):
    home = match_stats.home
    away = match_stats.away

    teams_count = int(getattr(league_info, "teams", 14) or 14)

    ranking_gap_score = _clamp(abs(match_stats.position_gap) / max(teams_count - 1, 1))

    home_attack_score = _attack_score(home.overall.gf_per_match)
    away_attack_score = _attack_score(away.overall.gf_per_match)

    home_defense_weakness_score = _defense_weakness_score(home.overall.ga_per_match)
    away_defense_weakness_score = _defense_weakness_score(away.overall.ga_per_match)

    home_last10_over_score = _last10_over_score(home)
    away_last10_over_score = _last10_over_score(away)

    home_venue_over_score = _venue_over_score(home.home)
    away_venue_over_score = _venue_over_score(away.away)

    btts_profile_score = _btts_score(home, away)

    total = (
        ranking_gap_score * 6
        + home_attack_score * 13
        + away_attack_score * 13
        + home_defense_weakness_score * 8
        + away_defense_weakness_score * 10
        + home_last10_over_score * 12
        + away_last10_over_score * 12
        + home_venue_over_score * 10
        + away_venue_over_score * 10
        + btts_profile_score * 12
    )

    score = round(total, 2)

    reason = _build_reason(
        home_attack_score,
        away_attack_score,
        home_defense_weakness_score,
        away_defense_weakness_score,
        home_last10_over_score,
        away_last10_over_score,
        home_venue_over_score,
        away_venue_over_score,
        btts_profile_score,
    )

    return ScoreV21DevResult(
        score=score,
        band=_band(score),
        reason=reason,
        ranking_gap_score=round(ranking_gap_score * 6, 2),
        home_attack_score=round(home_attack_score * 13, 2),
        away_attack_score=round(away_attack_score * 13, 2),
        home_defense_weakness_score=round(home_defense_weakness_score * 8, 2),
        away_defense_weakness_score=round(away_defense_weakness_score * 10, 2),
        home_last10_over_score=round(home_last10_over_score * 12, 2),
        away_last10_over_score=round(away_last10_over_score * 12, 2),
        home_venue_over_score=round(home_venue_over_score * 10, 2),
        away_venue_over_score=round(away_venue_over_score * 10, 2),
        btts_profile_score=round(btts_profile_score * 12, 2),
    )