from dataclasses import replace

from .scoring_v21dev import _band
from .scoring_v25 import calculate_score_v25


YOUNG_MIN_PLAYED = 7
YOUNG_MAX_PLAYED = 8
MIN_OVER_L5 = 0.70
MIN_GF_FULL = 1.40
BOOST_DELTA_GF_L5 = 0.20
STRONG_DELTA_GF_L5 = 0.30

BASE_SCORE_FLOOR = 80.0
BOOST_SCORE_FLOOR = 85.0
STRONG_SCORE_FLOOR = 90.0
NON_TARGET_SCORE_CAP = 74.99


def _avg(a: float, b: float) -> float:
    return (float(a) + float(b)) / 2.0


def _young_history_features(match_stats) -> dict[str, float | int | bool | str]:
    home = match_stats.home
    away = match_stats.away

    home_played = int(home.overall.played)
    away_played = int(away.overall.played)
    maturity = min(home_played, away_played)

    min_over_l5 = min(
        float(home.last5.over25_rate),
        float(away.last5.over25_rate),
    )
    min_gf_full = min(
        float(home.overall.gf_per_match),
        float(away.overall.gf_per_match),
    )

    avg_gf_l5 = _avg(
        home.last5.gf_per_match,
        away.last5.gf_per_match,
    )
    avg_gf_full = _avg(
        home.overall.gf_per_match,
        away.overall.gf_per_match,
    )
    delta_gf_l5 = avg_gf_l5 - avg_gf_full

    young_band = YOUNG_MIN_PLAYED <= maturity <= YOUNG_MAX_PLAYED

    base_signal = (
        young_band
        and min_over_l5 >= MIN_OVER_L5
        and min_gf_full >= MIN_GF_FULL
    )
    boost_signal = base_signal and delta_gf_l5 >= BOOST_DELTA_GF_L5
    strong_signal = base_signal and delta_gf_l5 >= STRONG_DELTA_GF_L5

    if strong_signal:
        level = "STRONG"
    elif boost_signal:
        level = "BOOST"
    elif base_signal:
        level = "BASE"
    else:
        level = "NO-SIGNAL"

    return {
        "home_played": home_played,
        "away_played": away_played,
        "maturity": maturity,
        "min_over_l5": min_over_l5,
        "min_gf_full": min_gf_full,
        "avg_gf_l5": avg_gf_l5,
        "avg_gf_full": avg_gf_full,
        "delta_gf_l5": delta_gf_l5,
        "young_band": young_band,
        "base_signal": base_signal,
        "boost_signal": boost_signal,
        "strong_signal": strong_signal,
        "level": level,
    }


def calculate_score_v31(match_stats, league_info):
    """
    V31: variante di V30 che NON richiede DeltaGF per entrare in ALTA.

    Segnale BASE:
    - maturita 7-8;
    - MinOverL5 >= 0.70;
    - MinGFFull >= 1.40.

    DeltaGF diventa soltanto un rafforzativo:
    - BASE   -> score minimo 80;
    - BOOST  -> DeltaGFL5 >= +0.20, score minimo 85;
    - STRONG -> DeltaGFL5 >= +0.30, score minimo 90.

    Fuori dal segnale V31 lo score viene limitato sotto 75, quindi ogni ALTA
    rappresenta esclusivamente la logica V31. V30 resta invariato per il
    confronto temporale tra Delta obbligatorio e Delta rafforzativo.
    """
    base = calculate_score_v25(match_stats, league_info)
    f = _young_history_features(match_stats)

    if f["strong_signal"]:
        final_score = max(float(base.score), STRONG_SCORE_FLOOR)
    elif f["boost_signal"]:
        final_score = max(float(base.score), BOOST_SCORE_FLOOR)
    elif f["base_signal"]:
        final_score = max(float(base.score), BASE_SCORE_FLOOR)
    else:
        final_score = min(float(base.score), NON_TARGET_SCORE_CAP)

    reason = getattr(base, "reason", "")
    v31_reason = (
        f"V31 {f['level']}: maturity={f['maturity']} "
        f"(home={f['home_played']}, away={f['away_played']}), "
        f"MinOverL5={f['min_over_l5']:.2f}, "
        f"MinGFFull={f['min_gf_full']:.2f}, "
        f"AvgGFL5={f['avg_gf_l5']:.2f}, "
        f"AvgGFFull={f['avg_gf_full']:.2f}, "
        f"DeltaGFL5={f['delta_gf_l5']:+.2f}"
    )

    if reason:
        reason = f"{reason} || {v31_reason}"
    else:
        reason = v31_reason

    return replace(
        base,
        score=round(final_score, 2),
        band=_band(final_score),
        reason=reason,
    )
