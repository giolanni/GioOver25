from dataclasses import replace

from .scoring_v21dev import _band
from .scoring_v25 import calculate_score_v25


YOUNG_MIN_PLAYED = 7
YOUNG_MAX_PLAYED = 8
CORE_MIN_OVER_L5 = 0.70
CORE_MIN_DELTA_GF_L5 = 0.20
STRONG_MIN_DELTA_GF_L5 = 0.30
CORE_SCORE_FLOOR = 80.0
STRONG_SCORE_FLOOR = 90.0
NON_TARGET_SCORE_CAP = 74.99


def _avg(a: float, b: float) -> float:
    return (float(a) + float(b)) / 2.0


def _young_history_features(match_stats) -> dict[str, float | int | bool]:
    home = match_stats.home
    away = match_stats.away

    home_played = int(home.overall.played)
    away_played = int(away.overall.played)
    maturity = min(home_played, away_played)

    min_over_l5 = min(
        float(home.last5.over25_rate),
        float(away.last5.over25_rate),
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
    core = (
        young_band
        and min_over_l5 >= CORE_MIN_OVER_L5
        and delta_gf_l5 >= CORE_MIN_DELTA_GF_L5
    )
    strong = core and delta_gf_l5 >= STRONG_MIN_DELTA_GF_L5

    return {
        "home_played": home_played,
        "away_played": away_played,
        "maturity": maturity,
        "min_over_l5": min_over_l5,
        "avg_gf_l5": avg_gf_l5,
        "avg_gf_full": avg_gf_full,
        "delta_gf_l5": delta_gf_l5,
        "young_band": young_band,
        "core": core,
        "strong": strong,
    }


def calculate_score_v30(match_stats, league_info):
    """
    V30: engine dedicato allo storico giovane.

    La fascia ALTA non viene ereditata dagli engine precedenti: viene concessa
    solo quando la partita rispetta il segnale validato sulla maturita 7-8:

    - entrambe le squadre con almeno 7 gare e la meno matura con non piu di 8;
    - almeno il 70% di Over 2.5 nelle ultime 5 per entrambe le squadre;
    - media GF L5 in crescita di almeno +0.20 rispetto alla media GF overall.

    Con crescita >= +0.30 il segnale viene trattato come STRONG.

    Lo score v25 resta la base numerica per mantenere confrontabilita e
    ordinamento; fuori dal segnale V30 viene pero limitato sotto 75, cosi ogni
    ALTA di V30 rappresenta esclusivamente la nuova logica.
    """
    base = calculate_score_v25(match_stats, league_info)
    f = _young_history_features(match_stats)

    if f["strong"]:
        final_score = max(float(base.score), STRONG_SCORE_FLOOR)
        label = "STRONG"
    elif f["core"]:
        final_score = max(float(base.score), CORE_SCORE_FLOOR)
        label = "CORE"
    else:
        final_score = min(float(base.score), NON_TARGET_SCORE_CAP)
        label = "NO-SIGNAL"

    reason = getattr(base, "reason", "")
    v30_reason = (
        f"V30 {label}: maturity={f['maturity']} "
        f"(home={f['home_played']}, away={f['away_played']}), "
        f"MinOverL5={f['min_over_l5']:.2f}, "
        f"AvgGFL5={f['avg_gf_l5']:.2f}, "
        f"AvgGFFull={f['avg_gf_full']:.2f}, "
        f"DeltaGFL5={f['delta_gf_l5']:+.2f}"
    )

    if reason:
        reason = f"{reason} || {v30_reason}"
    else:
        reason = v30_reason

    return replace(
        base,
        score=round(final_score, 2),
        band=_band(final_score),
        reason=reason,
    )
