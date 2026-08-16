"""
===============================================================================
GioOver2.5 - rank_matches_v2.py
===============================================================================

SCOPO
-----
Generare ranking Over 2.5 anche per partite tra squadre provenienti da
LeagueId differenti, purché appartenenti allo stesso CompetitionGroup.

CASI SPECIALI
-------------
- USL League Two: play-in e playoff possono coinvolgere squadre provenienti
  da divisioni differenti dello stesso CompetitionGroup.
- MLS Next Pro: le classifiche sono divisionali, ma le squadre disputano anche
  gare inter-divisione. Ogni partita è memorizzata una sola volta, nel file
  della divisione della squadra di casa; per statistiche e PPG della singola
  squadra devono però valere tutte le sue gare, indipendentemente dal file in
  cui sono archiviate.

INPUT
-----
CSV con colonne obbligatorie:
    LeagueId;MatchDate;Home;Away

DATI STORICI
------------
- Per le leghe senza CompetitionGroup viene letto il solo storico LeagueId.
- Per le leghe con CompetitionGroup vengono letti tutti gli storici risultati
  delle LeagueId appartenenti al gruppo.
- Per MLS Next Pro vengono letti tutti i LeagueId MLS Next Pro presenti
  letteralmente nel registry: nessun LeagueId viene costruito o inventato.

OUTPUT AGGIUNTIVO
-----------------
HomeSourceLeagueId e AwaySourceLeagueId indicano gli storici divisionali dai
quali sono state recuperate le squadre.
===============================================================================
"""

import argparse
import csv
import shutil
from datetime import date, datetime
from pathlib import Path

from .history import read_results_file
from .match_statistics import build_match_statistics
from .registry import get_league_info
from .ranking_history import append_predictions
from .engines.factory import get_engine, get_available_engines
from .team_names import canonicalize_team_display_name, normalize_team_name


INPUT_REQUIRED_COLUMNS = {"LeagueId", "MatchDate", "Home", "Away"}
RESULTS_DIR = Path("data/storico/risultati")
OUTPUT_DIR = Path("data/output_ranking")
INPUT_ARCHIVE_DIR = Path("data/input_partite/oldmatches")
OUTPUT_ARCHIVE_NAME = "old_ranking"

# Regola campione immaturo:
# - HomePlayed + AwayPlayed < 4  -> partita esclusa
# - totale >= 4 ma almeno una squadra < 5 gare -> score calcolato comunque
#   e, se sarebbe ALTA, Band = IMM-ALTA-# dove # è il totale gare
# - entrambe >= 5 -> fascia normale
MIN_TOTAL_TEAM_MATCHES = 4
MATURE_TEAM_MATCHES = 5
REGISTRY_FILE = Path("data/league_registry.csv")
MLS_NEXT_PRO_PREFIX = "USA_MLSNextPro_"

FIELDNAMES = [
    "MatchDate",
    "LeagueId",
    "Home",
    "Away",
    "Score",
    "Band",
    "Round",
    "PredictionDate",
    "HomeSourceLeagueId",
    "AwaySourceLeagueId",
    "CompetitionGroup",
    "Reason",
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
    "AlgorithmVersion",
]


def _normalize_team(value: str) -> str:
    return canonicalize_team_display_name(value).casefold()


def _parse_date(value) -> date | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _match_date(match) -> date | None:
    return _parse_date(str(getattr(match, "date", "")))


def read_registry() -> list[dict]:
    if not REGISTRY_FILE.exists():
        raise FileNotFoundError(f"Registro leghe non trovato: {REGISTRY_FILE}")
    with REGISTRY_FILE.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def get_competition_group(league_id: str, registry_rows: list[dict]) -> str:
    for row in registry_rows:
        if str(row.get("LeagueId", "")).strip() == league_id:
            return str(row.get("CompetitionGroup", "")).strip()
    return ""


def is_mls_next_pro_league(league_id: str) -> bool:
    return str(league_id or "").startswith(MLS_NEXT_PRO_PREFIX)


