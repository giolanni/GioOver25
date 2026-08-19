"""
GioOver2.5 - Engine sperimentale v22def

RUOLO
-----
v22def è v22 con una penalità aggiuntiva per la forza difensiva recente
della squadra OSPITE.

BASE
----
Lo scoring base è v22.

REGOLA STRONG-DEFENSE CONGELATA
-------------------------------
Se la squadra ospite ha subito in media <= 1.60 gol nelle ultime 5 partite
precedenti, vengono sottratti 13 punti allo score v22.

    metrica   = Away GA medio ultime 5
    regola    = difesa ospite forte
    soglia    = <= 1.60
    penalità  = -13 punti

La regola nasce dal secondo esperimento Strong Defense, dove questo profilo
ha mostrato una riduzione consistente dell'affidabilità delle ALTA v22.
La penalità può soltanto declassare partite già forti; non crea nuove ALTA.

ORIGINE
-------
Questo engine corrisponde al precedente v22dev.

PARAMETRI
---------
Soglia e penalità sono congelate per il periodo di osservazione prospettica.
"""

from . import v22
from .defense_dev_utils import apply_defense_penalty

ENGINE_NAME = "v22def"
ENGINE_VERSION = "2.2.def1"
REQUIRES_DEFENSE_LAST5 = True

DEFENSE_RULE = "AWAY_STRONG"
DEFENSE_THRESHOLD = 1.60
DEFENSE_PENALTY = 13.0


def calculate_score(
    match_stats,
    league_info,
    *,
    home_ga_last5=None,
    away_ga_last5=None,
):
    base = v22.calculate_score(match_stats, league_info)

    return apply_defense_penalty(
        base,
        home_ga_last5=home_ga_last5,
        away_ga_last5=away_ga_last5,
        rule=DEFENSE_RULE,
        threshold=DEFENSE_THRESHOLD,
        penalty=DEFENSE_PENALTY,
        label="V22DEF_STRONG_DEFENSE",
    )
