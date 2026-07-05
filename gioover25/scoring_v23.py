from gioover25.scoring_v22 import calculate_score_v22
from gioover25.scoring_v21dev import ScoreV21DevResult, _band


def _safe_rate(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def calculate_score_v23(match_stats, league_info):
    base = calculate_score_v22(match_stats, league_info)

    home = match_stats.home
    away = match_stats.away

    away_attack = away.overall.gf_per_match
    btts_rate = (
        _safe_rate(home.overall.btts, home.overall.played)
        + _safe_rate(away.overall.btts, away.overall.played)
    ) / 2

    penalty = 0
    cons = []

    if base.score >= 85 and away_attack < 1.10:
        penalty += 6
        cons.append("v23 penalità: ospite poco prolifico su score alto")

    if base.score >= 85 and btts_rate < 0.50:
        penalty += 6
        cons.append("v23 penalità: BTTS basso su score alto")

    if base.score >= 90 and away_attack < 1.00 and btts_rate < 0.50:
        penalty += 5
        cons.append("v23 penalità extra: rischio partita a senso unico")

    final_score = max(0, round(base.score - penalty, 2))

    reason = base.reason
    if cons:
        reason += " || CONTRO V23: " + " | ".join(cons)

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