def get_group_league_ids(
    league_id: str,
    competition_group: str,
    registry_rows: list[dict],
) -> list[str]:
    """
    Restituisce i LeagueId da caricare per la partita.

    MLS Next Pro è un caso speciale: nel registry le quattro divisioni sono
    LeagueId distinti e non hanno bisogno di un CompetitionGroup artificiale.
    Vengono quindi selezionati esclusivamente i LeagueId già presenti nel
    registry e che iniziano con il prefisso canonico USA_MLSNextPro_.
    """

    if is_mls_next_pro_league(league_id):
        ids = [
            str(row.get("LeagueId", "")).strip()
            for row in registry_rows
            if is_mls_next_pro_league(str(row.get("LeagueId", "")).strip())
        ]
        return [value for value in ids if value]

    if not competition_group:
        return [league_id]

    ids = [
        str(row.get("LeagueId", "")).strip()
        for row in registry_rows
        if str(row.get("CompetitionGroup", "")).strip() == competition_group
    ]
    return [value for value in ids if value]


def load_group_histories(league_ids: list[str]) -> dict[str, list]:
    histories = {}
    for source_league_id in league_ids:
        path = RESULTS_DIR / f"{source_league_id}.csv"
        if path.exists():
            histories[source_league_id] = read_results_file(path)
    return histories


def find_team_source_league(
    team: str,
    histories: dict[str, list],
    match_date: date | None,
    fallback_league_id: str | None = None,
) -> str | None:
    """
    Individua lo storico di provenienza di una squadra per i casi ordinari e
    per i CompetitionGroup tradizionali.
    """

    normalized = _normalize_team(team)
    candidates = []

    for league_id, matches in histories.items():
        team_dates = []

        for match in matches:
            teams = {
                _normalize_team(getattr(match, "home", "")),
                _normalize_team(getattr(match, "away", "")),
            }

            if normalized not in teams:
                continue

            current_date = _match_date(match)
            if current_date is None:
                continue
            if match_date is not None and current_date >= match_date:
                continue

            team_dates.append(current_date)

        if team_dates:
            candidates.append((max(team_dates), league_id))

    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]

    if fallback_league_id:
        print(
            f"[WARN] {team}: nessuna partita storica precedente. "
            f"Utilizzo {fallback_league_id} come lega di appartenenza."
        )
        return fallback_league_id

    return None


def find_mls_next_pro_home_league(
    team: str,
    histories: dict[str, list],
) -> str | None:
    """
    Determina la divisione MLS Next Pro dalla squadra di casa.

    Gli storici MLS Next Pro sono archiviati una sola volta: il LeagueId del
    file corrisponde alla divisione della Home. Per questo, per stabilire la
    divisione canonica di una squadra, cerchiamo il file nel quale la squadra
    compare come Home. Non usiamo la semplice presenza come Away, perché le
    gare inter-divisione la farebbero comparire anche in altri file.

    La ricerca può usare tutta la stagione: conoscere la divisione di una
    squadra non costituisce informazione futura sul risultato delle partite.
    """

    normalized = _normalize_team(team)
    candidates = []

    for league_id, matches in histories.items():
        home_dates = []

        for match in matches:
            if _normalize_team(getattr(match, "home", "")) != normalized:
                continue

            current_date = _match_date(match)
            if current_date is not None:
                home_dates.append(current_date)

        if home_dates:
            candidates.append((max(home_dates), league_id))

    if not candidates:
        return None

    candidates.sort(reverse=True)
    return candidates[0][1]


def get_mls_next_pro_division_team_names(
    source_league_id: str,
    histories: dict[str, list],
) -> set[str]:
    """
    Ricava le squadre appartenenti a una divisione MLS Next Pro.

    I membri della divisione sono identificati dalle squadre che compaiono
    come Home nel relativo file. Successivamente vengono raccolte, da tutti gli
    storici MLS Next Pro, le forme testuali corrispondenti agli stessi nomi,
    così da ridurre problemi dovuti a piccole varianti di denominazione.
    """

    source_matches = histories.get(source_league_id, [])
    member_keys = {
        _normalize_team(getattr(match, "home", ""))
        for match in source_matches
        if str(getattr(match, "home", "")).strip()
    }

    names: set[str] = set()

    for matches in histories.values():
        for match in matches:
            for value in (
                getattr(match, "home", ""),
                getattr(match, "away", ""),
            ):
                name = canonicalize_team_display_name(value)
                if name and _normalize_team(name) in member_keys:
                    names.add(name)

    return names


def _match_has_final_score(match) -> bool:
    """Restituisce True quando lo storico contiene un risultato concluso."""

    goal_pairs = (
        ("hg", "ag"),
        ("home_goals", "away_goals"),
        ("home_score", "away_score"),
    )

    for home_field, away_field in goal_pairs:
        home_value = getattr(match, home_field, None)
        away_value = getattr(match, away_field, None)

        if home_value not in (None, "") and away_value not in (None, ""):
            return True

    status = str(getattr(match, "status", "") or "").strip().casefold()
    return status in {
        "finale",
        "final",
        "dopo supplementari",
        "rigori",
    }


