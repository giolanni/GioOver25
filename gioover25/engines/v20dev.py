"""
GioOver2.5 - Engine sperimentale v20dev

Regola candidata congelata:
- v20 Band = MEDIA-ALTA
- v20 Score >= 71
- v22 Band = ALTA
- v25 Band = ALTA

v20dev mantiene tutte le ALTA originali v20 e promuove in ALTA i candidati.
"""

from dataclasses import replace

from . import v20
from gioover25.scoring_v22 import calculate_score_v22
from gioover25.scoring_v25 import calculate_score_v25

ENGINE_NAME = "v20dev"
ENGINE_VERSION = "2.0.dev1"

CANDIDATE_MIN_V20_SCORE = 71.0


def _band(value) -> str:
    return str(value or "").strip().upper()


def _candidate_diagnostics(v20_result, v22_result, v25_result) -> str:
    return (
        "V20DEV_CANDIDATE["
        f"V20Score={float(v20_result.score):.2f};"
        f"V20Band={_band(v20_result.band)};"
        f"V22Score={float(v22_result.score):.2f};"
        f"V22Band={_band(v22_result.band)};"
        f"V25Score={float(v25_result.score):.2f};"
        f"V25Band={_band(v25_result.band)};"
        f"MinV20Score={CANDIDATE_MIN_V20_SCORE:.2f}"
        "]"
    )


def is_candidate(v20_result, v22_result, v25_result) -> bool:
    return (
        _band(v20_result.band) == "MEDIA-ALTA"
        and float(v20_result.score) >= CANDIDATE_MIN_V20_SCORE
        and _band(v22_result.band) == "ALTA"
        and _band(v25_result.band) == "ALTA"
    )


def calculate_score(match_stats, league_info):
    base_v20 = v20.calculate_score(match_stats, league_info)

    if _band(base_v20.band) == "ALTA":
        return base_v20

    if (
        _band(base_v20.band) != "MEDIA-ALTA"
        or float(base_v20.score) < CANDIDATE_MIN_V20_SCORE
    ):
        return base_v20

    v22_result = calculate_score_v22(match_stats, league_info)
    v25_result = calculate_score_v25(match_stats, league_info)

    if not is_candidate(base_v20, v22_result, v25_result):
        return base_v20

    diagnostic = _candidate_diagnostics(
        base_v20,
        v22_result,
        v25_result,
    )

    original_reason = str(
        getattr(base_v20, "reason", "") or ""
    ).strip()

    return replace(
        base_v20,
        band="ALTA",
        reason=(
            f"{original_reason} || {diagnostic}"
            if original_reason
            else diagnostic
        ),
    )
