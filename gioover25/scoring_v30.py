from .scoring_v21dev import ScoreV21DevResult, _band


YOUNG_MIN_PLAYED = 7
YOUNG_MAX_PLAYED = 8
CORE_MIN_OVER_L5 = 0.70
CORE_MIN_DELTA_GF_L5 = 0.20
STRONG_MIN_DELTA_GF_L5 = 0.30
CORE_SCORE_FLOOR = 80.0
STRONG_SCORE_FLOOR = 90.0


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, float(value)))


def _avg(a: float, b: float) -> float:
    return (float(a) + float(b)) / 2.0


def _young_history_features(match_stats) -> dict[str, float | int | bool]:
    home = match_stats.home
    away = match_stats.away
    home_played = int(home.overall.played)
    away_played = int(away.overall.played)
    maturity = min(home_played, away_played)
    min_over_l5 = min(float(home.last5.over25_rate), float(away.last5.over25_rate))
    avg_gf_l5 = _avg(home.last5.gf_per_match, away.last5.gf_per_match)
    avg_gf_full = _avg(home.overall.gf_per_match, away.overall.gf_per_match)
    delta_gf_l5 = avg_gf_l5 - avg_gf_full
    young_band = YOUNG_MIN_PLAYED <= maturity <= YOUNG_MAX_PLAYED
    core = young_band and min_over_l5 >= CORE_MIN_OVER_L5 and delta_gf_l5 >= CORE_MIN_DELTA_GF_L5
    strong = core and delta_gf_l5 >= STRONG_MIN_DELTA_GF_L5
    return {"home_played": home_played, "away_played": away_played, "maturity": maturity,
            "min_over_l5": min_over_l5, "avg_gf_l5": avg_gf_l5, "avg_gf_full": avg_gf_full,
            "delta_gf_l5": delta_gf_l5, "young_band": young_band, "core": core, "strong": strong}


def _ranking_score(f) -> float:
    maturity_component = _clamp(1.0 - abs(float(f["maturity"]) - 7.5) / 7.5)
    over_component = _clamp(float(f["min_over_l5"]) / CORE_MIN_OVER_L5)
    gf_component = _clamp(float(f["avg_gf_l5"]) / 2.0)
    delta_component = _clamp((float(f["delta_gf_l5"]) + 0.40) / 0.60)
    raw = 0.15 * maturity_component + 0.40 * over_component + 0.25 * gf_component + 0.20 * delta_component
    return round(raw * 74.0, 2)


def calculate_score_v30(match_stats, league_info):
    """V30 autonomo: storico giovane, senza dipendenze da engine precedenti."""
    f = _young_history_features(match_stats)
    if f["strong"]:
        final_score, label = STRONG_SCORE_FLOOR, "STRONG"
    elif f["core"]:
        final_score, label = CORE_SCORE_FLOOR, "CORE"
    else:
        final_score, label = _ranking_score(f), "NO-SIGNAL"

    reason = (f"V30 {label}: maturity={f['maturity']} (home={f['home_played']}, away={f['away_played']}), "
              f"MinOverL5={f['min_over_l5']:.2f}, AvgGFL5={f['avg_gf_l5']:.2f}, "
              f"AvgGFFull={f['avg_gf_full']:.2f}, DeltaGFL5={f['delta_gf_l5']:+.2f}")
    return ScoreV21DevResult(score=round(final_score, 2), band=_band(final_score), reason=reason,
        ranking_gap_score=0.0, home_attack_score=0.0, away_attack_score=0.0,
        home_defense_weakness_score=0.0, away_defense_weakness_score=0.0,
        home_last10_over_score=0.0, away_last10_over_score=0.0,
        home_venue_over_score=0.0, away_venue_over_score=0.0, btts_profile_score=0.0)
