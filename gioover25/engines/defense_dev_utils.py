"""
GioOver2.5 - helper condiviso strong-defense per engine DEV.

Congelato il 16/08/2026 per osservazione prospettica.
"""

from dataclasses import replace


def _band(score: float) -> str:
    if score >= 75:
        return "ALTA"
    if score >= 60:
        return "MEDIA-ALTA"
    if score >= 45:
        return "MEDIA"
    return "BASSA"


def apply_defense_penalty(
    base,
    *,
    home_ga_last5: float | None,
    away_ga_last5: float | None,
    rule: str,
    threshold: float,
    penalty: float,
    label: str,
):
    home_strong = (
        home_ga_last5 is not None
        and float(home_ga_last5) <= threshold
    )
    away_strong = (
        away_ga_last5 is not None
        and float(away_ga_last5) <= threshold
    )

    if rule == "HOME_STRONG":
        triggered = home_strong
    elif rule == "AWAY_STRONG":
        triggered = away_strong
    elif rule == "AT_LEAST_ONE_STRONG":
        triggered = home_strong or away_strong
    elif rule == "BOTH_STRONG":
        triggered = home_strong and away_strong
    else:
        raise ValueError(f"Regola strong-defense sconosciuta: {rule}")

    if not triggered:
        return base

    final_score = max(
        0.0,
        round(float(base.score) - float(penalty), 2),
    )

    home_text = "NA" if home_ga_last5 is None else f"{home_ga_last5:.2f}"
    away_text = "NA" if away_ga_last5 is None else f"{away_ga_last5:.2f}"

    diag = (
        f"{label}["
        f"Rule={rule};Threshold={threshold:.2f};Penalty=-{penalty:.2f};"
        f"HomeGALast5={home_text};AwayGALast5={away_text};"
        f"BaseScore={float(base.score):.2f};FinalScore={final_score:.2f}"
        "]"
    )

    old_reason = str(getattr(base, "reason", "") or "").strip()

    return replace(
        base,
        score=final_score,
        band=_band(final_score),
        reason=f"{old_reason} || {diag}" if old_reason else diag,
    )
