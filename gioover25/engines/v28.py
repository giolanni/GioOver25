"""V28 sperimentale Over 2.5: selezione piu selettiva, indipendente da V27.

Regola candidata, ricavata dal Laboratory 2026-11-23:
HomeAttackScore >= 12.428 AND AwayGALast5Avg >= 3.00.
Non modificare V27. La soglia e da validare prospetticamente.
"""
from dataclasses import replace
from . import v26

ENGINE_NAME = "v28"
ENGINE_VERSION = "2.8.0"
REQUIRES_DEFENSE_LAST5 = True
SELECTION_ONLY = True

HOME_ATTACK_THRESHOLD = 12.428
AWAY_GA_LAST5_THRESHOLD = 3.00


def calculate_score(match_stats, league_info, *, home_ga_last5=None, away_ga_last5=None):
    base = v26.calculate_score(match_stats, league_info)
    home_attack = float(base.home_attack_score)
    away_ga = None if away_ga_last5 is None else float(away_ga_last5)
    selected = (
        home_attack >= HOME_ATTACK_THRESHOLD
        and away_ga is not None
        and away_ga >= AWAY_GA_LAST5_THRESHOLD
    )
    reason = (
        f"V28_OVER25_ATTACK_AWAYGA: HomeAttack={home_attack:.3f} "
        f"(>={HOME_ATTACK_THRESHOLD:.3f}); "
        f"AwayGA5={away_ga:.3f} (>={AWAY_GA_LAST5_THRESHOLD:.2f})"
        if selected else "V28_OVER25_ATTACK_AWAYGA: regola non soddisfatta"
    )
    return replace(base, band="ALTA" if selected else "BASSA",
                   reason=f"{base.reason} || {reason}")
