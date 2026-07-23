"""
===============================================================================
GioOver2.5 - analysis/laboratory/recent_form_drivers.py
===============================================================================

SCOPO
-----
Calcolare, direttamente all'interno del Laboratory, i driver candidati legati
alla forma recente delle due squadre prima della partita analizzata.

Lo script non modifica alcun engine e non assegna penalità. Aggiunge soltanto
nuove colonne al dataset `01_matches.csv`, così che gli strumenti già esistenti
del Laboratory possano valutarle nelle quattro popolazioni ufficiali:

    ALTA_OK
    ALTA_KO
    MEDIA_OK
    MEDIA_KO

DRIVER CALCOLATI
----------------
Per ciascuna squadra vengono considerate esclusivamente le ultime cinque gare
con data precedente alla partita/prediction analizzata:

    HomePPGLast5 / AwayPPGLast5
        Punti medi per partita nelle ultime cinque gare.

    HomeWinsLast5 / AwayWinsLast5
        Numero di vittorie nelle ultime cinque gare.

    HomeWinlessLast5 / AwayWinlessLast5
        Vale 1 quando la squadra non ha vinto nessuna delle ultime cinque gare.

    BothTeamsWinlessLast5
        Vale 1 quando entrambe le squadre sono senza vittorie nelle ultime 5.

    HomeGFLast5Avg / AwayGFLast5Avg
        Gol segnati medi nelle ultime cinque gare.

    HomeGALast5Avg / AwayGALast5Avg
        Gol subiti medi nelle ultime cinque gare.

    WorstPPGLast5
        Il PPG peggiore tra le due squadre.

    AveragePPGLast5
        Media dei PPG recenti delle due squadre.

    TotalPPGLast5
        Somma dei PPG recenti delle due squadre. È il driver che misura
        direttamente quanto entrambe arrivano complessivamente bene o male.

    HomeLowPPGLowGF / AwayLowPPGLowGF
        Vale 1 se PPG < 0,60 e gol segnati medi < 1,20.

    BothTeamsLowPPGLowGF
        Vale 1 se entrambe le squadre rispettano la condizione precedente.

DRIVER RIPRESA DOPO UNA PAUSA LUNGA
-----------------------------------
Per ciascuna squadra viene cercata l'ultima interruzione di almeno 21 giorni,
ma soltanto quando la squadra aveva già disputato almeno cinque partite prima
della pausa. In questo modo l'inizio naturale della stagione non viene
confuso con una ripresa.

    HomeLongBreakDetected / AwayLongBreakDetected
        Vale 1 se è stata rilevata una pausa lunga valida.

    HomeLongBreakDays / AwayLongBreakDays
        Numero di giorni tra l'ultima partita prima della pausa e la prima
        partita successiva.

    HomeMatchesSinceRestart / AwayMatchesSinceRestart
        Partite disputate dalla squadra dopo la pausa e prima della prediction.

    HomeGFAvgSinceRestart / AwayGFAvgSinceRestart
        Gol segnati medi dalla ripresa.

    HomeOverRateSinceRestart / AwayOverRateSinceRestart
        Quota di partite Over 2.5 giocate dalla ripresa, compresa tra 0 e 1.

    HomeRestartReady / AwayRestartReady
        Vale 1 quando la squadra ha già disputato almeno tre partite dalla
        ripresa oppure mostra segnali offensivi confortanti in anticipo.

    HomeRestartNotReady / AwayRestartNotReady
        Vale 1 quando la squadra è ancora nella fase di ripresa incerta.

    BothTeamsRestartNotReady
        Vale 1 quando entrambe le squadre sono ancora in ripresa incerta.

PRINCIPIO ANTI-LOOKAHEAD
------------------------
Per evitare contaminazioni, vengono usate soltanto gare con MatchDate/Date
strettamente precedente alla data di riferimento della prediction.

CAMPIONE MINIMO
---------------
I driver vengono valorizzati soltanto quando entrambe le squadre dispongono di
almeno cinque gare precedenti. In caso contrario restano vuoti, evitando di
confrontare campioni non omogenei.

FILE LETTI
----------
    data/storico/risultati/<LeagueId>.csv

COMPATIBILITÀ
-------------
Il lettore accetta sia il nuovo header `MatchDate` sia il precedente `Date`.
Non richiede la colonna `Season` e funziona con LeagueId senza suffisso annuale.
===============================================================================
"""

from __future__ import annotations

