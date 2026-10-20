"""GioOver2.5 - Engine sperimentale v27.

Regola Over 2.5 congelata dopo validazione walk-forward:
- HomeAttackScore >= 12.428
- AwayGALast5Avg >= 2.20

La selezione e' indipendente dalla fascia dell'engine base. Lo scoring v26 viene
mantenuto solo per compatibilita' con l'output e per conservare i driver.
"""

from dataclasses import replace

from . import v26

ENGINE_NAME = "v27"
ENGINE_VERSION = "2.7.0"
REQUIRES_DEFENSE_LAST5 = True
SELECTION_ONLY = True

HOME_ATTACK_THRESHOLD = 12.428
AWAY_GA_LAST5_THRESHOLD = 2.20


def calculate_score(
    match_stats,
    league_info,
    *,
    home_ga_last5=None,
    away_ga_last5=None,
):
    base = v26.calculate_score(match_stats, league_info)

    home_attack_score = float(base.home_attack_score)
    away_ga = None if away_ga_last5 is None else float(away_ga_last5)

    selected = (
        home_attack_score >= HOME_ATTACK_THRESHOLD
        and away_ga is not None
        and away_ga >= AWAY_GA_LAST5_THRESHOLD
    )

    rule_reason = (
        f"V27_OVER25_ATTACK_AWAYGA: HomeAttack={home_attack_score:.3f} "
        f"(>={HOME_ATTACK_THRESHOLD:.3f}); "
        f"AwayGA5={away_ga:.3f} (>={AWAY_GA_LAST5_THRESHOLD:.2f})"
        if selected
        else "V27_OVER25_ATTACK_AWAYGA: regola non soddisfatta"
    )

    return replace(
        base,
        band="ALTA" if selected else "BASSA",
        reason=f"{base.reason} || {rule_reason}",
    )
