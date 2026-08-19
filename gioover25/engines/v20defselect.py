"""
GioOver2.5 - Engine sperimentale v20defselect

RUOLO
-----
v20defselect è il GEMELLO DIFENSIVO di v20select.

È un engine di SELEZIONE PURA: non espone tutte le partite di v20def, ma
soltanto il sottoinsieme che soddisfa una conferma incrociata tra gli engine
della famiglia strong-defense.

BASE DI PARTENZA
----------------
La partita deve prima appartenere a v20def, NON a v20 originale.

REGOLA
------
Una partita viene esposta come ALTA solo se TUTTE le condizioni sono vere:

1. v20def = MEDIA-ALTA;
2. score v20def >= 71;
3. v22def = ALTA;
4. v25def = ALTA.

Quindi:

    MEDIA-ALTA v20def con score >= 71
        +
    conferma ALTA v22def
        +
    conferma ALTA v25def
        =
    ALTA v20defselect

Tutte le altre partite vengono rese BASSA con score 0, perché lo scopo è
misurare separatamente l'affidabilità di questo solo segmento.

RELAZIONE CON v20defplus
------------------------
    v20defplus = ALTA originali v20def + ALTA individuate da v20defselect

NOTA SPERIMENTALE
-----------------
La soglia 71 e i parametri strong-defense dei tre engine coinvolti sono
congelati per consentire un confronto prospettico pulito.
"""

from dataclasses import replace

from . import v20def, v22def, v25def

ENGINE_NAME = "v20defselect"
ENGINE_VERSION = "2.0.defselect1"
REQUIRES_DEFENSE_LAST5 = True

CANDIDATE_MIN_V20DEF_SCORE = 71.0


def _band(value) -> str:
    return str(value or "").strip().upper()


def _candidate_diagnostics(v20def_result, v22def_result, v25def_result) -> str:
    return (
        "V20DEFSELECT_CANDIDATE["
        f"V20DEFScore={float(v20def_result.score):.2f};"
        f"V20DEFBand={_band(v20def_result.band)};"
        f"V22DEFScore={float(v22def_result.score):.2f};"
        f"V22DEFBand={_band(v22def_result.band)};"
        f"V25DEFScore={float(v25def_result.score):.2f};"
        f"V25DEFBand={_band(v25def_result.band)};"
        f"MinV20DEFScore={CANDIDATE_MIN_V20DEF_SCORE:.2f}"
        "]"
    )


def is_candidate(v20def_result, v22def_result, v25def_result) -> bool:
    return (
        _band(v20def_result.band) == "MEDIA-ALTA"
        and float(v20def_result.score) >= CANDIDATE_MIN_V20DEF_SCORE
        and _band(v22def_result.band) == "ALTA"
        and _band(v25def_result.band) == "ALTA"
    )


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

    base_v20def = v20def.calculate_score(
        match_stats,
        league_info,
        **kwargs,
    )

    if (
        _band(base_v20def.band) != "MEDIA-ALTA"
        or float(base_v20def.score) < CANDIDATE_MIN_V20DEF_SCORE
    ):
        return replace(
            base_v20def,
            score=0.0,
            band="BASSA",
            reason=(
                "V20DEFSELECT_NOT_CANDIDATE || "
                f"OriginalV20DEFScore={float(base_v20def.score):.2f};"
                f"OriginalV20DEFBand={_band(base_v20def.band)}"
            ),
        )

    v22def_result = v22def.calculate_score(
        match_stats,
        league_info,
        **kwargs,
    )
    v25def_result = v25def.calculate_score(
        match_stats,
        league_info,
        **kwargs,
    )

    if not is_candidate(base_v20def, v22def_result, v25def_result):
        return replace(
            base_v20def,
            score=0.0,
            band="BASSA",
            reason=(
                "V20DEFSELECT_NOT_CANDIDATE || "
                + _candidate_diagnostics(
                    base_v20def,
                    v22def_result,
                    v25def_result,
                )
            ),
        )

    return replace(
        base_v20def,
        band="ALTA",
        reason=(
            "V20DEFSELECT_CANDIDATE || "
            + _candidate_diagnostics(
                base_v20def,
                v22def_result,
                v25def_result,
            )
        ),
    )