def _match_goals(match) -> tuple[int, int] | None:
    """Recupera il punteggio finale da MatchResult."""

    goal_pairs = (
        ("home_goals", "away_goals"),
        ("hg", "ag"),
        ("home_score", "away_score"),
    )

    for home_field, away_field in goal_pairs:
        home_value = getattr(match, home_field, None)
        away_value = getattr(match, away_field, None)

        if home_value in (None, "") or away_value in (None, ""):
            continue

        try:
            return int(home_value), int(away_value)
        except (TypeError, ValueError):
            continue

    return None


def _team_history_matches(
    histories: dict[str, list],
    source_league_id: str,
    include_all_histories: bool,
) -> list:
    if include_all_histories:
        return [
            match
            for source_matches in histories.values()
            for match in source_matches
        ]

    return histories.get(source_league_id, [])


def calculate_team_ppg_before_match(
    *,
    team: str,
    source_league_id: str,
    histories: dict[str, list],
    match_date: date | None,
    include_all_histories: bool = False,
) -> tuple[int, int, float]:
    """
    Calcola partite giocate, punti e PPG della squadra prima della partita.

    Nei casi ordinari usa lo storico della lega/divisione di origine.
    Per MLS Next Pro ``include_all_histories=True`` fa valere anche le gare
    inter-divisione archiviate nei file delle divisioni avversarie.
    """

    matches = _team_history_matches(
        histories,
        source_league_id,
        include_all_histories,
    )

    canonical_team = normalize_team_name(source_league_id, team)
    played = 0
    points = 0

    for match in matches:
        current_date = _match_date(match)
        if current_date is None:
            continue
        if match_date is not None and current_date >= match_date:
            continue

        goals = _match_goals(match)
        if goals is None:
            continue

        home_goals, away_goals = goals
        historical_home = normalize_team_name(
            source_league_id,
            getattr(match, "home", ""),
        )
        historical_away = normalize_team_name(
            source_league_id,
            getattr(match, "away", ""),
        )

        if canonical_team == historical_home:
            played += 1
            if home_goals > away_goals:
                points += 3
            elif home_goals == away_goals:
                points += 1

        elif canonical_team == historical_away:
            played += 1
            if away_goals > home_goals:
                points += 3
            elif away_goals == home_goals:
                points += 1

    ppg = points / played if played > 0 else 0.0
    return played, points, ppg


def calculate_team_ga_last5_before_match(
    *,
    team: str,
    source_league_id: str,
    histories: dict[str, list],
    match_date: date | None,
    include_all_histories: bool = False,
) -> float | None:
    """
    Media gol subiti nelle ultime 5 gare concluse precedenti alla MatchDate.

    Per MLS Next Pro può usare tutte le divisioni, così una trasferta
    inter-divisione non viene persa dal campione recente.
    """

    matches = _team_history_matches(
        histories,
        source_league_id,
        include_all_histories,
    )
    canonical_team = normalize_team_name(source_league_id, team)
    observations = []

    for match in matches:
        current_date = _match_date(match)
        if current_date is None:
            continue
        if match_date is not None and current_date >= match_date:
            continue

        goals = _match_goals(match)
        if goals is None:
            continue

        home_goals, away_goals = goals
        historical_home = normalize_team_name(
            source_league_id,
            getattr(match, "home", ""),
        )
        historical_away = normalize_team_name(
            source_league_id,
            getattr(match, "away", ""),
        )

        if canonical_team == historical_home:
            observations.append((current_date, away_goals))
        elif canonical_team == historical_away:
            observations.append((current_date, home_goals))

    observations.sort(key=lambda item: item[0])
    recent = observations[-5:]

    if len(recent) < 5:
        return None

    return round(
        sum(goals_against for _, goals_against in recent) / 5.0,
        4,
    )


def count_completed_rounds_before(
    matches: list,
    match_date: date | None,
) -> int:
    """Conta i turni distinti conclusi prima della partita da analizzare."""

    completed_rounds = set()

    for match in matches:
        current_date = _match_date(match)
        if current_date is None:
            continue
        if match_date is not None and current_date >= match_date:
            continue
        if not _match_has_final_score(match):
            continue

        round_value = str(getattr(match, "round", "") or "").strip()
        if round_value:
            completed_rounds.add(round_value)

    return len(completed_rounds)


