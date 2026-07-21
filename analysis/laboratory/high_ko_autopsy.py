"""
===============================================================================
GioOver2.5 - analysis/laboratory/high_ko_autopsy.py
===============================================================================

SCOPO
-----
Questo modulo rende permanente, all'interno del Laboratory, l'analisi degli
errori della FASCIA ALTA.

Non è uno script occasionale: viene richiamato da ``run_all.py`` ogni volta che
si aggiorna il Laboratory e rigenera automaticamente tre report diagnostici.

INPUT
-----
1. ``analysis/laboratory/data/01_matches.csv``
   Dataset principale prodotto dal Laboratory.

2. ``data/storico/risultati/<LeagueId>.csv``
   Storici risultati, usati esclusivamente per ricostruire la situazione delle
   squadre PRIMA della prediction analizzata.

OUTPUT
------
``analysis/laboratory/data/14_high_ko_autopsy.csv``
    Una riga per ogni partita FASCIA ALTA conclusa con esito KO, arricchita con
    posizione, PPG, gol fatti/subiti per gara e forma delle ultime cinque.

``analysis/laboratory/data/15_high_ko_patterns.csv``
    Confronto aggregato tra FASCIA ALTA OK e FASCIA ALTA KO. Per ogni metrica
    mostra media, mediana, differenza e numerosità disponibile.

``analysis/laboratory/data/16_high_band_daily.csv``
    Andamento giornaliero della FASCIA ALTA: numero di OK, KO, precisione e
    media dei principali driver. Serve a verificare se il peggioramento è
    davvero recente oppure soltanto percepito.

PRINCIPI DI SICUREZZA
---------------------
- Non modifica engine, ranking o storici risultati.
- Usa soltanto partite precedenti alla data della prediction.
- Se un dato non è disponibile lascia il campo vuoto, senza inventarlo.
- Gestisce sia ``MatchDate`` sia il vecchio ``Date`` negli storici.
- Non richiede la colonna ``Season``.
===============================================================================
"""

# ``csv`` legge e scrive i file delimitati da punto e virgola del progetto.
import csv

# ``math`` serve per verificare valori numerici mancanti o non validi.
import math

# ``statistics`` calcola medie e mediane senza dipendenze esterne.
import statistics

# ``dataclass`` rende esplicita e leggibile la struttura di un risultato.
from dataclasses import dataclass

# ``date`` permette confronti temporali sicuri tra prediction e risultati.
from datetime import date

# ``Path`` evita concatenazioni manuali e rende il codice portabile.
from pathlib import Path


# Radice del repository. Lo script va eseguito dalla directory principale.
ROOT = Path(".")

# Dataset già prodotto dal Laboratory e quindi unica fonte delle prediction.
MATCHES_FILE = ROOT / "analysis/laboratory/data/01_matches.csv"

# Cartella contenente un file CSV per ogni LeagueId.
RESULTS_DIR = ROOT / "data/storico/risultati"

# Cartella ufficiale degli output del Laboratory.
OUTPUT_DIR = ROOT / "analysis/laboratory/data"

# Report dettagliato delle sole ALTA KO.
AUTOPSY_FILE = OUTPUT_DIR / "14_high_ko_autopsy.csv"

# Report statistico di confronto ALTA OK contro ALTA KO.
PATTERNS_FILE = OUTPUT_DIR / "15_high_ko_patterns.csv"

# Report cronologico della resa della fascia ALTA.
DAILY_FILE = OUTPUT_DIR / "16_high_band_daily.csv"

# Numero di gare recenti utilizzate nelle metriche di forma.
LAST_N = 5

# Punti assegnati dai risultati calcistici.
WIN_POINTS = 3
DRAW_POINTS = 1
LOSS_POINTS = 0


@dataclass(frozen=True)
class HistoricalMatch:
    """Rappresenta una singola partita letta dallo storico risultati."""

    # Giornata della gara; può essere zero quando lo storico non la conosce.
    round_number: int

    # Data ISO della gara, se disponibile.
    match_date: date | None

    # Nomi delle squadre così come compaiono nello storico.
    home: str
    away: str

    # Gol finali della gara.
    home_goals: int
    away_goals: int


