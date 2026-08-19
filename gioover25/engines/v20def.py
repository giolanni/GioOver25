"""
GioOver2.5 - Engine sperimentale v20def

RUOLO
-----
v20def è v20 con una penalità aggiuntiva dedicata alla SOLIDITÀ DIFENSIVA
RECENTE, introdotta dopo gli esperimenti Strong Defense di agosto 2026.

BASE
----
Lo scoring di partenza è v20, senza modifiche ai suoi driver originali.

REGOLA STRONG-DEFENSE CONGELATA
-------------------------------
Se almeno una delle due squadre ha subito in media <= 1.60 gol nelle ultime
5 partite precedenti al match, vengono sottratti 3 punti allo score v20.

    metrica   = GA medio ultime 5
    regola    = almeno una difesa forte
    soglia    = <= 1.60
    penalità  = -3 punti

La penalità può declassare una partita ma non può crearne una nuova in ALTA.
Se una squadra non dispone di almeno 5 gare precedenti, il relativo valore è
None e quella squadra non attiva la condizione.

ORIGINE
-------
Questo engine corrisponde al precedente v202dev. Il nome "def" identifica
chiaramente la famiglia con filtro/penalità difensiva.

PARAMETRI
---------
I parametri sono congelati per il periodo prospettico e non vanno ritarati
quotidianamente. Saranno rivalutati con un nuovo backtest sul campione ampliato.
"""

from . import v20
from .defense_dev_utils import apply_defense_penalty

ENGINE_NAME = "v20def"
ENGINE_VERSION = "2.0.def1"
REQUIRES_DEFENSE_LAST5 = True

DEFENSE_RULE = "AT_LEAST_ONE_STRONG"
DEFENSE_THRESHOLD = 1.60
DEFENSE_PENALTY = 3.0


def calculate_score(
    match_stats,
    league_info,
    *,
    home_ga_last5=None,
    away_ga_last5=None,
):
    base = v20.calculate_score(match_stats, league_info)

    return apply_defense_penalty(
        base,
        home_ga_last5=home_ga_last5,
        away_ga_last5=away_ga_last5,
        rule=DEFENSE_RULE,
        threshold=DEFENSE_THRESHOLD,
        penalty=DEFENSE_PENALTY,
        label="V20DEF_STRONG_DEFENSE",
    )
