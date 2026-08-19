"""
GioOver2.5 - Engine sperimentale v26def

RUOLO
-----
v26def è v26 con una penalità aggiuntiva per la forza difensiva recente.

BASE
----
Mantiene integralmente v26, compreso il driver contestuale PROX.

REGOLA STRONG-DEFENSE CONGELATA
-------------------------------
Se almeno una delle due squadre ha subito in media <= 1.20 gol nelle ultime
5 partite precedenti, vengono sottratti 14 punti allo score v26.

    metrica   = GA medio ultime 5
    regola    = almeno una difesa forte
    soglia    = <= 1.20
    penalità  = -14 punti

La penalità può declassare una partita ma non crearne una nuova in ALTA.

ORIGINE
-------
Questo engine corrisponde al precedente v26dev.

PARAMETRI
---------
Soglia e penalità restano congelate durante il periodo prospettico.
"""

from . import v26
from .defense_dev_utils import apply_defense_penalty

ENGINE_NAME = "v26def"
ENGINE_VERSION = "2.6.def1"
REQUIRES_DEFENSE_LAST5 = True

DEFENSE_RULE = "AT_LEAST_ONE_STRONG"
DEFENSE_THRESHOLD = 1.20
DEFENSE_PENALTY = 14.0


def calculate_score(
    match_stats,
    league_info,
    *,
    home_ga_last5=None,
    away_ga_last5=None,
):
    base = v26.calculate_score(match_stats, league_info)

    return apply_defense_penalty(
        base,
        home_ga_last5=home_ga_last5,
        away_ga_last5=away_ga_last5,
        rule=DEFENSE_RULE,
        threshold=DEFENSE_THRESHOLD,
        penalty=DEFENSE_PENALTY,
        label="V26DEF_STRONG_DEFENSE",
    )


def apply_contextual_band(
    base_band: str,
    *,
    home_played: int,
    away_played: int,
    home_ppg: float,
    away_ppg: float,
) -> str:
    """Mantiene identica la logica PROX dell'engine v26 ufficiale."""
    return v26.apply_contextual_band(
        base_band,
        home_played=home_played,
        away_played=away_played,
        home_ppg=home_ppg,
        away_ppg=away_ppg,
    )