# `csv` serve a leggere gli storici dei risultati salvati con separatore `;`.
import csv

# `date` viene usato per confrontare correttamente le date delle partite.
from datetime import date

# `Path` permette di costruire percorsi compatibili con Windows e Linux.
from pathlib import Path

# `Any` rende più chiari i tipi delle funzioni che ricevono valori da CSV.
from typing import Any


# Cartella che contiene uno storico risultati per ogni LeagueId.
RESULTS_DIR = Path("data/storico/risultati")

# Numero di partite recenti richieste per il calcolo uniforme del driver.
RECENT_MATCH_COUNT = 5

# Soglie sperimentali iniziali. Non modificano il motore: servono soltanto a
# costruire driver booleani che il Laboratory potrà confermare o bocciare.
LOW_PPG_THRESHOLD = 0.60
LOW_GF_AVG_THRESHOLD = 1.20

# Una pausa di almeno 21 giorni viene considerata una possibile interruzione
# significativa del ritmo agonistico. È una soglia sperimentale: il Laboratory
# dovrà stabilire se possiede davvero potere discriminante.
LONG_BREAK_DAYS = 21

# La pausa viene considerata soltanto se la squadra aveva già costruito una
# storia sufficiente prima dell'interruzione. Così l'inizio stagione non viene
# classificato erroneamente come ripresa.
MIN_MATCHES_BEFORE_LONG_BREAK = 5

# Dopo tre partite la squadra viene considerata normalmente riattivata.
MIN_MATCHES_TO_BE_RESTART_READY = 3

# Uscita anticipata dalla fase incerta: almeno due partite, entrambe Over 2.5.
EARLY_READY_MIN_MATCHES = 2

# Ulteriore segnale offensivo forte: media di almeno due gol segnati a partita
# nelle gare già disputate dopo la pausa.
EARLY_READY_GF_AVG = 2.0

# Elenco centralizzato delle colonne aggiunte al dataset del Laboratory.
RECENT_FORM_DRIVERS = [
    "HomePPGLast5",
    "AwayPPGLast5",
    "WorstPPGLast5",
    "AveragePPGLast5",
    "TotalPPGLast5",
    "HomeWinsLast5",
    "AwayWinsLast5",
    "HomeWinlessLast5",
    "AwayWinlessLast5",
    "BothTeamsWinlessLast5",
    "HomeGFLast5Avg",
    "AwayGFLast5Avg",
    "HomeGALast5Avg",
    "AwayGALast5Avg",
    "HomeLowPPGLowGF",
    "AwayLowPPGLowGF",
    "BothTeamsLowPPGLowGF",

    # Driver candidati relativi alla ripresa dopo una pausa lunga.
    "HomeLongBreakDetected",
    "AwayLongBreakDetected",
    "HomeLongBreakDays",
    "AwayLongBreakDays",
    "HomeMatchesSinceRestart",
    "AwayMatchesSinceRestart",
    "HomeGFAvgSinceRestart",
    "AwayGFAvgSinceRestart",
    "HomeOverRateSinceRestart",
    "AwayOverRateSinceRestart",
    "HomeRestartReady",
    "AwayRestartReady",
    "HomeRestartNotReady",
    "AwayRestartNotReady",
    "BothTeamsRestartNotReady",
    "AtLeastOneTeamRestartNotReady",
]


def _text(value: Any) -> str:
    """Restituisce sempre una stringa pulita, anche quando il valore è None."""
    return str(value or "").strip()


def _normalize_team(value: Any) -> str:
    """
    Normalizza il nome squadra per confronti robusti.

    `casefold()` gestisce maiuscole/minuscole meglio di `lower()` e la coppia
    `split()` + `join()` elimina spazi doppi o accidentali.
    """
    return " ".join(_text(value).casefold().split())


def _parse_date(value: Any) -> date | None:
    """Converte una data ISO `YYYY-MM-DD`; restituisce None se non valida."""
    raw = _text(value)

    if not raw:
        return None

    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _to_int(value: Any) -> int | None:
    """Converte HG/AG in intero senza interrompere l'analisi su righe sporche."""
    raw = _text(value)

    if raw == "":
        return None

    try:
        return int(raw)
    except ValueError:
        return None


def _reference_date(row: dict) -> date | None:
    """
    Determina la data oltre la quale non bisogna leggere risultati.

    `MatchDate` è il riferimento preferito. `PredictionDate` è un fallback utile
    per vecchie righe storiche dove MatchDate non era ancora valorizzata.
    """
    return (
        _parse_date(row.get("MatchDate"))
        or _parse_date(row.get("PredictionDate"))
    )


