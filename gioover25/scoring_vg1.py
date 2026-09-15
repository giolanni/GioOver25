from dataclasses import replace

from .scoring_v21dev import _band
from .scoring_v25 import calculate_score_v25


MIN_BTTS_FULL = 0.70
MIN_GF_L5 = 1.80
MAX_PPG_GAP_FULL = 1.00
MIN_OVER_FULL_TOP = 0.80

BASE_SCORE = 76.0
ALTA_SCORE = 85.0
TOP_SCORE = 92.0
NON_TARGET_SCORE_CAP = 74.99


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


def calculate_score_vg1(match_stats, league_info):
    """VG1: primo engine sperimentale dedicato al mercato GOAL/BTTS.

    Ricerca storica anti-lookahead:
      BASE: MinBTTSFull >= .70 e MinGFL5 >= 1.80
      ALTA: BASE + PPGGapFull <= 1.00 + DeltaBTTSL5 >= 0
      TOP:  ALTA + MinOverFull >= .80

    TOP resta un booster sperimentale; ALTA e il segnale principale da validare
    su prediction future. Lo scoring v25 viene usato soltanto come contenitore
    compatibile con la pipeline esistente, non come logica di selezione GOAL.
    """
    base_score = calculate_score_v25(match_stats, league_info)
    f = _features(match_stats)

    if f["top"]:
        score = TOP_SCORE
    elif f["alta"]:
        score = ALTA_SCORE
    elif f["base"]:
        score = BASE_SCORE
    else:
        score = min(float(base_score.score), NON_TARGET_SCORE_CAP)

    vg_reason = (
        f"VG1 {f['level']}: MinBTTSFull={f['min_btts_full']:.2f}, "
        f"MinGFL5={f['min_gf_l5']:.2f}, PPGGapFull={f['ppg_gap_full']:.2f}, "
        f"DeltaBTTSL5={f['delta_btts_l5']:+.2f}, MinOverFull={f['min_over_full']:.2f}"
    )

    return replace(
        base_score,
        score=round(score, 2),
        band=_band(score),
        reason=vg_reason,
    )
