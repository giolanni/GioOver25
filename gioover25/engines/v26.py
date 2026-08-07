"""
===============================================================================
GioOver2.5 - Engine v26
===============================================================================

BASE
----
v26 mantiene IDENTICO lo scoring di v25.

NOVITA'
-------
Aggiunge un solo driver contestuale PROX basato sull'equilibrio PPG.

La fascia viene riclassificata quando:
- entrambe le squadre hanno almeno 10 partite giocate;
- differenza PPG <= 0.30.

Trasformazioni:
- ALTA  -> PROX-ALTA
- MEDIA -> PROX-MEDIA
- BASSA resta BASSA

Lo score numerico NON viene modificato.
===============================================================================
"""

from gioover25.scoring_v25 import calculate_score_v25


ENGINE_NAME = "v26"
ENGINE_VERSION = "2.6.0"

PROX_ENABLED = True
PROX_MIN_MATCHES = 10
PROX_PPG_THRESHOLD = 0.30


def calculate_score(match_stats, league_info):
    """Usa esattamente lo scoring v25."""
    return calculate_score_v25(
        match_stats,
        league_info,
    )


def apply_contextual_band(
    base_band: str,
    *,
    home_played: int,
    away_played: int,
    home_ppg: float,
    away_ppg: float,
) -> str:
    """
    Applica esclusivamente il driver contestuale PROX.

    Non modifica lo score.
    """

    band = str(base_band or "").strip().upper()

    if not PROX_ENABLED:
        return band

    if (
        home_played < PROX_MIN_MATCHES
        or away_played < PROX_MIN_MATCHES
    ):
        return band

    ppg_gap = abs(
        float(home_ppg)
        - float(away_ppg)
    )

    if ppg_gap > PROX_PPG_THRESHOLD:
        return band

    if band == "ALTA":
        return "PROX-ALTA"

    if band == "MEDIA":
        return "PROX-MEDIA"

    return band