def _source_league_id(row: dict, side: str) -> str:
    """
    Sceglie lo storico corretto per Home o Away.

    Nei CompetitionGroup una squadra può provenire da una divisione diversa
    dalla LeagueId della partita. Se il campo SourceLeagueId è valorizzato viene
    usato; altrimenti si ricade sulla LeagueId principale.
    """
    source_field = f"{side}SourceLeagueId"
    return _text(row.get(source_field)) or _text(row.get("LeagueId"))


def _read_results_file(path: Path) -> list[dict]:
    """
    Legge uno storico risultati in modo indipendente dalla vecchia Season.

    Ogni riga valida viene convertita in un dizionario minimale contenente data,
    squadre e gol. Le righe senza data o risultato finale vengono ignorate.
    """
    if not path.exists():
        return []

    matches: list[dict] = []

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")

        # Accetta il nuovo `MatchDate` e il vecchio `Date`.
        date_field = (
            "MatchDate"
            if "MatchDate" in (reader.fieldnames or [])
            else "Date"
        )

        required = {date_field, "Home", "Away", "HG", "AG"}
        missing = required.difference(reader.fieldnames or [])

        # Un file non conforme viene ignorato in questa fase diagnostica; non
        # deve impedire la costruzione dell'intero Laboratory.
        if missing:
            return []

        for raw in reader:
            match_date = _parse_date(raw.get(date_field))
            home_goals = _to_int(raw.get("HG"))
            away_goals = _to_int(raw.get("AG"))

            if match_date is None or home_goals is None or away_goals is None:
                continue

            matches.append({
                "date": match_date,
                "home": _normalize_team(raw.get("Home")),
                "away": _normalize_team(raw.get("Away")),
                "hg": home_goals,
                "ag": away_goals,
            })

    # Ordinare una volta sola rende poi deterministica la scelta delle ultime 5.
    matches.sort(key=lambda item: item["date"])
    return matches


def _team_recent_matches(
    matches: list[dict],
    team: str,
    before_date: date,
) -> list[dict]:
    """Seleziona le ultime cinque gare della squadra precedenti alla prediction."""
    normalized_team = _normalize_team(team)

    previous = [
        match
        for match in matches
        if match["date"] < before_date
        and normalized_team in {match["home"], match["away"]}
    ]

    return previous[-RECENT_MATCH_COUNT:]



def _team_previous_matches(
    matches: list[dict],
    team: str,
    before_date: date,
) -> list[dict]:
    """
    Restituisce tutte le partite precedenti della squadra in ordine cronologico.

    Questa funzione è distinta da `_team_recent_matches()` perché l'analisi
    della ripresa deve osservare l'intera sequenza storica e cercare intervalli
    lunghi tra due gare consecutive, non soltanto le ultime cinque.
    """
    normalized_team = _normalize_team(team)

    return [
        match
        for match in matches
        if match["date"] < before_date
        and normalized_team in {match["home"], match["away"]}
    ]


def _team_goals_for(match: dict, normalized_team: str) -> int:
    """Restituisce i gol segnati dalla squadra nella partita ricevuta."""
    return match["hg"] if match["home"] == normalized_team else match["ag"]


