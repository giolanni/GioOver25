"""
v26dev = v26 + strong-defense penalty.

Mantiene anche il PROX originale di v26.

Configurazione congelata 16/08/2026:
- Last5 GA
- almeno una difesa <= 1.20
- penalità -14
"""
from . import v26
from .defense_dev_utils import apply_defense_penalty

ENGINE_NAME = "v26dev"
ENGINE_VERSION = "2.6.dev-defense1"
REQUIRES_DEFENSE_LAST5 = True

DEFENSE_RULE = "AT_LEAST_ONE_STRONG"
DEFENSE_THRESHOLD = 1.20
DEFENSE_PENALTY = 14.0


def calculate_score(match_stats, league_info, *, home_ga_last5=None, away_ga_last5=None):
    base = v26.calculate_score(match_stats, league_info)
    return apply_defense_penalty(
        base,
        home_ga_last5=home_ga_last5,
        away_ga_last5=away_ga_last5,
        rule=DEFENSE_RULE,
        threshold=DEFENSE_THRESHOLD,
        penalty=DEFENSE_PENALTY,
        label="V26DEV_STRONG_DEFENSE",
    )


def apply_contextual_band(
    base_band: str,
    *,
    home_played: int,
    away_played: int,
    home_ppg: float,
    away_ppg: float,
) -> str:
    return v26.apply_contextual_band(
        base_band,
        home_played=home_played,
        away_played=away_played,
        home_ppg=home_ppg,
        away_ppg=away_ppg,
    )