@dataclass
class TeamSnapshot:
    """Fotografia statistica di una squadra prima della prediction."""

    # Numero complessivo di partite precedenti.
    played: int = 0

    # Vittorie, pareggi e sconfitte precedenti.
    wins: int = 0
    draws: int = 0
    losses: int = 0

    # Gol fatti, gol subiti e punti complessivi.
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0

    # Posizione ricostruita nella classifica prima del match.
    position: int | None = None

    # Indicatori medi stagionali ricostruiti.
    ppg: float | None = None
    gf_per_game: float | None = None
    ga_per_game: float | None = None

    # Indicatori delle ultime cinque partite disponibili.
    ppg_last5: float | None = None
    wins_last5: int | None = None
    gf_last5_avg: float | None = None
    ga_last5_avg: float | None = None


# Questi sono i driver numerici già prodotti dal motore e dal Laboratory.
# Verranno conservati nell'autopsia e confrontati nel report aggregato.
ENGINE_DRIVER_FIELDS = [
    "Score",
    "RankingGapScore",
    "HomeAttackScore",
    "AwayAttackScore",
    "HomeDefenseWeaknessScore",
    "AwayDefenseWeaknessScore",
    "HomeLast10OverScore",
    "AwayLast10OverScore",
    "HomeVenueOverScore",
    "AwayVenueOverScore",
    "BTTSProfileScore",
]

# Driver recenti già presenti nel Laboratory dopo l'estensione sulla forma.
RECENT_FORM_FIELDS = [
    "HomePPGLast5",
    "AwayPPGLast5",
    "WorstPPGLast5",
    "AveragePPGLast5",
    "TotalPPGLast5",
    "HomeWinsLast5",
    "AwayWinsLast5",
    "HomeGFLast5Avg",
    "AwayGFLast5Avg",
    "HomeGALast5Avg",
    "AwayGALast5Avg",
]

# Metriche diagnostiche ricostruite direttamente dagli storici risultati.
DERIVED_FIELDS = [
    "HomePosition",
    "AwayPosition",
    "PositionGap",
    "HomePlayed",
    "AwayPlayed",
    "HomePoints",
    "AwayPoints",
    "HomePPG",
    "AwayPPG",
    "PPGGap",
    "HomeGFpg",
    "AwayGFpg",
    "HomeGApg",
    "AwayGApg",
    "BestDefenseGApg",
    "WorstDefenseGApg",
    "BestAttackGFpg",
    "WorstAttackGFpg",
    "SnapshotHomePPGLast5",
    "SnapshotAwayPPGLast5",
    "SnapshotTotalPPGLast5",
    "SnapshotHomeWinsLast5",
    "SnapshotAwayWinsLast5",
    "SnapshotHomeGFLast5Avg",
    "SnapshotAwayGFLast5Avg",
    "SnapshotHomeGALast5Avg",
    "SnapshotAwayGALast5Avg",
    "SnapshotTotalGoalsLast5Avg",
]


def _text(value) -> str:
    """Restituisce sempre una stringa pulita, anche se il valore è ``None``."""

    return str(value or "").strip()


def _normalize_team(value) -> str:
    """Normalizza un nome squadra per confronti interni non sensibili al caso."""

    return " ".join(_text(value).casefold().split())


def _parse_date(value) -> date | None:
    """Converte una data ISO in ``date``; i valori non validi diventano vuoti."""

    raw = _text(value)

    if not raw:
        return None

    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _to_int(value) -> int:
    """Converte un valore numerico CSV in intero senza interrompere il report."""

    raw = _text(value)

    if not raw:
        return 0

    try:
        return int(float(raw.replace(",", ".")))
    except ValueError:
        return 0


def _to_float(value) -> float | None:
    """Converte un valore CSV in float; restituisce ``None`` se non utilizzabile."""

    raw = _text(value)

    if not raw:
        return None

    try:
        number = float(raw.replace(",", "."))
    except ValueError:
        return None

    if math.isnan(number) or math.isinf(number):
        return None

    return number


def _round_or_blank(value: float | None, digits: int = 3):
    """Arrotonda un numero, ma mantiene vuoti i dati non disponibili."""

    if value is None:
        return ""

    return round(value, digits)


def _is_high_band(value) -> bool:
    """Riconosce le varianti usate nel progetto per indicare la fascia alta."""

    normalized = _text(value).upper().replace(" ", "_")

    return normalized in {"ALTA", "HIGH", "HA", "FASCIA_ALTA"}


