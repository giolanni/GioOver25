"""
GioOver2.5 - Engine sperimentale v20select

RUOLO
-----
v20select è un engine di SELEZIONE PURA.

Non rappresenta l'intero universo delle partite di v20: espone come ALTA
esclusivamente il sottoinsieme di MEDIA-ALTA v20 che soddisfa la regola di
conferma incrociata usata da v20plus.

REGOLA
------
Una partita viene esposta come ALTA solo se:

1. v20 = MEDIA-ALTA;
2. score v20 >= 71;
3. v22 = ALTA;
4. v25 = ALTA.

Tutte le altre partite vengono rese BASSA con score 0, perché lo scopo di
questo engine è misurare separatamente l'affidabilità del solo segmento
selezionato.

RELAZIONE CON v20plus
---------------------
    v20plus = ALTA originali v20 + ALTA individuate da v20select

ORIGINE
-------
Questo engine corrisponde al precedente v201dev. Il nome "select" rende
esplicito che non è una nuova generazione numerica di v20, ma un selettore.
"""

from dataclasses import replace

from . import v20
from .v20plus import (
    CANDIDATE_MIN_V20_SCORE,
    _band,
    _candidate_diagnostics,
    is_candidate,
)
from gioover25.scoring_v22 import calculate_score_v22
from gioover25.scoring_v25 import calculate_score_v25

ENGINE_NAME = "v20select"
ENGINE_VERSION = "2.0.select1"


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
                "V20SELECT_NOT_CANDIDATE || "
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
                "V20SELECT_NOT_CANDIDATE || "
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
            "V20SELECT_CANDIDATE || "
            + _candidate_diagnostics(
                base_v20,
                v22_result,
                v25_result,
            )
        ),
    )
