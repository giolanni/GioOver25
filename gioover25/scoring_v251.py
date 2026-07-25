"""
===============================================================================
GioOver2.5 - scoring_v251.py
===============================================================================

SCOPO
-----
Creare un motore sperimentale derivato direttamente dalla v25.

La v251 non cambia il cuore del calcolo: ottiene prima lo score della v25 e
applica soltanto micro-penalità prudenti emerse dalle analisi Laboratory.

MICRO-CORREZIONI
----------------
1. Difesa molto solida
   - almeno una squadra con meno di 1,00 GA/gara: -1 punto;
   - almeno una squadra con meno di 0,80 GA/gara: -2 punti complessivi.

2. Entrambe in forma risultati molto bassa
   - entrambe con PPG ultime 5 <= 0,60: -1 punto.

3. Ripresa dopo una lunga pausa
   - una squadra non ancora pronta: -1 punto;
   - entrambe non ancora pronte: -2 punti complessivi.

4. Limite di sicurezza
   - penalità complessiva massima: -4 punti.

MISURABILITÀ
------------
Ogni correzione viene scritta dentro `Reason` in forma strutturata, così lo
script di confronto può misurare quante volte si attiva e con quali esiti.

La v25 resta invariata e continua a essere la baseline ufficiale.
===============================================================================
"""

from dataclasses import replace

from .scoring_v25 import calculate_score_v25
from .scoring_v21dev import _band


# Soglie sperimentali. Sono centralizzate per rendere semplice modificarle in
# una futura iterazione senza cercare numeri sparsi nel codice.
STRONG_DEFENSE_GA_THRESHOLD = 1.00
VERY_STRONG_DEFENSE_GA_THRESHOLD = 0.80
LOW_RECENT_PPG_THRESHOLD = 0.60
MAX_TOTAL_PENALTY = 4.0



def _safe_float(value, default: float = 0.0) -> float:
    """Converte un valore in float senza interrompere il ranking."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return default



def _last5_ppg(team) -> float | None:
    """
    Calcola il PPG delle ultime cinque partite.

    Restituisce `None` quando non sono disponibili esattamente cinque gare,
    evitando di applicare una penalità su un campione incompleto.
    """

    played = int(getattr(team.last5, "played", 0) or 0)

    if played < 5:
        return None

    points = _safe_float(getattr(team.last5, "points", 0))
    return points / played



def calculate_score_v251(match_stats, league_info):
    """
    Calcola lo score v251 partendo integralmente dalla v25.

    La funzione restituisce lo stesso tipo di risultato della v25. Le
    informazioni diagnostiche vengono aggiunte a `Reason`, perciò non è
    necessario modificare il formato CSV dei ranking.
    """

    base = calculate_score_v25(match_stats, league_info)

    home = match_stats.home
    away = match_stats.away

    strong_defense_adjustment = 0.0
    recent_form_adjustment = 0.0
    restart_adjustment = 0.0
    notes: list[str] = []

    # -----------------------------------------------------------------------
    # 1. MICRO-CORREZIONE DIFESA SOLIDA
    # -----------------------------------------------------------------------
    # La penalità viene valutata soltanto quando entrambe le squadre hanno
    # almeno cinque gare, così una media GA molto bassa non deriva da un
    # campione troppo piccolo.
    enough_overall_history = (
        int(getattr(home.overall, "played", 0) or 0) >= 5
        and int(getattr(away.overall, "played", 0) or 0) >= 5
    )

    if enough_overall_history:
        best_defense_ga = min(
            _safe_float(getattr(home.overall, "ga_per_match", 0.0)),
            _safe_float(getattr(away.overall, "ga_per_match", 0.0)),
        )

        if best_defense_ga < VERY_STRONG_DEFENSE_GA_THRESHOLD:
            strong_defense_adjustment = -2.0
            notes.append(
                "difesa molto solida "
                f"({best_defense_ga:.2f} GA/gara)"
            )
        elif best_defense_ga < STRONG_DEFENSE_GA_THRESHOLD:
            strong_defense_adjustment = -1.0
            notes.append(
                "difesa solida "
                f"({best_defense_ga:.2f} GA/gara)"
            )

    # -----------------------------------------------------------------------
    # 2. MICRO-CORREZIONE FORMA RECENTE BASSA DI ENTRAMBE
    # -----------------------------------------------------------------------
    home_last5_ppg = _last5_ppg(home)
    away_last5_ppg = _last5_ppg(away)

    if (
        home_last5_ppg is not None
        and away_last5_ppg is not None
        and home_last5_ppg <= LOW_RECENT_PPG_THRESHOLD
        and away_last5_ppg <= LOW_RECENT_PPG_THRESHOLD
    ):
        recent_form_adjustment = -1.0
        notes.append(
            "entrambe con PPG ultime5 basso "
            f"({home_last5_ppg:.2f}+{away_last5_ppg:.2f})"
        )

    # -----------------------------------------------------------------------
    # 3. MICRO-CORREZIONE RIPRESA DOPO PAUSA LUNGA
    # -----------------------------------------------------------------------
    home_restart_not_ready = int(
        getattr(home, "restart_not_ready", 0) or 0
    )
    away_restart_not_ready = int(
        getattr(away, "restart_not_ready", 0) or 0
    )

    restart_not_ready_count = (
        home_restart_not_ready + away_restart_not_ready
    )

    if restart_not_ready_count == 1:
        restart_adjustment = -1.0
        notes.append("una squadra ancora in fase di ripresa")
    elif restart_not_ready_count == 2:
        restart_adjustment = -2.0
        notes.append("entrambe ancora in fase di ripresa")

    # -----------------------------------------------------------------------
    # 4. LIMITE DI SICUREZZA
    # -----------------------------------------------------------------------
    raw_total_adjustment = (
        strong_defense_adjustment
        + recent_form_adjustment
        + restart_adjustment
    )

    total_adjustment = max(-MAX_TOTAL_PENALTY, raw_total_adjustment)
    final_score = max(0.0, round(base.score + total_adjustment, 2))

    # Il suffisso è volutamente strutturato: compare sempre, anche quando tutte
    # le correzioni valgono zero, così il confronto retroattivo può analizzare
    # ogni prediction v251 in modo uniforme.
    diagnostics = (
        "V251_DIAGNOSTICS["
        f"BaseScore={base.score:.2f};"
        f"StrongDefense={strong_defense_adjustment:.2f};"
        f"RecentForm={recent_form_adjustment:.2f};"
        f"Restart={restart_adjustment:.2f};"
        f"Total={total_adjustment:.2f}"
        "]"
    )

    reason = getattr(base, "reason", "")

    if reason:
        reason += " || "

    reason += diagnostics

    if notes:
        reason += " || CONTRO V251: " + " | ".join(notes)

    return replace(
        base,
        score=final_score,
        band=_band(final_score),
        reason=reason,
    )