def _outcome(row: dict) -> str:
    """Ricava l'esito Over 2.5 dalla colonna disponibile nel dataset."""

    explicit = _text(row.get("Outcome") or row.get("Over25")).upper()

    if explicit in {"OK", "KO"}:
        return explicit

    goals = _to_int(row.get("Goals"))

    if _text(row.get("Goals")):
        return "OK" if goals >= 3 else "KO"

    return ""


def _effective_date(row: dict) -> date | None:
    """Usa MatchDate e, solo come fallback legacy, PredictionDate."""

    return _parse_date(row.get("MatchDate")) or _parse_date(
        row.get("PredictionDate")
    )


def _load_laboratory_matches() -> list[dict]:
    """Legge il dataset ufficiale del Laboratory e valida le colonne essenziali."""

    if not MATCHES_FILE.exists():
        raise FileNotFoundError(
            f"Dataset Laboratory non trovato: {MATCHES_FILE}. "
            "Eseguire prima build_laboratory."
        )

    with MATCHES_FILE.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")

        required = {"LeagueId", "Home", "Away", "Band"}
        missing = required - set(reader.fieldnames or [])

        if missing:
            raise ValueError(
                "01_matches.csv non valido. Mancano le colonne: "
                + ", ".join(sorted(missing))
            )

        return list(reader)


def _load_results_file(path: Path) -> list[HistoricalMatch]:
    """
    Legge uno storico risultati in modo compatibile con vecchio e nuovo schema.

    Il progetto ha usato nel tempo sia ``Date`` sia ``MatchDate``. Questo reader
    accetta entrambi e non richiede più ``Season``.
    """

    if not path.exists():
        return []

    matches: list[HistoricalMatch] = []

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        fieldnames = set(reader.fieldnames or [])

        date_field = "MatchDate" if "MatchDate" in fieldnames else "Date"
        required = {"Home", "Away", "HG", "AG"}

        if not required.issubset(fieldnames):
            return []

        for row in reader:
            # Un risultato privo di entrambi i gol non è una gara conclusa.
            if not _text(row.get("HG")) or not _text(row.get("AG")):
                continue

            matches.append(
                HistoricalMatch(
                    round_number=_to_int(row.get("Round")),
                    match_date=_parse_date(row.get(date_field)),
                    home=_text(row.get("Home")),
                    away=_text(row.get("Away")),
                    home_goals=_to_int(row.get("HG")),
                    away_goals=_to_int(row.get("AG")),
                )
            )

    # Ordinamento deterministico, utile per estrarre correttamente le ultime 5.
    matches.sort(
        key=lambda match: (
            match.match_date or date.min,
            match.round_number,
            _normalize_team(match.home),
            _normalize_team(match.away),
        )
    )

    return matches


def _previous_matches(
    matches: list[HistoricalMatch],
    target_date: date | None,
    target_round: int,
) -> list[HistoricalMatch]:
    """Seleziona esclusivamente partite giocate prima della prediction."""

    previous: list[HistoricalMatch] = []

    for match in matches:
        # Quando entrambe le date esistono, il confronto temporale è prioritario.
        if target_date is not None and match.match_date is not None:
            if match.match_date < target_date:
                previous.append(match)
            continue

        # Fallback per storici senza data: usa la giornata quando disponibile.
        if target_round > 0 and match.round_number > 0:
            if match.round_number < target_round:
                previous.append(match)

    return previous


def _team_points(goals_for: int, goals_against: int) -> int:
    """Converte il risultato di una squadra nei punti di classifica."""

    if goals_for > goals_against:
        return WIN_POINTS

    if goals_for == goals_against:
        return DRAW_POINTS

    return LOSS_POINTS