def _restart_status(previous_matches: list[dict], team: str) -> dict | None:
    """
    Calcola lo stato di ripresa della singola squadra.

    LOGICA
    ------
    1. Cerca l'ultima coppia di partite consecutive separata da almeno
       `LONG_BREAK_DAYS`.
    2. Accetta quella pausa soltanto se prima dell'interruzione risultano già
       almeno `MIN_MATCHES_BEFORE_LONG_BREAK` partite.
    3. Considera come gare post-ripresa tutte quelle dalla prima partita dopo
       la pausa fino alla data della prediction, esclusa.
    4. La squadra è pronta dopo almeno tre gare, oppure prima quando:
       - ha disputato almeno due gare ed entrambe sono Over 2.5; oppure
       - segna mediamente almeno due gol a partita dalla ripresa.

    Restituisce None se non esiste alcuna pausa lunga valida. In questo modo i
    campionati senza interruzioni non vengono mescolati artificialmente con i
    casi di ripresa.
    """
    if len(previous_matches) <= MIN_MATCHES_BEFORE_LONG_BREAK:
        return None

    break_index: int | None = None
    break_days = 0

    # Si percorrono tutte le coppie consecutive e si conserva l'ultima pausa
    # valida, cioè quella temporalmente più vicina alla prediction.
    for current_index in range(1, len(previous_matches)):
        matches_before_break = current_index
        gap_days = (
            previous_matches[current_index]["date"]
            - previous_matches[current_index - 1]["date"]
        ).days

        if (
            matches_before_break >= MIN_MATCHES_BEFORE_LONG_BREAK
            and gap_days >= LONG_BREAK_DAYS
        ):
            break_index = current_index
            break_days = gap_days

    if break_index is None:
        return None

    since_restart = previous_matches[break_index:]
    matches_since_restart = len(since_restart)
    normalized_team = _normalize_team(team)

    goals_for = sum(
        _team_goals_for(match, normalized_team)
        for match in since_restart
    )

    over_count = sum(
        1
        for match in since_restart
        if match["hg"] + match["ag"] >= 3
    )

    gf_avg = (
        goals_for / matches_since_restart
        if matches_since_restart
        else 0.0
    )
    over_rate = (
        over_count / matches_since_restart
        if matches_since_restart
        else 0.0
    )

    enough_matches = (
        matches_since_restart >= MIN_MATCHES_TO_BE_RESTART_READY
    )
    early_all_over = (
        matches_since_restart >= EARLY_READY_MIN_MATCHES
        and over_count == matches_since_restart
    )
    early_strong_scoring = (
        matches_since_restart >= 1
        and gf_avg >= EARLY_READY_GF_AVG
    )

    ready = int(
        enough_matches
        or early_all_over
        or early_strong_scoring
    )

    return {
        "detected": 1,
        "break_days": break_days,
        "matches_since_restart": matches_since_restart,
        "gf_avg_since_restart": round(gf_avg, 3),
        "over_rate_since_restart": round(over_rate, 3),
        "ready": ready,
        "not_ready": int(ready == 0),
    }


def _team_form(matches: list[dict], team: str) -> dict | None:
    """
    Calcola PPG, vittorie, gol fatti e subiti sulle cinque gare ricevute.

    Restituisce None quando il campione non contiene esattamente cinque gare.
    """
    if len(matches) < RECENT_MATCH_COUNT:
        return None

    normalized_team = _normalize_team(team)
    points = 0
    wins = 0
    goals_for = 0
    goals_against = 0

    for match in matches:
        is_home = match["home"] == normalized_team

        team_goals = match["hg"] if is_home else match["ag"]
        opponent_goals = match["ag"] if is_home else match["hg"]

        goals_for += team_goals
        goals_against += opponent_goals

        if team_goals > opponent_goals:
            points += 3
            wins += 1
        elif team_goals == opponent_goals:
            points += 1

    return {
        "ppg": round(points / RECENT_MATCH_COUNT, 3),
        "wins": wins,
        "gf_avg": round(goals_for / RECENT_MATCH_COUNT, 3),
        "ga_avg": round(goals_against / RECENT_MATCH_COUNT, 3),
    }


def _empty_driver_values() -> dict:
    """Crea tutti i nuovi campi vuoti quando il campione non è sufficiente."""
    return {driver: "" for driver in RECENT_FORM_DRIVERS}


