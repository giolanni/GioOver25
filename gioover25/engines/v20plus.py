"""
GioOver2.5 - Engine sperimentale v20plus

RUOLO
-----
v20plus è la versione "estesa" di v20.

Mantiene integralmente tutte le partite che v20 classifica già in ALTA e,
in aggiunta, promuove in ALTA un sottoinsieme molto selettivo delle
MEDIA-ALTA di v20.

REGOLA DI PROMOZIONE
--------------------
Una partita non ALTA in v20 viene promossa soltanto se TUTTE le condizioni
seguenti sono vere:

1. v20 la classifica MEDIA-ALTA;
2. lo score v20 è almeno 71;
3. v22 la classifica ALTA;
4. v25 la classifica ALTA.

Quindi:

    ALTA v20
        +
    MEDIA-ALTA v20 con score >= 71
    confermata ALTA sia da v22 sia da v25
        =
    ALTA v20plus

ORIGINE
-------
Questo engine corrisponde al precedente v20dev. Il rename serve a rendere
esplicita la funzione: "plus" = v20 originale più selezioni aggiuntive.

NOTA SPERIMENTALE
-----------------
La soglia 71 e la doppia conferma v22/v25 sono parametri congelati del test.
Non modificarli durante il periodo di osservazione prospettica.
"""

from dataclasses import replace

from . import v20
from gioover25.scoring_v22 import calculate_score_v22
from gioover25.scoring_v25 import calculate_score_v25

ENGINE_NAME = "v20plus"
ENGINE_VERSION = "2.0.plus1"

CANDIDATE_MIN_V20_SCORE = 71.0


def _band(value) -> str:
    return str(value or "").strip().upper()


def _candidate_diagnostics(v20_result, v22_result, v25_result) -> str:
    return (
        "V20PLUS_CANDIDATE["
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
