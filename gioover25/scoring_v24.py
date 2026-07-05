from gioover25.scoring_v22 import calculate_score_v22
from gioover25.scoring_v21dev import ScoreV21DevResult, _band


def _safe_rate(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def calculate_score_v24(match_stats, league_info):
    base = calculate_score_v22(match_stats, league_info)

    home = match_stats.home
    away = match_stats.away

    home_btts = _safe_rate(home.overall.btts, home.overall.played)
    away_btts = _safe_rate(away.overall.btts, away.overall.played)
    btts_rate = (home_btts + away_btts) / 2

    away_attack = away.overall.gf_per_match
    home_concedes = home.overall.ga_per_match
    away_concedes = away.overall.ga_per_match

    bonus = 0
    pros = []

    if btts_rate >= 0.60:
        bonus += 5
        pros.append("v24 bonus: BTTS alto")

    if away_attack >= 1.30:
        bonus += 4
        pros.append("v24 bonus: ospite offensivo")

    if home_concedes >= 1.20 and away_concedes >= 1.20:
        bonus += 4
        pros.append("v24 bonus: entrambe concedono gol")

    if away_attack >= 1.20 and btts_rate >= 0.55:
        bonus += 4
        pros.append("v24 bonus: profilo partita aperta")

    final_score = min(100, round(base.score + bonus, 2))

    reason = base.reason
    if pros:
        reason += " || PRO V24: " + " | ".join(pros)

    return type(base)(
        score=final_score,
        band=_band(final_score),
        reason=reason,
        ranking_gap_score=base.ranking_gap_score,
        home_attack_score=base.home_attack_score,
        away_attack_score=base.away_attack_score,
        home_defense_weakness_score=base.home_defense_weakness_score,
        away_defense_weakness_score=base.away_defense_weakness_score,
        home_last10_over_score=base.home_last10_over_score,
        away_last10_over_score=base.away_last10_over_score,
        home_venue_over_score=base.home_venue_over_score,
        away_venue_over_score=base.away_venue_over_score,
        btts_profile_score=base.btts_profile_score,
    )