def enrich_matches_with_recent_form(
    rows: list[dict],
    results_dir: Path = RESULTS_DIR,
) -> list[dict]:
    """
    Aggiunge i driver recenti a tutte le righe del dataset Laboratory.

    La funzione usa una cache per leggere ogni file storico una sola volta.
    Restituisce nuove righe senza modificare in modo incontrollato quelle di
    input, così il comportamento rimane facile da verificare e testare.
    """
    cache: dict[str, list[dict]] = {}
    enriched_rows: list[dict] = []

    for original_row in rows:
        row = dict(original_row)
        reference_date = _reference_date(row)

        if reference_date is None:
            row.update(_empty_driver_values())
            enriched_rows.append(row)
            continue

        home_league_id = _source_league_id(row, "Home")
        away_league_id = _source_league_id(row, "Away")

        for league_id in {home_league_id, away_league_id}:
            if league_id and league_id not in cache:
                cache[league_id] = _read_results_file(
                    results_dir / f"{league_id}.csv"
                )

        home_history = _team_previous_matches(
            cache.get(home_league_id, []),
            row.get("Home", ""),
            reference_date,
        )
        away_history = _team_previous_matches(
            cache.get(away_league_id, []),
            row.get("Away", ""),
            reference_date,
        )

        # Le ultime cinque gare vengono ricavate dalla storia già filtrata.
        home_recent = home_history[-RECENT_MATCH_COUNT:]
        away_recent = away_history[-RECENT_MATCH_COUNT:]

        home_form = _team_form(home_recent, row.get("Home", ""))
        away_form = _team_form(away_recent, row.get("Away", ""))

        # Lo stato di ripresa viene calcolato indipendentemente dalla presenza
        # delle cinque gare recenti: una pausa può essere diagnosticata anche
        # quando una delle metriche Last5 non è disponibile.
        home_restart = _restart_status(home_history, row.get("Home", ""))
        away_restart = _restart_status(away_history, row.get("Away", ""))

        driver_values = _empty_driver_values()

        if home_restart is not None:
            driver_values.update({
                "HomeLongBreakDetected": home_restart["detected"],
                "HomeLongBreakDays": home_restart["break_days"],
                "HomeMatchesSinceRestart": home_restart["matches_since_restart"],
                "HomeGFAvgSinceRestart": home_restart["gf_avg_since_restart"],
                "HomeOverRateSinceRestart": home_restart["over_rate_since_restart"],
                "HomeRestartReady": home_restart["ready"],
                "HomeRestartNotReady": home_restart["not_ready"],
            })

        if away_restart is not None:
            driver_values.update({
                "AwayLongBreakDetected": away_restart["detected"],
                "AwayLongBreakDays": away_restart["break_days"],
                "AwayMatchesSinceRestart": away_restart["matches_since_restart"],
                "AwayGFAvgSinceRestart": away_restart["gf_avg_since_restart"],
                "AwayOverRateSinceRestart": away_restart["over_rate_since_restart"],
                "AwayRestartReady": away_restart["ready"],
                "AwayRestartNotReady": away_restart["not_ready"],
            })

        home_not_ready = int(
            home_restart is not None and home_restart["not_ready"] == 1
        )
        away_not_ready = int(
            away_restart is not None and away_restart["not_ready"] == 1
        )

        driver_values["BothTeamsRestartNotReady"] = int(
            home_not_ready == 1 and away_not_ready == 1
        )
        driver_values["AtLeastOneTeamRestartNotReady"] = int(
            home_not_ready == 1 or away_not_ready == 1
        )

        if home_form is None or away_form is None:
            row.update(driver_values)
            enriched_rows.append(row)
            continue

        home_low_ppg_low_gf = int(
            home_form["ppg"] < LOW_PPG_THRESHOLD
            and home_form["gf_avg"] < LOW_GF_AVG_THRESHOLD
        )
        away_low_ppg_low_gf = int(
            away_form["ppg"] < LOW_PPG_THRESHOLD
            and away_form["gf_avg"] < LOW_GF_AVG_THRESHOLD
        )

        driver_values.update({
            "HomePPGLast5": home_form["ppg"],
            "AwayPPGLast5": away_form["ppg"],
            "WorstPPGLast5": min(home_form["ppg"], away_form["ppg"]),
            "AveragePPGLast5": round(
                (home_form["ppg"] + away_form["ppg"]) / 2,
                3,
            ),

            # Somma dei PPG delle due squadre. Un valore molto basso indica
            # che entrambe hanno raccolto pochi punti nelle ultime cinque gare.
            # Il Laboratory potrà cercare automaticamente le soglie più utili.
            "TotalPPGLast5": round(
                home_form["ppg"] + away_form["ppg"],
                3,
            ),
            "HomeWinsLast5": home_form["wins"],
            "AwayWinsLast5": away_form["wins"],
            "HomeWinlessLast5": int(home_form["wins"] == 0),
            "AwayWinlessLast5": int(away_form["wins"] == 0),
            "BothTeamsWinlessLast5": int(
                home_form["wins"] == 0 and away_form["wins"] == 0
            ),
            "HomeGFLast5Avg": home_form["gf_avg"],
            "AwayGFLast5Avg": away_form["gf_avg"],
            "HomeGALast5Avg": home_form["ga_avg"],
            "AwayGALast5Avg": away_form["ga_avg"],
            "HomeLowPPGLowGF": home_low_ppg_low_gf,
            "AwayLowPPGLowGF": away_low_ppg_low_gf,
            "BothTeamsLowPPGLowGF": int(
                home_low_ppg_low_gf == 1 and away_low_ppg_low_gf == 1
            ),
        })

        row.update(driver_values)
        enriched_rows.append(row)

    return enriched_rows
