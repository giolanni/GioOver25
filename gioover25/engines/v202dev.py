"""
v202dev = v20 + strong-defense penalty.

Configurazione congelata 16/08/2026:
- Last5 GA
- almeno una difesa <= 1.60
- penalità -3
"""
from . import v20
from .defense_dev_utils import apply_defense_penalty

ENGINE_NAME = "v202dev"
ENGINE_VERSION = "2.0.2.dev1"
REQUIRES_DEFENSE_LAST5 = True

DEFENSE_RULE = "AT_LEAST_ONE_STRONG"
DEFENSE_THRESHOLD = 1.60
DEFENSE_PENALTY = 3.0


def calculate_score(match_stats, league_info, *, home_ga_last5=None, away_ga_last5=None):
    base = v20.calculate_score(match_stats, league_info)
    return apply_defense_penalty(
        base,
        home_ga_last5=home_ga_last5,
        away_ga_last5=away_ga_last5,
        rule=DEFENSE_RULE,
        threshold=DEFENSE_THRESHOLD,
        penalty=DEFENSE_PENALTY,
        label="V202DEV_STRONG_DEFENSE",
    )
