"""
GioOver2.5 - Engine sperimentale v20defplus

RUOLO
-----
v20defplus è il GEMELLO DIFENSIVO di v20plus.

Combina due componenti:

1. tutte le partite che v20def classifica già in ALTA;
2. le partite selezionate da v20defselect.

In altre parole:

    ALTA v20def
        +
    MEDIA-ALTA v20def con score >= 71
    confermata ALTA da v22def e v25def
        =
    ALTA v20defplus

BASE DI PARTENZA
----------------
La base è sempre v20def, non v20 originale. Questo è fondamentale perché la
famiglia defense deve essere perfettamente parallela alla famiglia originale:

    v20 + v20select -> v20plus
    v20def + v20defselect -> v20defplus

COMPORTAMENTO
-------------
- se v20def è già ALTA, la partita resta invariata;
- se v20def non è MEDIA-ALTA o ha score < 71, resta invariata;
- se è una candidata, vengono calcolati v22def e v25def;
- solo con doppia conferma ALTA viene promossa ad ALTA.

NOTA SPERIMENTALE
-----------------
Tutte le soglie e penalità sono congelate durante il periodo prospettico.
"""

from dataclasses import replace

from . import v20def, v22def, v25def
from .v20defselect import (
    CANDIDATE_MIN_V20DEF_SCORE,
    _band,
    _candidate_diagnostics,
    is_candidate,
)

ENGINE_NAME = "v20defplus"
ENGINE_VERSION = "2.0.defplus1"
REQUIRES_DEFENSE_LAST5 = True


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

    if _band(base_v20def.band) == "ALTA":
        return base_v20def

    if (
        _band(base_v20def.band) != "MEDIA-ALTA"
        or float(base_v20def.score) < CANDIDATE_MIN_V20DEF_SCORE
    ):
        return base_v20def

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
        return base_v20def

    diagnostic = _candidate_diagnostics(
        base_v20def,
        v22def_result,
        v25def_result,
    )

    original_reason = str(
        getattr(base_v20def, "reason", "") or ""
    ).strip()

    return replace(
        base_v20def,
        band="ALTA",
        reason=(
            f"{original_reason} || V20DEFPLUS_PROMOTED || {diagnostic}"
            if original_reason
            else f"V20DEFPLUS_PROMOTED || {diagnostic}"
        ),
    )
