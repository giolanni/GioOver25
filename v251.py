"""
===============================================================================
GioOver2.5 - engines/v251.py
===============================================================================

Wrapper ufficiale dell'engine sperimentale v251.

La logica di scoring è contenuta in `gioover25.scoring_v251`; questo file rende
il motore disponibile alla factory e quindi ai comandi:

    python -m gioover25.rank_matches_v2 ... --engine v251
    python -m gioover25.rank_matches_v2 ... --engine all
===============================================================================
"""

from gioover25.scoring_v251 import calculate_score_v251


ENGINE_NAME = "v251"
ENGINE_VERSION = "2.5.1-experimental"



def calculate_score(match_stats, league_info):
    """Delega il calcolo alla funzione principale della v251."""

    return calculate_score_v251(match_stats, league_info)
