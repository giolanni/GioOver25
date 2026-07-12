from dataclasses import replace

from .scoring_v22 import calculate_score_v22
from .scoring_v21dev import _band


def _get_nested_value(obj, *paths, default=None):
    """
    Cerca un valore provando più percorsi possibili.

    Esempio:
        _get_nested_value(team, "standing.position", "overall.position", "position")
    """
    for path in paths:
        current = obj

        try:
            for part in path.split("."):
                current = getattr(current, part)

            if current is not None:
                return current

        except AttributeError:
            continue

    return default


def _safe_float(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def calculate_score_v25(match_stats, league_info):
    """
    Engine v25:
    - parte dal punteggio di v22;
    - aggiunge una penalità per sfide equilibrate di alta classifica;
    - la vicinanza viene valutata tramite posizione, punti e PPG;
    - la penalità scatta solo se la squadra meglio classificata
      ha una difesa stagionale solida.
    """

    base = calculate_score_v22(
        match_stats,
        league_info,
    )

    home = match_stats.home
    away = match_stats.away

    home_position = _safe_float(
        _get_nested_value(
            home,
            "standing.position",
            "overall.position",
            "position",
        ),
        default=999,
    )

    away_position = _safe_float(
        _get_nested_value(
            away,
            "standing.position",
            "overall.position",
            "position",
        ),
        default=999,
    )

    home_points = _safe_float(
        _get_nested_value(
            home,
            "standing.points",
            "overall.points",
            "points",
        )
    )

    away_points = _safe_float(
        _get_nested_value(
            away,
            "standing.points",
            "overall.points",
            "points",
        )
    )

    home_played = _safe_float(
        _get_nested_value(
            home,
            "standing.played",
            "overall.played",
            "played",
        )
    )

    away_played = _safe_float(
        _get_nested_value(
            away,
            "standing.played",
            "overall.played",
            "played",
        )
    )

    home_ppg = _get_nested_value(
        home,
        "standing.ppg",
        "overall.ppg",
        "ppg",
    )

    away_ppg = _get_nested_value(
        away,
        "standing.ppg",
        "overall.ppg",
        "ppg",
    )

    if home_ppg is None:
        home_ppg = (
            home_points / home_played
            if home_played > 0
            else 0.0
        )

    if away_ppg is None:
        away_ppg = (
            away_points / away_played
            if away_played > 0
            else 0.0
        )

    home_ppg = _safe_float(home_ppg)
    away_ppg = _safe_float(away_ppg)

    home_ga_per_match = _safe_float(
        _get_nested_value(
            home,
            "overall.ga_per_match",
            "ga_per_match",
        )
    )

    away_ga_per_match = _safe_float(
        _get_nested_value(
            away,
            "overall.ga_per_match",
            "ga_per_match",
        )
    )

    position_gap = abs(
        home_position - away_position
    )

    points_gap = abs(
        home_points - away_points
    )

    ppg_gap = abs(
        home_ppg - away_ppg
    )

    both_top_five = (
        home_position <= 5
        and away_position <= 5
    )

    close_positions = position_gap <= 2

    # Se le squadre hanno giocato praticamente lo stesso
    # numero di partite, usiamo soprattutto i punti.
    similar_matches_played = (
        abs(home_played - away_played) <= 1
    )

    if similar_matches_played:
        close_in_table = (
            points_gap <= 4
            and ppg_gap <= 0.30
        )
    else:
        # Se il numero di partite è differente,
        # il PPG diventa il riferimento principale.
        close_in_table = (
            ppg_gap <= 0.25
        )

    close_top_match = (
        both_top_five
        and close_positions
        and close_in_table
    )

    # La squadra meglio classificata è quella
    # con posizione numericamente più bassa.
    if home_position < away_position:
        best_team_ga = home_ga_per_match
        best_team_label = "casa"

    elif away_position < home_position:
        best_team_ga = away_ga_per_match
        best_team_label = "trasferta"

    else:
        # A parità di posizione teorica usiamo il PPG.
        if home_ppg >= away_ppg:
            best_team_ga = home_ga_per_match
            best_team_label = "casa"
        else:
            best_team_ga = away_ga_per_match
            best_team_label = "trasferta"

    penalty = 0
    cons = []

    if (
        close_top_match
        and best_team_ga < 1.00
    ):
        penalty += 6

        cons.append(
            "v25: sfida equilibrata di alta classifica "
            f"(gap punti {points_gap:.1f}, "
            f"gap PPG {ppg_gap:.2f}) con difesa "
            f"{best_team_label} sotto 1 gol subito a partita"
        )

    if (
        close_top_match
        and best_team_ga < 0.80
    ):
        penalty += 3

        cons.append(
            "v25 extra: difesa stagionale molto solida "
            f"({best_team_ga:.2f} GA per partita)"
        )

    if (
        base.score >= 85
        and close_top_match
        and best_team_ga < 1.00
    ):
        penalty += 3

        cons.append(
            "v25 extra: riduzione score molto alto "
            "per rischio gara tattica"
        )

    final_score = max(
        0,
        round(base.score - penalty, 2),
    )

    reason = getattr(base, "reason", "")

    if cons:
        if reason:
            reason += " || CONTRO V25: "
        else:
            reason = "CONTRO V25: "

        reason += " | ".join(cons)

    return replace(
        base,
        score=final_score,
        band=_band(final_score),
        reason=reason,
    )