def _build_snapshots(
    matches: list[HistoricalMatch],
) -> tuple[dict[str, TeamSnapshot], dict[str, list[tuple]]]:
    """
    Ricostruisce classifica e sequenza recente di tutte le squadre della lega.

    La funzione lavora soltanto sulle partite già filtrate come precedenti.
    """

    snapshots: dict[str, TeamSnapshot] = {}
    team_games: dict[str, list[tuple]] = {}

    for match in matches:
        home_key = _normalize_team(match.home)
        away_key = _normalize_team(match.away)

        home_snapshot = snapshots.setdefault(home_key, TeamSnapshot())
        away_snapshot = snapshots.setdefault(away_key, TeamSnapshot())

        home_points = _team_points(match.home_goals, match.away_goals)
        away_points = _team_points(match.away_goals, match.home_goals)

        # Aggiornamento statistiche complessive della squadra di casa.
        home_snapshot.played += 1
        home_snapshot.goals_for += match.home_goals
        home_snapshot.goals_against += match.away_goals
        home_snapshot.points += home_points

        # Aggiornamento statistiche complessive della squadra ospite.
        away_snapshot.played += 1
        away_snapshot.goals_for += match.away_goals
        away_snapshot.goals_against += match.home_goals
        away_snapshot.points += away_points

        # Conteggio esplicito di vittorie, pareggi e sconfitte.
        if match.home_goals > match.away_goals:
            home_snapshot.wins += 1
            away_snapshot.losses += 1
        elif match.home_goals < match.away_goals:
            away_snapshot.wins += 1
            home_snapshot.losses += 1
        else:
            home_snapshot.draws += 1
            away_snapshot.draws += 1

        # Salvataggio cronologico della gara dal punto di vista di ogni squadra.
        team_games.setdefault(home_key, []).append(
            (match.match_date, match.round_number, home_points, match.home_goals, match.away_goals)
        )
        team_games.setdefault(away_key, []).append(
            (match.match_date, match.round_number, away_points, match.away_goals, match.home_goals)
        )

    # Calcolo degli indicatori medi stagionali ricostruiti.
    for snapshot in snapshots.values():
        if snapshot.played:
            snapshot.ppg = snapshot.points / snapshot.played
            snapshot.gf_per_game = snapshot.goals_for / snapshot.played
            snapshot.ga_per_game = snapshot.goals_against / snapshot.played

    # La posizione segue punti, differenza reti, gol fatti e nome normalizzato.
    ordered_teams = sorted(
        snapshots.items(),
        key=lambda item: (
            -item[1].points,
            -(item[1].goals_for - item[1].goals_against),
            -item[1].goals_for,
            item[0],
        ),
    )

    for position, (_, snapshot) in enumerate(ordered_teams, start=1):
        snapshot.position = position

    # Calcolo della forma recente usando al massimo le ultime cinque partite.
    for team_key, games in team_games.items():
        games.sort(key=lambda game: (game[0] or date.min, game[1]))
        recent = games[-LAST_N:]

        if not recent:
            continue

        snapshot = snapshots[team_key]
        snapshot.ppg_last5 = sum(game[2] for game in recent) / len(recent)
        snapshot.wins_last5 = sum(1 for game in recent if game[2] == WIN_POINTS)
        snapshot.gf_last5_avg = sum(game[3] for game in recent) / len(recent)
        snapshot.ga_last5_avg = sum(game[4] for game in recent) / len(recent)

    return snapshots, team_games


def _source_league(row: dict, side: str) -> str:
    """Usa la lega sorgente nei gruppi; altrimenti ricade sul LeagueId del match."""

    return _text(row.get(f"{side}SourceLeagueId")) or _text(row.get("LeagueId"))


def _load_league_matches(
    league_id: str,
    cache: dict[str, list[HistoricalMatch]],
) -> list[HistoricalMatch]:
    """Carica ogni storico una sola volta per evitare letture ripetute."""

    if league_id not in cache:
        cache[league_id] = _load_results_file(RESULTS_DIR / f"{league_id}.csv")

    return cache[league_id]


def _combine_source_matches(
    row: dict,
    cache: dict[str, list[HistoricalMatch]],
) -> list[HistoricalMatch]:
    """Unisce gli storici sorgente necessari per ricostruire entrambe le squadre."""

    source_ids = {
        _source_league(row, "Home"),
        _source_league(row, "Away"),
    }

    combined: list[HistoricalMatch] = []

    for league_id in sorted(source_id for source_id in source_ids if source_id):
        combined.extend(_load_league_matches(league_id, cache))

    # Elimina eventuali duplicati quando entrambe le sorgenti coincidono o si
    # sovrappongono in un CompetitionGroup.
    unique: dict[tuple, HistoricalMatch] = {}

    for match in combined:
        key = (
            match.match_date,
            match.round_number,
            _normalize_team(match.home),
            _normalize_team(match.away),
            match.home_goals,
            match.away_goals,
        )
        unique[key] = match

    return list(unique.values())


def _snapshot_value(snapshot: TeamSnapshot | None, field: str):
    """Legge in sicurezza un attributo della fotografia statistica."""

    if snapshot is None:
        return ""

    value = getattr(snapshot, field)

    if isinstance(value, float):
        return _round_or_blank(value)

    return "" if value is None else value


