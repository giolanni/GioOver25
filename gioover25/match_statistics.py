"""
===============================================================================
GioOver2.5 - match_statistics.py
===============================================================================

SCOPO
-----
Costruire tutte le statistiche disponibili prima di una partita, senza usare
informazioni future.

Questa versione conserva il comportamento storico del progetto e aggiunge
soltanto alcuni campi contestuali necessari al motore sperimentale v251:

- PPG delle ultime cinque partite, già ricavabile da `last5.points`;
- rilevazione di una pausa lunga della singola squadra;
- numero di gare disputate dalla ripresa;
- stato `restart_ready` / `restart_not_ready`.

IMPORTANTE
----------
Le nuove informazioni non modificano direttamente nessun engine esistente.
Gli engine v13-v25 possono continuare a usare gli stessi campi di prima.
Solo v251 legge i nuovi campi contestuali.

LOGICA RESTART
--------------
Una pausa viene considerata significativa quando:

1. tra due partite consecutive della stessa squadra passano almeno 21 giorni;
2. la squadra aveva già giocato almeno 5 gare prima della pausa.

La squadra viene considerata nuovamente pronta quando:

- ha disputato almeno 3 gare dopo la pausa; oppure
- ha disputato almeno 2 gare e sono state entrambe Over 2.5; oppure
- dalla ripresa segna almeno 2 gol di media a partita.

Queste soglie sono sperimentali e servono solo alla v251.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .history import MatchResult
from .statistics import StatsSummary, get_team_statistics
from .standings import calculate_standings_after_round


# Soglie contestuali usate per riconoscere una ripresa dopo una pausa lunga.
LONG_BREAK_DAYS = 21
MIN_MATCHES_BEFORE_LONG_BREAK = 5
MIN_MATCHES_TO_BE_RESTART_READY = 3
EARLY_READY_MIN_MATCHES = 2
EARLY_READY_GF_AVG = 2.0


@dataclass
class TeamMatchContext:
    """
    Contiene tutte le informazioni disponibili per una singola squadra.

    I primi campi sono quelli già utilizzati dagli engine esistenti.
    Gli ultimi campi, con prefisso `restart_`, sono opzionali e hanno valori
    neutri quando non viene rilevata alcuna pausa lunga.
    """

    team: str
    overall: StatsSummary
    last5: StatsSummary
    last10: StatsSummary
    home: StatsSummary
    away: StatsSummary
    position: int
    points: int
    ppg: float

    # Nuovi campi contestuali. I default mantengono retrocompatibilità.
    long_break_detected: int = 0
    long_break_days: int = 0
    matches_since_restart: int = 0
    gf_avg_since_restart: float = 0.0
    over_rate_since_restart: float = 0.0
    restart_ready: int = 1
    restart_not_ready: int = 0


@dataclass
class MatchStatistics:
    """Raccoglie il contesto delle due squadre e i gap di classifica."""

    home: TeamMatchContext
    away: TeamMatchContext
    position_gap: int
    points_gap: int
    ppg_gap: float



def _get_standing_map(
    matches: list[MatchResult],
    before_round: int,
) -> dict[str, dict]:
    """
    Ricostruisce la classifica prima del round da analizzare.

    La funzione restituisce un dizionario indicizzato per nome squadra così da
    recuperare rapidamente posizione, punti e PPG.
    """

    standings = calculate_standings_after_round(matches, before_round - 1)
    result: dict[str, dict] = {}

    for position, standing in enumerate(standings, start=1):
        result[standing.team] = {
            "position": position,
            "points": standing.points,
            "ppg": standing.ppg,
        }

    return result




def _as_date(value) -> date:
    """Converte le date ISO degli storici in oggetti `date` confrontabili."""

    if isinstance(value, date):
        return value

    return date.fromisoformat(str(value))


def _team_matches_before_round(
    matches: list[MatchResult],
    team: str,
    before_round: int,
) -> list[MatchResult]:
    """
    Restituisce tutte le gare della squadra precedenti al round analizzato.

    Le gare vengono ordinate per data e round per rendere deterministica la
    ricerca delle pause lunghe.
    """

    previous = [
        match
        for match in matches
        if match.round < before_round
        and team in {match.home, match.away}
    ]

    previous.sort(key=lambda match: (_as_date(match.date), match.round))
    return previous



def _goals_for(match: MatchResult, team: str) -> int:
    """Restituisce i gol segnati dalla squadra nella partita ricevuta."""

    if match.home == team:
        return match.home_goals
    return match.away_goals



def _restart_context(
    matches: list[MatchResult],
    team: str,
    before_round: int,
) -> dict[str, int | float]:
    """
    Calcola lo stato di ripresa della squadra prima della partita analizzata.

    Se non esiste una pausa lunga valida, restituisce valori neutri:
    `restart_ready=1` e `restart_not_ready=0`.
    """

    previous = _team_matches_before_round(matches, team, before_round)

    # Servono almeno cinque gare prima di poter distinguere una vera ripresa
    # dall'inizio naturale della stagione.
    if len(previous) <= MIN_MATCHES_BEFORE_LONG_BREAK:
        return {
            "long_break_detected": 0,
            "long_break_days": 0,
            "matches_since_restart": 0,
            "gf_avg_since_restart": 0.0,
            "over_rate_since_restart": 0.0,
            "restart_ready": 1,
            "restart_not_ready": 0,
        }

    break_index: int | None = None
    break_days = 0

    # Conserviamo l'ultima pausa valida, cioè quella più vicina alla partita
    # che stiamo analizzando.
    for current_index in range(1, len(previous)):
        matches_before_break = current_index
        gap_days = (
            _as_date(previous[current_index].date)
            - _as_date(previous[current_index - 1].date)
        ).days

        if (
            matches_before_break >= MIN_MATCHES_BEFORE_LONG_BREAK
            and gap_days >= LONG_BREAK_DAYS
        ):
            break_index = current_index
            break_days = gap_days

    if break_index is None:
        return {
            "long_break_detected": 0,
            "long_break_days": 0,
            "matches_since_restart": 0,
            "gf_avg_since_restart": 0.0,
            "over_rate_since_restart": 0.0,
            "restart_ready": 1,
            "restart_not_ready": 0,
        }

    since_restart = previous[break_index:]
    matches_since_restart = len(since_restart)

    goals_for = sum(_goals_for(match, team) for match in since_restart)
    over_count = sum(
        1
        for match in since_restart
        if match.home_goals + match.away_goals >= 3
    )

    gf_avg = goals_for / matches_since_restart if matches_since_restart else 0.0
    over_rate = over_count / matches_since_restart if matches_since_restart else 0.0

    enough_matches = matches_since_restart >= MIN_MATCHES_TO_BE_RESTART_READY
    early_all_over = (
        matches_since_restart >= EARLY_READY_MIN_MATCHES
        and over_count == matches_since_restart
    )
    early_strong_scoring = (
        matches_since_restart >= 1
        and gf_avg >= EARLY_READY_GF_AVG
    )

    restart_ready = int(
        enough_matches
        or early_all_over
        or early_strong_scoring
    )

    return {
        "long_break_detected": 1,
        "long_break_days": break_days,
        "matches_since_restart": matches_since_restart,
        "gf_avg_since_restart": round(gf_avg, 3),
        "over_rate_since_restart": round(over_rate, 3),
        "restart_ready": restart_ready,
        "restart_not_ready": int(restart_ready == 0),
    }



def build_team_context(
    matches: list[MatchResult],
    team: str,
    before_round: int,
) -> TeamMatchContext:
    """
    Costruisce il contesto completo di una squadra prima della partita.

    Le statistiche `overall`, `last5`, `last10`, `home` e `away` sono quelle
    tradizionali del progetto. Lo stato restart viene aggiunto senza alterare
    i calcoli preesistenti.
    """

    standing_map = _get_standing_map(matches, before_round)

    standing = standing_map.get(
        team,
        {
            "position": 999,
            "points": 0,
            "ppg": 0.0,
        },
    )

    restart = _restart_context(matches, team, before_round)

    return TeamMatchContext(
        team=team,
        overall=get_team_statistics(matches, team, before_round=before_round),
        last5=get_team_statistics(
            matches,
            team,
            before_round=before_round,
            last_n=5,
        ),
        last10=get_team_statistics(
            matches,
            team,
            before_round=before_round,
            last_n=10,
        ),
        home=get_team_statistics(
            matches,
            team,
            before_round=before_round,
            venue="home",
        ),
        away=get_team_statistics(
            matches,
            team,
            before_round=before_round,
            venue="away",
        ),
        position=standing["position"],
        points=standing["points"],
        ppg=standing["ppg"],
        long_break_detected=int(restart["long_break_detected"]),
        long_break_days=int(restart["long_break_days"]),
        matches_since_restart=int(restart["matches_since_restart"]),
        gf_avg_since_restart=float(restart["gf_avg_since_restart"]),
        over_rate_since_restart=float(restart["over_rate_since_restart"]),
        restart_ready=int(restart["restart_ready"]),
        restart_not_ready=int(restart["restart_not_ready"]),
    )



def build_match_statistics(
    matches: list[MatchResult],
    home_team: str,
    away_team: str,
    before_round: int,
) -> MatchStatistics:
    """
    Costruisce le statistiche della partita e neutralizza i gap non affidabili.

    Se una squadra non ha ancora disputato gare, non viene trattata come
    automaticamente ultima: la sua posizione viene temporaneamente allineata
    a quella dell'altra squadra per evitare gap artificiali enormi.
    """

    home = build_team_context(matches, home_team, before_round)
    away = build_team_context(matches, away_team, before_round)

    home_has_history = home.overall.played > 0
    away_has_history = away.overall.played > 0

    if not home_has_history and away_has_history:
        home.position = away.position
        home.points = away.points
        home.ppg = away.ppg

    elif not away_has_history and home_has_history:
        away.position = home.position
        away.points = home.points
        away.ppg = home.ppg

    elif not home_has_history and not away_has_history:
        home.position = 1
        away.position = 1
        home.points = 0
        away.points = 0
        home.ppg = 0.0
        away.ppg = 0.0

    return MatchStatistics(
        home=home,
        away=away,
        position_gap=abs(home.position - away.position),
        points_gap=abs(home.points - away.points),
        ppg_gap=abs(home.ppg - away.ppg),
    )
