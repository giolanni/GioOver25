"""
GioOver2.5 - Engine sperimentale v20defplus_v2

Variante sperimentale della famiglia v20 strong-defense.

Regola di promozione:
- mantiene invariate tutte le ALTA di v20def;
- considera solo le MEDIA-ALTA di v20def;
- promuove ad ALTA se contemporaneamente:
    v20def score >= 70
    v22def score >= 80
    v25def score >= 80

Questa variante usa quindi soglie numeriche esplicite 70/80/80 e non la
logica originaria di v20defselect/v20defplus basata sulla doppia conferma di
fascia ALTA.
"""

from dataclasses import replace

from . import v20def, v22def, v25def

ENGINE_NAME = "v20defplus_v2"
ENGINE_VERSION = "2.0.defplus2"
REQUIRES_DEFENSE_LAST5 = True

MIN_V20DEF_SCORE = 70.0
MIN_V22DEF_SCORE = 80.0
MIN_V25DEF_SCORE = 80.0


def _band(value) -> str:
    return str(value or "").strip().upper()


def calculate_score(
    match_stats,
    league_info,
    *,
    home_ga_last5=None,
    away_ga_last5=None,
):
    kwargs = {
        "home_ga_last5": home_ga_last5,
        "away_ga_last5": away_ga_last5,
    }

    base_v20def = v20def.calculate_score(match_stats, league_info, **kwargs)

    # Le ALTA originali di v20def restano sempre ALTA.
    if _band(base_v20def.band) == "ALTA":
        return base_v20def

    # Il plus lavora solo sul segmento MEDIA-ALTA di v20def.
    if (
        _band(base_v20def.band) != "MEDIA-ALTA"
        or float(base_v20def.score) < MIN_V20DEF_SCORE
    ):
        return base_v20def

    v22def_result = v22def.calculate_score(match_stats, league_info, **kwargs)
    v25def_result = v25def.calculate_score(match_stats, league_info, **kwargs)

    if not (
        float(v22def_result.score) >= MIN_V22DEF_SCORE
        and float(v25def_result.score) >= MIN_V25DEF_SCORE
    ):
        return base_v20def

    diagnostic = (
        "V20DEFPLUS_V2_PROMOTED["
        f"V20DEFScore={float(base_v20def.score):.2f};"
        f"V22DEFScore={float(v22def_result.score):.2f};"
        f"V25DEFScore={float(v25def_result.score):.2f};"
        f"Thresholds={MIN_V20DEF_SCORE:.0f}/{MIN_V22DEF_SCORE:.0f}/{MIN_V25DEF_SCORE:.0f}"
        "]"
    )

    original_reason = str(getattr(base_v20def, "reason", "") or "").strip()

    return replace(
        base_v20def,
        band="ALTA",
        reason=(
            f"{original_reason} || {diagnostic}"
            if original_reason
            else diagnostic
        ),
    )