def _minimum_or_blank(*values: float | None):
    """Calcola un minimo soltanto quando tutti i valori sono disponibili."""

    if any(value is None for value in values):
        return ""

    return round(min(values), 3)


def _maximum_or_blank(*values: float | None):
    """Calcola un massimo soltanto quando tutti i valori sono disponibili."""

    if any(value is None for value in values):
        return ""

    return round(max(values), 3)


def _difference_or_blank(first: float | None, second: float | None):
    """Calcola la differenza assoluta soltanto con due valori disponibili."""

    if first is None or second is None:
        return ""

    return round(abs(first - second), 3)


def _sum_or_blank(*values: float | None):
    """Somma valori diagnostici senza trasformare i dati mancanti in zero."""

    if any(value is None for value in values):
        return ""

    return round(sum(values), 3)


def _enrich_match(
    row: dict,
    results_cache: dict[str, list[HistoricalMatch]],
) -> dict:
    """Aggiunge al match tutte le metriche diagnostiche pre-partita."""

    target_date = _effective_date(row)
    target_round = _to_int(row.get("Round"))

    all_source_matches = _combine_source_matches(row, results_cache)
    previous = _previous_matches(all_source_matches, target_date, target_round)
    snapshots, _ = _build_snapshots(previous)

    home_snapshot = snapshots.get(_normalize_team(row.get("Home")))
    away_snapshot = snapshots.get(_normalize_team(row.get("Away")))

    enriched = dict(row)
    enriched["Outcome"] = _outcome(row)

    # Posizione, partite, punti e indicatori medi delle due squadre.
    enriched["HomePosition"] = _snapshot_value(home_snapshot, "position")
    enriched["AwayPosition"] = _snapshot_value(away_snapshot, "position")
    enriched["PositionGap"] = _difference_or_blank(
        home_snapshot.position if home_snapshot else None,
        away_snapshot.position if away_snapshot else None,
    )
    enriched["HomePlayed"] = _snapshot_value(home_snapshot, "played")
    enriched["AwayPlayed"] = _snapshot_value(away_snapshot, "played")
    enriched["HomePoints"] = _snapshot_value(home_snapshot, "points")
    enriched["AwayPoints"] = _snapshot_value(away_snapshot, "points")
    enriched["HomePPG"] = _snapshot_value(home_snapshot, "ppg")
    enriched["AwayPPG"] = _snapshot_value(away_snapshot, "ppg")
    enriched["PPGGap"] = _difference_or_blank(
        home_snapshot.ppg if home_snapshot else None,
        away_snapshot.ppg if away_snapshot else None,
    )
    enriched["HomeGFpg"] = _snapshot_value(home_snapshot, "gf_per_game")
    enriched["AwayGFpg"] = _snapshot_value(away_snapshot, "gf_per_game")
    enriched["HomeGApg"] = _snapshot_value(home_snapshot, "ga_per_game")
    enriched["AwayGApg"] = _snapshot_value(away_snapshot, "ga_per_game")

    # Sintesi della migliore/peggiore capacità offensiva e difensiva.
    enriched["BestDefenseGApg"] = _minimum_or_blank(
        home_snapshot.ga_per_game if home_snapshot else None,
        away_snapshot.ga_per_game if away_snapshot else None,
    )
    enriched["WorstDefenseGApg"] = _maximum_or_blank(
        home_snapshot.ga_per_game if home_snapshot else None,
        away_snapshot.ga_per_game if away_snapshot else None,
    )
    enriched["BestAttackGFpg"] = _maximum_or_blank(
        home_snapshot.gf_per_game if home_snapshot else None,
        away_snapshot.gf_per_game if away_snapshot else None,
    )
    enriched["WorstAttackGFpg"] = _minimum_or_blank(
        home_snapshot.gf_per_game if home_snapshot else None,
        away_snapshot.gf_per_game if away_snapshot else None,
    )

    # Forma recente ricostruita indipendentemente dai driver già presenti.
    enriched["SnapshotHomePPGLast5"] = _snapshot_value(home_snapshot, "ppg_last5")
    enriched["SnapshotAwayPPGLast5"] = _snapshot_value(away_snapshot, "ppg_last5")
    enriched["SnapshotTotalPPGLast5"] = _sum_or_blank(
        home_snapshot.ppg_last5 if home_snapshot else None,
        away_snapshot.ppg_last5 if away_snapshot else None,
    )
    enriched["SnapshotHomeWinsLast5"] = _snapshot_value(home_snapshot, "wins_last5")
    enriched["SnapshotAwayWinsLast5"] = _snapshot_value(away_snapshot, "wins_last5")
    enriched["SnapshotHomeGFLast5Avg"] = _snapshot_value(home_snapshot, "gf_last5_avg")
    enriched["SnapshotAwayGFLast5Avg"] = _snapshot_value(away_snapshot, "gf_last5_avg")
    enriched["SnapshotHomeGALast5Avg"] = _snapshot_value(home_snapshot, "ga_last5_avg")
    enriched["SnapshotAwayGALast5Avg"] = _snapshot_value(away_snapshot, "ga_last5_avg")
    enriched["SnapshotTotalGoalsLast5Avg"] = _sum_or_blank(
        home_snapshot.gf_last5_avg if home_snapshot else None,
        away_snapshot.gf_last5_avg if away_snapshot else None,
        home_snapshot.ga_last5_avg if home_snapshot else None,
        away_snapshot.ga_last5_avg if away_snapshot else None,
    )

    return enriched


