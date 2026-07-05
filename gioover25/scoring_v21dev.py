from dataclasses import dataclass


@dataclass
class ScoreV21DevResult:
    score: float
    band: str
    reason: str
    ranking_gap_score: float
    home_attack_score: float
    away_attack_score: float
    home_defense_weakness_score: float
    away_defense_weakness_score: float
    home_last10_over_score: float
    away_last10_over_score: float
    home_venue_over_score: float
    away_venue_over_score: float
    btts_profile_score: float


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _safe_rate(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _band(score: float) -> str:
    if score >= 75:
        return "ALTA"
    if score >= 60:
        return "MEDIA"
    return "BASSA"


def _attack_score(gf_per_match: float) -> float:
    return _clamp(gf_per_match / 2.2)


def _defense_weakness_score(ga_per_match: float) -> float:
    return _clamp(ga_per_match / 2.2)


def _last10_over_score(team) -> float:
    return _safe_rate(team.last10.over25, team.last10.played)


def _venue_over_score(venue_stats) -> float:
    return _safe_rate(venue_stats.over25, venue_stats.played)


def _btts_score(home, away) -> float:
    home_btts = _safe_rate(home.overall.btts, home.overall.played)
    away_btts = _safe_rate(away.overall.btts, away.overall.played)
    return (home_btts + away_btts) / 2


def _build_reason(
    home_attack_score,
    away_attack_score,
    home_defense_weakness_score,
    away_defense_weakness_score,
    home_last10_over_score,
    away_last10_over_score,
    home_venue_over_score,
    away_venue_over_score,
    btts_profile_score,
):
    pros = []
    cons = []

    if home_attack_score >= 0.65:
        pros.append("attacco casa positivo")
    else:
        cons.append("attacco casa non dominante")

    if away_attack_score >= 0.65:
        pros.append("attacco trasferta positivo")
    else:
        cons.append("ospite poco prolifico")

    if home_defense_weakness_score >= 0.65:
        pros.append("difesa casa vulnerabile")

    if away_defense_weakness_score >= 0.65:
        pros.append("difesa trasferta vulnerabile")

    if home_last10_over_score >= 0.60:
        pros.append("trend over recente casa")
    else:
        cons.append("trend over casa non forte")

    if away_last10_over_score >= 0.60:
        pros.append("trend over recente trasferta")
    else:
        cons.append("trend over trasferta non forte")

    if home_venue_over_score >= 0.60:
        pros.append("profilo over interno positivo")
    else:
        cons.append("profilo over interno debole")

    if away_venue_over_score >= 0.60:
        pros.append("profilo over esterno positivo")
    else:
        cons.append("profilo over esterno debole")

    if btts_profile_score >= 0.60:
        pros.append("alta tendenza BTTS")
    else:
        cons.append("BTTS non elevato")

    if not pros:
        pros.append("nessun indicatore over forte")

    if not cons:
        cons.append("nessun contro rilevante")

    return "PRO: " + " | ".join(pros) + " || CONTRO: " + " | ".join(cons)


def calculate_score_v21dev(match_stats, league_info):
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
        ranking_gap_score * 8
        + home_attack_score * 13
        + away_attack_score * 13
        + home_defense_weakness_score * 10
        + away_defense_weakness_score * 14
        + home_last10_over_score * 12
        + away_last10_over_score * 12
        + home_venue_over_score * 8
        + away_venue_over_score * 8
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
        ranking_gap_score=round(ranking_gap_score * 8, 2),
        home_attack_score=round(home_attack_score * 13, 2),
        away_attack_score=round(away_attack_score * 13, 2),
        home_defense_weakness_score=round(home_defense_weakness_score * 10, 2),
        away_defense_weakness_score=round(away_defense_weakness_score * 14, 2),
        home_last10_over_score=round(home_last10_over_score * 12, 2),
        away_last10_over_score=round(away_last10_over_score * 12, 2),
        home_venue_over_score=round(home_venue_over_score * 8, 2),
        away_venue_over_score=round(away_venue_over_score * 8, 2),
        btts_profile_score=round(btts_profile_score * 12, 2),
    )