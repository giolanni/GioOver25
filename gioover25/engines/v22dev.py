"""
v22dev = v22 + strong-defense penalty.

Configurazione congelata 16/08/2026:
- Away GA Last5 <= 1.60
- penalità -13
"""
from . import v22
from .defense_dev_utils import apply_defense_penalty

ENGINE_NAME = "v22dev"
ENGINE_VERSION = "2.2.dev-defense1"
REQUIRES_DEFENSE_LAST5 = True

DEFENSE_RULE = "AWAY_STRONG"
DEFENSE_THRESHOLD = 1.60
DEFENSE_PENALTY = 13.0


def calculate_score(match_stats, league_info, *, home_ga_last5=None, away_ga_last5=None):
    base = v22.calculate_score(match_stats, league_info)
    return apply_defense_penalty(
        base,
        home_ga_last5=home_ga_last5,
        away_ga_last5=away_ga_last5,
        rule=DEFENSE_RULE,
        threshold=DEFENSE_THRESHOLD,
        penalty=DEFENSE_PENALTY,
        label="V22DEV_STRONG_DEFENSE",
    )