def _autopsy_fieldnames(source_fields: list[str]) -> list[str]:
    """Ordina il report mettendo prima le colonne utili alla lettura quotidiana."""

    preferred = [
        "MatchDate",
        "PredictionDate",
        "LeagueId",
        "Home",
        "Away",
        "Score",
        "Band",
        "Round",
        "Outcome",
        "HG",
        "AG",
        "Goals",
        "Reason",
    ]

    ordered: list[str] = []

    for field in preferred + DERIVED_FIELDS + ENGINE_DRIVER_FIELDS + RECENT_FORM_FIELDS:
        if field not in ordered:
            ordered.append(field)

    # Qualsiasi colonna futura del Laboratory viene conservata in coda.
    for field in source_fields:
        if field not in ordered:
            ordered.append(field)

    return ordered


def _write_autopsy(rows: list[dict], source_fields: list[str]) -> None:
    """Scrive il dettaglio permanente delle partite ALTA KO."""

    fieldnames = _autopsy_fieldnames(source_fields)

    with AUTOPSY_FILE.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def _numeric_values(rows: list[dict], field: str) -> list[float]:
    """Estrae soltanto i valori numerici validi di una colonna."""

    values: list[float] = []

    for row in rows:
        value = _to_float(row.get(field))

        if value is not None:
            values.append(value)

    return values


def _mean_or_blank(values: list[float]):
    """Calcola la media o lascia vuoto quando non esistono osservazioni."""

    return round(statistics.fmean(values), 4) if values else ""


def _median_or_blank(values: list[float]):
    """Calcola la mediana o lascia vuoto quando non esistono osservazioni."""

    return round(statistics.median(values), 4) if values else ""


def _write_patterns(high_rows: list[dict]) -> None:
    """Confronta sistematicamente ALTA OK e ALTA KO sulle stesse metriche."""

    ok_rows = [row for row in high_rows if row.get("Outcome") == "OK"]
    ko_rows = [row for row in high_rows if row.get("Outcome") == "KO"]

    candidate_fields = []

    for field in ENGINE_DRIVER_FIELDS + RECENT_FORM_FIELDS + DERIVED_FIELDS:
        if field not in candidate_fields:
            candidate_fields.append(field)

    output_rows: list[dict] = []

    for field in candidate_fields:
        ok_values = _numeric_values(ok_rows, field)
        ko_values = _numeric_values(ko_rows, field)

        ok_mean = statistics.fmean(ok_values) if ok_values else None
        ko_mean = statistics.fmean(ko_values) if ko_values else None

        output_rows.append(
            {
                "Metric": field,
                "HighOKCount": len(ok_values),
                "HighKOCount": len(ko_values),
                "HighOKMean": _round_or_blank(ok_mean, 4),
                "HighKOMean": _round_or_blank(ko_mean, 4),
                "MeanDeltaOKMinusKO": _round_or_blank(
                    ok_mean - ko_mean
                    if ok_mean is not None and ko_mean is not None
                    else None,
                    4,
                ),
                "HighOKMedian": _median_or_blank(ok_values),
                "HighKOMedian": _median_or_blank(ko_values),
            }
        )

    # Le metriche con maggiore differenza assoluta vengono mostrate per prime.
    output_rows.sort(
        key=lambda row: abs(_to_float(row.get("MeanDeltaOKMinusKO")) or 0),
        reverse=True,
    )

    fieldnames = [
        "Metric",
        "HighOKCount",
        "HighKOCount",
        "HighOKMean",
        "HighKOMean",
        "MeanDeltaOKMinusKO",
        "HighOKMedian",
        "HighKOMedian",
    ]

    with PATTERNS_FILE.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(output_rows)


