from .scoring_v21dev import ScoreV21DevResult, _band


MIN_BTTS_FULL = 0.70
MIN_GF_L5 = 1.80
MAX_PPG_GAP_FULL = 1.00
MIN_OVER_FULL_TOP = 0.80

BASE_SCORE = 76.0
ALTA_SCORE = 85.0
TOP_SCORE = 92.0


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, float(value)))


def _btts_rate(summary) -> float:
    return float(summary.btts) / float(summary.played) if summary.played else 0.0


def _features(match_stats):
    home = match_stats.home
    away = match_stats.away

    home_btts_full = _btts_rate(home.overall)
    away_btts_full = _btts_rate(away.overall)
    home_btts_l5 = _btts_rate(home.last5)
    away_btts_l5 = _btts_rate(away.last5)

    min_btts_full = min(home_btts_full, away_btts_full)
    min_gf_l5 = min(float(home.last5.gf_per_match), float(away.last5.gf_per_match))
    min_over_full = min(float(home.overall.over25_rate), float(away.overall.over25_rate))
    ppg_gap_full = abs(float(home.ppg) - float(away.ppg))

    avg_btts_l5 = (home_btts_l5 + away_btts_l5) / 2.0
    avg_btts_full = (home_btts_full + away_btts_full) / 2.0
    delta_btts_l5 = avg_btts_l5 - avg_btts_full

    base = min_btts_full >= MIN_BTTS_FULL and min_gf_l5 >= MIN_GF_L5
    alta = base and ppg_gap_full <= MAX_PPG_GAP_FULL and delta_btts_l5 >= 0.0
    top = alta and min_over_full >= MIN_OVER_FULL_TOP

    level = "TOP" if top else "ALTA" if alta else "BASE" if base else "NO-SIGNAL"
    return {
        "min_btts_full": min_btts_full,
        "min_gf_l5": min_gf_l5,
        "min_over_full": min_over_full,
        "ppg_gap_full": ppg_gap_full,
        "delta_btts_l5": delta_btts_l5,
        "base": base,
        "alta": alta,
        "top": top,
        "level": level,
    }


def _goal_ranking_score(f) -> float:
    """Score continuo GOAL per ordinare anche le partite fuori dal CORE.

    Non usa alcun engine Over2.5. I pesi servono solo al ranking relativo dei
    NO-SIGNAL; le soglie BASE/ALTA/TOP restano quelle validate dal laboratorio.
    """
    btts_component = _clamp(f["min_btts_full"] / MIN_BTTS_FULL)
    gf_component = _clamp(f["min_gf_l5"] / MIN_GF_L5)
    ppg_component = _clamp(1.0 - f["ppg_gap_full"] / 2.0)
    delta_component = _clamp((f["delta_btts_l5"] + 0.30) / 0.60)
    over_component = _clamp(f["min_over_full"] / MIN_OVER_FULL_TOP)

    raw = (
        0.40 * btts_component
        + 0.35 * gf_component
        + 0.10 * ppg_component
        + 0.10 * delta_component
        + 0.05 * over_component
    )
    return round(raw * 74.0, 2)


def calculate_score_vg1(match_stats, league_info):
    """VG1: primo engine sperimentale autonomo per il mercato GOAL/BTTS.

    BASE: MinBTTSFull >= .70 e MinGFL5 >= 1.80
    ALTA: BASE + PPGGapFull <= 1.00 + DeltaBTTSL5 >= 0
    TOP:  ALTA + MinOverFull >= .80

    Nessuna dipendenza da scoring V20/V25 o altri engine Over2.5.
    """
    f = _features(match_stats)

    if f["top"]:
        score = TOP_SCORE
    elif f["alta"]:
        score = ALTA_SCORE
    elif f["base"]:
        score = BASE_SCORE
    else:
        score = _goal_ranking_score(f)

    reason = (
        f"VG1 {f['level']}: MinBTTSFull={f['min_btts_full']:.2f}, "
        f"MinGFL5={f['min_gf_l5']:.2f}, PPGGapFull={f['ppg_gap_full']:.2f}, "
        f"DeltaBTTSL5={f['delta_btts_l5']:+.2f}, MinOverFull={f['min_over_full']:.2f}"
    )

    # Mantiene il contratto ScoreResult atteso dalla pipeline. I campi legacy
    # non partecipano allo scoring VG1.
    return ScoreV21DevResult(
        score=round(score, 2),
        band=_band(score),
        reason=reason,
        ranking_gap_score=0.0,
        home_attack_score=0.0,
        away_attack_score=0.0,
        home_defense_weakness_score=0.0,
        away_defense_weakness_score=0.0,
        home_last10_over_score=0.0,
        away_last10_over_score=0.0,
        home_venue_over_score=0.0,
        away_venue_over_score=0.0,
        btts_profile_score=round(f["min_btts_full"] * 12.0, 2),
    )
