from .scoring_v21dev import ScoreV21DevResult, _band

YOUNG_MIN_PLAYED = 7
YOUNG_MAX_PLAYED = 8
MIN_OVER_L5 = 0.70
MIN_GF_FULL = 1.40
BOOST_DELTA_GF_L5 = 0.20
STRONG_DELTA_GF_L5 = 0.30
BASE_SCORE_FLOOR = 80.0
BOOST_SCORE_FLOOR = 85.0
STRONG_SCORE_FLOOR = 90.0


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, float(value)))


def _avg(a: float, b: float) -> float:
    return (float(a) + float(b)) / 2.0


def _young_history_features(match_stats):
    home, away = match_stats.home, match_stats.away
    home_played, away_played = int(home.overall.played), int(away.overall.played)
    maturity = min(home_played, away_played)
    min_over_l5 = min(float(home.last5.over25_rate), float(away.last5.over25_rate))
    min_gf_full = min(float(home.overall.gf_per_match), float(away.overall.gf_per_match))
    avg_gf_l5 = _avg(home.last5.gf_per_match, away.last5.gf_per_match)
    avg_gf_full = _avg(home.overall.gf_per_match, away.overall.gf_per_match)
    delta_gf_l5 = avg_gf_l5 - avg_gf_full
    young_band = YOUNG_MIN_PLAYED <= maturity <= YOUNG_MAX_PLAYED
    base_signal = young_band and min_over_l5 >= MIN_OVER_L5 and min_gf_full >= MIN_GF_FULL
    boost_signal = base_signal and delta_gf_l5 >= BOOST_DELTA_GF_L5
    strong_signal = base_signal and delta_gf_l5 >= STRONG_DELTA_GF_L5
    level = "STRONG" if strong_signal else "BOOST" if boost_signal else "BASE" if base_signal else "NO-SIGNAL"
    return {"home_played": home_played, "away_played": away_played, "maturity": maturity,
            "min_over_l5": min_over_l5, "min_gf_full": min_gf_full, "avg_gf_l5": avg_gf_l5,
            "avg_gf_full": avg_gf_full, "delta_gf_l5": delta_gf_l5, "young_band": young_band,
            "base_signal": base_signal, "boost_signal": boost_signal, "strong_signal": strong_signal,
            "level": level}


def _ranking_score(f) -> float:
    maturity_component = _clamp(1.0 - abs(float(f["maturity"]) - 7.5) / 7.5)
    over_component = _clamp(float(f["min_over_l5"]) / MIN_OVER_L5)
    gf_component = _clamp(float(f["min_gf_full"]) / MIN_GF_FULL)
    delta_component = _clamp((float(f["delta_gf_l5"]) + 0.40) / 0.70)
    raw = 0.15 * maturity_component + 0.40 * over_component + 0.30 * gf_component + 0.15 * delta_component
    return round(raw * 74.0, 2)


def calculate_score_v31(match_stats, league_info):
    """V31 autonomo: DeltaGF e un rafforzativo, senza dipendenze da altri engine."""
    f = _young_history_features(match_stats)
    if f["strong_signal"]:
        final_score = STRONG_SCORE_FLOOR
    elif f["boost_signal"]:
        final_score = BOOST_SCORE_FLOOR
    elif f["base_signal"]:
        final_score = BASE_SCORE_FLOOR
    else:
        final_score = _ranking_score(f)

    reason = (f"V31 {f['level']}: maturity={f['maturity']} (home={f['home_played']}, away={f['away_played']}), "
              f"MinOverL5={f['min_over_l5']:.2f}, MinGFFull={f['min_gf_full']:.2f}, "
              f"AvgGFL5={f['avg_gf_l5']:.2f}, AvgGFFull={f['avg_gf_full']:.2f}, "
              f"DeltaGFL5={f['delta_gf_l5']:+.2f}")
    return ScoreV21DevResult(score=round(final_score, 2), band=_band(final_score), reason=reason,
        ranking_gap_score=0.0, home_attack_score=0.0, away_attack_score=0.0,
        home_defense_weakness_score=0.0, away_defense_weakness_score=0.0,
        home_last10_over_score=0.0, away_last10_over_score=0.0,
        home_venue_over_score=0.0, away_venue_over_score=0.0, btts_profile_score=0.0)