def infer_next_round(matches: list) -> int:
    if not matches:
        return 1
    return max(match.round for match in matches) + 1


def score_value(score, field: str):
    return getattr(score, field, "")


def read_matches_to_rank(path: str | Path) -> list[dict]:
    input_path = Path(path)
    if not input_path.exists():
        raise FileNotFoundError(f"File input partite non trovato: {input_path}")

    with input_path.open("r", newline="", encoding="utf-8-sig") as f:
        lines = [line for line in f if line.strip()]

    reader = csv.DictReader(lines, delimiter=";")
    missing = INPUT_REQUIRED_COLUMNS - set(reader.fieldnames or [])

    if missing:
        raise ValueError(
            "File input partite non valido. Mancano le colonne: "
            + ", ".join(sorted(missing))
        )

    rows = list(reader)

    for row in rows:
        row["Home"] = canonicalize_team_display_name(row.get("Home", ""))
        row["Away"] = canonicalize_team_display_name(row.get("Away", ""))

    return rows


def build_output_row(
    *,
    prediction_date: str,
    match_date: str,
    algorithm_version: str,
    league_id: str,
    round_number: int,
    home: str,
    away: str,
    home_source_league_id: str,
    away_source_league_id: str,
    competition_group: str,
    score,
    band_override: str | None = None,
) -> dict:
    return {
        "MatchDate": match_date,
        "LeagueId": league_id,
        "Home": canonicalize_team_display_name(home),
        "Away": canonicalize_team_display_name(away),
        "Score": score_value(score, "score"),
        "Band": (
            band_override
            if band_override is not None
            else score_value(score, "band")
        ),
        "Round": round_number,
        "PredictionDate": prediction_date,
        "HomeSourceLeagueId": home_source_league_id,
        "AwaySourceLeagueId": away_source_league_id,
        "CompetitionGroup": competition_group,
        "Reason": score_value(score, "reason"),
        "RankingGapScore": score_value(score, "ranking_gap_score"),
        "HomeAttackScore": score_value(score, "home_attack_score"),
        "AwayAttackScore": score_value(score, "away_attack_score"),
        "HomeDefenseWeaknessScore": score_value(score, "home_defense_weakness_score"),
        "AwayDefenseWeaknessScore": score_value(score, "away_defense_weakness_score"),
        "HomeLast10OverScore": score_value(score, "home_last10_over_score"),
        "AwayLast10OverScore": score_value(score, "away_last10_over_score"),
        "HomeVenueOverScore": score_value(score, "home_venue_over_score"),
        "AwayVenueOverScore": score_value(score, "away_venue_over_score"),
        "BTTSProfileScore": score_value(score, "btts_profile_score"),
        "AlgorithmVersion": algorithm_version,
    }


def _collision_safe_destination(destination: Path) -> Path:
    if not destination.exists():
        return destination

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = destination.with_name(
        f"{destination.stem}_{timestamp}{destination.suffix}"
    )

    counter = 1
    while candidate.exists():
        candidate = destination.with_name(
            f"{destination.stem}_{timestamp}_{counter}{destination.suffix}"
        )
        counter += 1

    return candidate


def archive_output_rankings(engine_name: str) -> int:
    engine_output_dir = OUTPUT_DIR / engine_name
    archive_dir = engine_output_dir / OUTPUT_ARCHIVE_NAME

    engine_output_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    archived = 0

    for csv_file in sorted(engine_output_dir.glob("*.csv")):
        destination = _collision_safe_destination(archive_dir / csv_file.name)
        shutil.move(str(csv_file), str(destination))
        print(f"[ARCHIVE] {csv_file} -> {destination}")
        archived += 1

    print(f"[ARCHIVE] {engine_name}: {archived} ranking archiviati.")
    return archived


def archive_input_file(input_path: Path) -> Path:
    if not input_path.exists():
        raise FileNotFoundError(
            f"File input non più disponibile per l'archiviazione: {input_path}"
        )

    INPUT_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    destination = _collision_safe_destination(INPUT_ARCHIVE_DIR / input_path.name)

    shutil.move(str(input_path), str(destination))
    print(f"[ARCHIVE] Input: {input_path} -> {destination}")
    return destination


