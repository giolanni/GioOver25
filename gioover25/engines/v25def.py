"""
GioOver2.5 - Engine sperimentale v25def

RUOLO
-----
v25def è v25 con una penalità aggiuntiva per la forza difensiva recente
della squadra OSPITE.

BASE
----
Lo scoring base è v25, quindi mantiene integralmente la logica v25 e le sue
penalità contestuali originarie.

REGOLA STRONG-DEFENSE CONGELATA
-------------------------------
Se la squadra ospite ha subito in media <= 1.60 gol nelle ultime 5 partite
precedenti, vengono sottratti 13 punti allo score v25.

    metrica   = Away GA medio ultime 5
    regola    = difesa ospite forte
    soglia    = <= 1.60
    penalità  = -13 punti

La penalità è stata scelta dal secondo esperimento Strong Defense. Può
soltanto ridurre lo score e quindi declassare una partita; non crea nuove ALTA.

ORIGINE
-------
Questo engine corrisponde al precedente v25dev.

PARAMETRI
---------
Soglia e penalità sono congelate durante il periodo prospettico.
"""

from . import v25
from .defense_dev_utils import apply_defense_penalty

ENGINE_NAME = "v25def"
ENGINE_VERSION = "2.5.def1"
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
    base = v25.calculate_score(match_stats, league_info)

    return apply_defense_penalty(
        base,
        home_ga_last5=home_ga_last5,
        away_ga_last5=away_ga_last5,
        rule=DEFENSE_RULE,
        threshold=DEFENSE_THRESHOLD,
        penalty=DEFENSE_PENALTY,
        label="V25DEF_STRONG_DEFENSE",
    )
