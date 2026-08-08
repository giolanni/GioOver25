"""
GioOver2.5 - Engine sperimentale v201dev

Espone come ALTA esclusivamente i candidati della regola v20dev.
Le altre partite vengono rese BASSA con score 0.
"""

from dataclasses import replace

from . import v20
from .v20dev import (
    CANDIDATE_MIN_V20_SCORE,
    _band,
    _candidate_diagnostics,
    is_candidate,
)
from gioover25.scoring_v22 import calculate_score_v22
from gioover25.scoring_v25 import calculate_score_v25

ENGINE_NAME = "v201dev"
ENGINE_VERSION = "2.0.1.dev1"


def calculate_score(match_stats, league_info):
    base_v20 = v20.calculate_score(match_stats, league_info)

    if (
        _band(base_v20.band) != "MEDIA-ALTA"
        or float(base_v20.score) < CANDIDATE_MIN_V20_SCORE
    ):
        return replace(
            base_v20,
            score=0.0,
            band="BASSA",
            reason=(
                "V201DEV_NOT_CANDIDATE || "
                f"OriginalV20Score={float(base_v20.score):.2f};"
                f"OriginalV20Band={_band(base_v20.band)}"
            ),
        )

    v22_result = calculate_score_v22(match_stats, league_info)
    v25_result = calculate_score_v25(match_stats, league_info)

    if not is_candidate(base_v20, v22_result, v25_result):
        return replace(
            base_v20,
            score=0.0,
            band="BASSA",
            reason=(
                "V201DEV_NOT_CANDIDATE || "
                + _candidate_diagnostics(
                    base_v20,
                    v22_result,
                    v25_result,
                )
            ),
        )

    return replace(
        base_v20,
        band="ALTA",
        reason=(
            "V201DEV_CANDIDATE || "
            + _candidate_diagnostics(
                base_v20,
                v22_result,
                v25_result,
            )
        ),
    )