def rank_matches(
    input_file: str | Path,
    output_file: str | Path,
    engine_name: str = "v20",
) -> None:
    engine = get_engine(engine_name)
    prediction_date = date.today().isoformat()
    algorithm_version = engine.ENGINE_VERSION
    registry_rows = read_registry()
    rows = read_matches_to_rank(input_file)
    results = []

    for row in rows:
        league_id = row["LeagueId"].strip()
        match_date_text = row["MatchDate"].strip()
        match_date_value = _parse_date(match_date_text)
        home = canonicalize_team_display_name(row["Home"])
        away = canonicalize_team_display_name(row["Away"])

        league_info = get_league_info(league_id)
        competition_group = get_competition_group(league_id, registry_rows)
        mls_next_pro = is_mls_next_pro_league(league_id)

        group_league_ids = get_group_league_ids(
            league_id,
            competition_group,
            registry_rows,
        )
        histories = load_group_histories(group_league_ids)

        if not histories:
            print(
                f"[SKIP] {league_id}: nessuno storico risultati disponibile "
                f"(minimo {MIN_TOTAL_TEAM_MATCHES} gare complessive Home+Away)."
            )
            continue

        if mls_next_pro:
            home_source = find_mls_next_pro_home_league(home, histories)
            away_source = find_mls_next_pro_home_league(away, histories)

            # Per convenzione MLS Next Pro, il LeagueId della partita è la
            # divisione della squadra di casa. Se Home non ha ancora una gara
            # casalinga nello storico, questa informazione è quindi già nota.
            if home_source is None:
                home_source = league_id

            # Per Away non inventiamo alcuna divisione: se non è ricavabile
            # dagli storici, la partita viene saltata con un messaggio chiaro.
            if away_source is None:
                print(
                    f"[SKIP][MLSNP] {home} - {away}: divisione di {away} "
                    "non determinabile dagli storici MLS Next Pro."
                )
                continue

            home_standing_teams = get_mls_next_pro_division_team_names(
                home_source,
                histories,
            )
            away_standing_teams = get_mls_next_pro_division_team_names(
                away_source,
                histories,
            )
        else:
            fallback_league_id = (
                league_id
                if not competition_group
                else None
            )

            home_source = find_team_source_league(
                home,
                histories,
                match_date_value,
                fallback_league_id=fallback_league_id,
            )
            away_source = find_team_source_league(
                away,
                histories,
                match_date_value,
                fallback_league_id=fallback_league_id,
            )

            if home_source is None:
                home_source = league_id
            if away_source is None:
                away_source = league_id

            home_standing_teams = None
            away_standing_teams = None

        use_all_team_histories = mls_next_pro

        (
            home_played,
            home_points,
            home_ppg,
        ) = calculate_team_ppg_before_match(
            team=home,
            source_league_id=home_source,
            histories=histories,
            match_date=match_date_value,
            include_all_histories=use_all_team_histories,
        )

        (
            away_played,
            away_points,
            away_ppg,
        ) = calculate_team_ppg_before_match(
            team=away,
            source_league_id=away_source,
            histories=histories,
            match_date=match_date_value,
            include_all_histories=use_all_team_histories,
        )

        total_played = home_played + away_played

        if total_played < MIN_TOTAL_TEAM_MATCHES:
            print(
                f"[SKIP] {league_id} | {home} - {away}: "
                f"GP={home_played}/{away_played}, totale={total_played}; "
                f"minimo richiesto: {MIN_TOTAL_TEAM_MATCHES}."
            )
            continue

        immature_sample = (
            home_played < MATURE_TEAM_MATCHES
            or away_played < MATURE_TEAM_MATCHES
        )

        # Ogni riga fisica è presente in un solo storico: unire i file MLS
        # Next Pro consente di recuperare tutte le gare inter-divisione senza
        # duplicare le partite.
        statistics_matches = [
            match
            for source_matches in histories.values()
            for match in source_matches
        ]

        target_matches = histories.get(league_id, [])
        round_number = infer_next_round(target_matches)
        statistics_before_round = infer_next_round(statistics_matches)

        match_stats = build_match_statistics(
            matches=statistics_matches,
            home_team=home,
            away_team=away,
            before_round=statistics_before_round,
            home_standing_teams=home_standing_teams,
            away_standing_teams=away_standing_teams,
        )

        requires_played_counts = bool(
            getattr(engine, "REQUIRES_PLAYED_COUNTS", False)
        )
        requires_defense_last5 = bool(
            getattr(engine, "REQUIRES_DEFENSE_LAST5", False)
        )

        engine_kwargs = {}

        if requires_played_counts:
            (
                home_played_for_engine,
                _home_points_for_engine,
                _home_ppg_for_engine,
            ) = calculate_team_ppg_before_match(
                team=home,
                source_league_id=home_source,
                histories=histories,
                match_date=match_date_value,
                include_all_histories=use_all_team_histories,
            )

            (
                away_played_for_engine,
                _away_points_for_engine,
                _away_ppg_for_engine,
            ) = calculate_team_ppg_before_match(
                team=away,
                source_league_id=away_source,
                histories=histories,
                match_date=match_date_value,
                include_all_histories=use_all_team_histories,
            )

            engine_kwargs.update(
                home_played=home_played_for_engine,
                away_played=away_played_for_engine,
            )

        if requires_defense_last5:
            engine_kwargs.update(
                home_ga_last5=calculate_team_ga_last5_before_match(
                    team=home,
                    source_league_id=home_source,
                    histories=histories,
                    match_date=match_date_value,
                    include_all_histories=use_all_team_histories,
                ),
                away_ga_last5=calculate_team_ga_last5_before_match(
                    team=away,
                    source_league_id=away_source,
                    histories=histories,
                    match_date=match_date_value,
                    include_all_histories=use_all_team_histories,
                ),
            )

        score = engine.calculate_score(
            match_stats,
            league_info,
            **engine_kwargs,
        )

        contextual_band = None
        apply_contextual_band = getattr(engine, "apply_contextual_band", None)

        if callable(apply_contextual_band):
            base_band = score_value(score, "band")

            contextual_band = apply_contextual_band(
                base_band,
                home_played=home_played,
                away_played=away_played,
                home_ppg=home_ppg,
                away_ppg=away_ppg,
            )

            if contextual_band != base_band:
                print(
                    f"[{engine_name}][PROX] {home} - {away}: "
                    f"{base_band} -> {contextual_band} | "
                    f"GP={home_played}/{away_played} | "
                    f"PPG={home_ppg:.3f}/{away_ppg:.3f} | "
                    f"gap={abs(home_ppg - away_ppg):.3f}"
                )

        base_band = score_value(score, "band")

        if immature_sample and base_band == "ALTA":
            contextual_band = f"IMM-ALTA-{total_played}"
            print(
                f"[{engine_name}][IMM] {home} - {away}: "
                f"ALTA -> {contextual_band} | "
                f"GP={home_played}/{away_played} | totale={total_played}"
            )

        results.append(
            build_output_row(
                prediction_date=prediction_date,
                match_date=match_date_text,
                algorithm_version=algorithm_version,
                league_id=league_id,
                round_number=round_number,
                home=home,
                away=away,
                home_source_league_id=home_source,
                away_source_league_id=away_source,
                competition_group=competition_group,
                score=score,
                band_override=contextual_band,
            )
        )

    results.sort(key=lambda x: float(x["Score"] or 0), reverse=True)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter=";")
        writer.writeheader()
        writer.writerows(results)

    print(f"[{engine_name}] Ranking generato: {output_path.resolve()}")
    append_predictions(
        results,
        engine_name=engine_name,
        algorithm_version=algorithm_version,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera ranking partite GioOver2.5 v2.0"
    )
    parser.add_argument("input_file", help="CSV partite da analizzare")
    parser.add_argument(
        "--engine",
        default="v20",
        choices=get_available_engines() + ["all"],
        help="Motore di scoring da usare",
    )
    parser.add_argument("--output", default=None, help="CSV output ranking")
    args = parser.parse_args()

    input_path = Path(args.input_file)
    base_name = input_path.stem.replace("partite", "ranking")

    if args.engine == "all":
        engine_names = get_available_engines()

        for engine_name in engine_names:
            archive_output_rankings(engine_name)

        for engine_name in engine_names:
            output_file = (
                OUTPUT_DIR
                / engine_name
                / f"{base_name}_{engine_name}.csv"
            )
            rank_matches(args.input_file, output_file, engine_name)
    else:
        archive_output_rankings(args.engine)

        output_file = (
            Path(args.output)
            if args.output
            else OUTPUT_DIR / args.engine / f"{base_name}_{args.engine}.csv"
        )
        rank_matches(args.input_file, output_file, args.engine)

    archive_input_file(input_path)


if __name__ == "__main__":
    main()
