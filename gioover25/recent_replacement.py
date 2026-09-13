from __future__ import annotations

from dataclasses import replace

from .statistics import StatsSummary


GROUP_FIELDS = {
    "gf": ("gf",),
    "ga": ("ga",),
    "over": ("over15", "over25", "over35", "btts"),
    "form": ("wins", "draws", "losses", "points"),
}


def _rate(summary: StatsSummary, field: str) -> float:
    if summary.played <= 0:
        return 0.0
    return float(getattr(summary, field)) / float(summary.played)


def _blend_field(full: StatsSummary, recent: StatsSummary, field: str, recent_weight: float) -> float:
    w = max(0.0, min(1.0, float(recent_weight)))
    return ((1.0 - w) * _rate(full, field)) + (w * _rate(recent, field))


def blend_summary(
    full: StatsSummary,
    recent: StatsSummary,
    weights: dict[str, float],
) -> StatsSummary:
    """Restituisce uno StatsSummary con gli stessi played dello storico completo.

    I conteggi vengono ricostruiti dai tassi blended, cosi gli engine esistenti
    possono continuare a leggere gf/ga/over/points oppure le property per-match.
    """
    played = max(int(full.played), 1)
    values = {
        "played": int(full.played),
        "wins": float(full.wins),
        "draws": float(full.draws),
        "losses": float(full.losses),
        "points": float(full.points),
        "gf": float(full.gf),
        "ga": float(full.ga),
        "over15": float(full.over15),
        "over25": float(full.over25),
        "over35": float(full.over35),
        "btts": float(full.btts),
    }
    for group, fields in GROUP_FIELDS.items():
        weight = float(weights.get(group, 0.0))
        if weight <= 0.0 or recent.played <= 0:
            continue
        for field in fields:
            values[field] = _blend_field(full, recent, field, weight) * played
    return StatsSummary(**values)


def replace_overall_with_recent(match_stats, *, window: int, weights: dict[str, float]):
    """Copia MatchStatistics sostituendo solo `overall` di Home/Away.

    window puo essere 7 o 8. Classifica, venue, last5 e last10 restano invariati.
    """
    attr = f"last{int(window)}"
    if attr not in {"last7", "last8"}:
        raise ValueError("window deve essere 7 oppure 8")

    home_recent = getattr(match_stats.home, attr)
    away_recent = getattr(match_stats.away, attr)
    if home_recent is None or away_recent is None:
        return match_stats

    home = replace(
        match_stats.home,
        overall=blend_summary(match_stats.home.overall, home_recent, weights),
    )
    away = replace(
        match_stats.away,
        overall=blend_summary(match_stats.away.overall, away_recent, weights),
    )
    return replace(match_stats, home=home, away=away)