def _write_daily(high_rows: list[dict]) -> None:
    """Produce una serie giornaliera per verificare il calo recente della fascia."""

    grouped: dict[str, list[dict]] = {}

    for row in high_rows:
        effective = _effective_date(row)

        if effective is None:
            continue

        grouped.setdefault(effective.isoformat(), []).append(row)

    output_rows: list[dict] = []

    for day in sorted(grouped):
        rows = grouped[day]
        ok_count = sum(1 for row in rows if row.get("Outcome") == "OK")
        ko_count = sum(1 for row in rows if row.get("Outcome") == "KO")
        total = ok_count + ko_count

        output = {
            "Date": day,
            "HighMatches": total,
            "HighOK": ok_count,
            "HighKO": ko_count,
            "HighPrecision": round(ok_count / total * 100, 2) if total else "",
        }

        # Aggiunge medie giornaliere dei driver più leggibili e rilevanti.
        for field in [
            "Score",
            "HomeAttackScore",
            "AwayAttackScore",
            "HomeDefenseWeaknessScore",
            "AwayDefenseWeaknessScore",
            "TotalPPGLast5",
            "BestDefenseGApg",
            "WorstAttackGFpg",
        ]:
            output[f"Avg{field}"] = _mean_or_blank(_numeric_values(rows, field))

        output_rows.append(output)

    fieldnames = [
        "Date",
        "HighMatches",
        "HighOK",
        "HighKO",
        "HighPrecision",
        "AvgScore",
        "AvgHomeAttackScore",
        "AvgAwayAttackScore",
        "AvgHomeDefenseWeaknessScore",
        "AvgAwayDefenseWeaknessScore",
        "AvgTotalPPGLast5",
        "AvgBestDefenseGApg",
        "AvgWorstAttackGFpg",
    ]

    with DAILY_FILE.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(output_rows)


def main() -> int:
    """Esegue l'intera diagnostica e restituisce un codice d'uscita standard."""

    rows = _load_laboratory_matches()
    source_fields = list(rows[0].keys()) if rows else []

    # Vengono analizzate solo prediction concluse con esito determinabile.
    high_rows = []

    for row in rows:
        outcome = _outcome(row)

        if not _is_high_band(row.get("Band")) or outcome not in {"OK", "KO"}:
            continue

        normalized = dict(row)
        normalized["Outcome"] = outcome
        high_rows.append(normalized)

    results_cache: dict[str, list[HistoricalMatch]] = {}
    enriched_high_rows: list[dict] = []

    for row in high_rows:
        enriched_high_rows.append(_enrich_match(row, results_cache))

    # Ordinamento cronologico, con i casi più recenti in cima all'autopsia.
    enriched_high_rows.sort(
        key=lambda row: (
            _effective_date(row) or date.min,
            _text(row.get("LeagueId")),
            _text(row.get("Home")),
        ),
        reverse=True,
    )

    high_ko_rows = [
        row for row in enriched_high_rows if row.get("Outcome") == "KO"
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_autopsy(high_ko_rows, source_fields)
    _write_patterns(enriched_high_rows)
    _write_daily(enriched_high_rows)

    high_ok_count = sum(
        1 for row in enriched_high_rows if row.get("Outcome") == "OK"
    )

    print(f"FASCIA ALTA concluse analizzate : {len(enriched_high_rows)}")
    print(f"FASCIA ALTA OK                  : {high_ok_count}")
    print(f"FASCIA ALTA KO                  : {len(high_ko_rows)}")
    print(f"Autopsia scritta                : {AUTOPSY_FILE}")
    print(f"Pattern scritti                 : {PATTERNS_FILE}")
    print(f"Andamento giornaliero scritto   : {DAILY_FILE}")

    return 0


# Permette sia l'esecuzione diretta sia il richiamo da ``run_all.py``.
if __name__ == "__main__":
    raise SystemExit(main())
