"""
===============================================================================
GioOver2.5 - rank_matches_v2.py
===============================================================================

SCOPO
-----
Generare ranking Over 2.5 anche per partite tra squadre provenienti da
LeagueId differenti, purché appartenenti allo stesso CompetitionGroup.

CASO PRINCIPALE
---------------
USL League Two americana: play-in e playoff possono coinvolgere squadre di
registri divisionali differenti.

INPUT
-----
CSV con colonne obbligatorie:
    LeagueId;MatchDate;Home;Away

LeagueId rappresenta la competizione della partita da analizzare, ad esempio:
    USA_USLLeagueTwo_PlayIn_2026

DATI STORICI
------------
- Per le leghe senza CompetitionGroup viene letto il solo storico LeagueId.
- Per le leghe con CompetitionGroup vengono letti tutti gli storici risultati
  delle LeagueId appartenenti al gruppo.
- Home e Away vengono cercate negli storici del gruppo per individuare la
  LeagueId di origine di ciascuna squadra.

OUTPUT AGGIUNTIVO
-----------------
HomeSourceLeagueId e AwaySourceLeagueId indicano gli storici divisionali dai
quali sono state recuperate le squadre.

LIMITAZIONI
-----------
- Se una squadra compare in più LeagueId del gruppo, lo script sceglie la lega
  in cui possiede la partita storica più recente prima di MatchDate.
- Se una squadra non viene trovata, viene sollevato un errore esplicito.
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
from .team_names import normalize_team_name


INPUT_REQUIRED_COLUMNS = {"LeagueId", "MatchDate", "Home", "Away"}
RESULTS_DIR = Path("data/storico/risultati")
OUTPUT_DIR = Path("data/output_ranking")
INPUT_ARCHIVE_DIR = Path("data/input_partite/oldmatches")
OUTPUT_ARCHIVE_NAME = "old_ranking"
MIN_COMPLETED_ROUNDS_PER_LEAGUE = 5
REGISTRY_FILE = Path("data/league_registry.csv")

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
    return " ".join(str(value or "").strip().casefold().split())


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


def get_group_league_ids(
    league_id: str,
    competition_group: str,
    registry_rows: list[dict],
) -> list[str]:
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
) -> str:
    """
    Individua lo storico di provenienza di una squadra.

    Se la squadra non ha ancora disputato partite e appartiene a una lega
    ordinaria, restituisce il LeagueId della partita tramite fallback.

    Nei CompetitionGroup il fallback non viene passato, perché una squadra
    deve essere associata alla propria divisione di origine.
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

    raise ValueError(
        f"Squadra non trovata negli storici del CompetitionGroup: {team}"
    )

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
    """
    Recupera il punteggio finale da MatchResult senza assumere un solo
    schema di attributi.
    """

    goal_pairs = (
        ("home_goals", "away_goals"),
        ("hg", "ag"),
        ("home_score", "away_score"),
    )

    for home_field, away_field in goal_pairs:
        home_value = getattr(
            match,
            home_field,
            None,
        )
        away_value = getattr(
            match,
            away_field,
            None,
        )

        if (
            home_value in (None, "")
            or away_value in (None, "")
        ):
            continue

        try:
            return (
                int(home_value),
                int(away_value),
            )
        except (TypeError, ValueError):
            continue

    return None


def calculate_team_ppg_before_match(
    *,
    team: str,
    source_league_id: str,
    histories: dict[str, list],
    match_date: date | None,
) -> tuple[int, int, float]:
    """
    Calcola partite giocate, punti e PPG della squadra PRIMA della partita.

    Per i CompetitionGroup usa esclusivamente lo storico della divisione
    d'origine individuata da find_team_source_league. In questo modo il PPG
    rappresenta il rendimento nel campionato di appartenenza e non miscela
    classifiche di divisioni differenti.
    """

    matches = histories.get(
        source_league_id,
        [],
    )

    canonical_team = normalize_team_name(
        source_league_id,
        team,
    )

    played = 0
    points = 0

    for match in matches:
        current_date = _match_date(
            match
        )

        if current_date is None:
            continue

        if (
            match_date is not None
            and current_date >= match_date
        ):
            continue

        goals = _match_goals(
            match
        )

        if goals is None:
            continue

        home_goals, away_goals = goals

        historical_home = normalize_team_name(
            source_league_id,
            getattr(
                match,
                "home",
                "",
            ),
        )

        historical_away = normalize_team_name(
            source_league_id,
            getattr(
                match,
                "away",
                "",
            ),
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

    ppg = (
        points / played
        if played > 0
        else 0.0
    )

    return (
        played,
        points,
        ppg,
    )


def count_completed_rounds_before(
    matches: list,
    match_date: date | None,
) -> int:
    """Conta i turni distinti conclusi prima della partita da analizzare.

    La soglia riguarda i turni realmente disponibili nello storico, non il
    semplice numero di righe. Una lega con molte gare del primo turno resta
    quindi non predicibile finché non possiede almeno cinque turni conclusi.
    """

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
    return list(reader)


def build_output_row(
    *, prediction_date: str, match_date: str, algorithm_version: str,
    league_id: str, round_number: int, home: str, away: str,
    home_source_league_id: str, away_source_league_id: str,
    competition_group: str, score,
    band_override: str | None = None,
) -> dict:
    return {
    "MatchDate": match_date,
    "LeagueId": league_id,
    "Home": home,
    "Away": away,
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
    """
    Restituisce una destinazione libera senza sovrascrivere file esistenti.

    Se il nome è già presente, aggiunge data e ora; in caso di una seconda
    collisione nello stesso secondo, aggiunge anche un contatore progressivo.
    """

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
    """
    Sposta i ranking CSV precedenti dell'engine nella sua old_ranking.

    Struttura:
        data/output_ranking/<engine>/*.csv
            -> data/output_ranking/<engine>/old_ranking/

    La funzione analizza soltanto i CSV presenti direttamente nella cartella
    dell'engine e non entra ricorsivamente nella cartella di archivio.
    """

    engine_output_dir = OUTPUT_DIR / engine_name
    archive_dir = engine_output_dir / OUTPUT_ARCHIVE_NAME

    engine_output_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    archived = 0

    for csv_file in sorted(engine_output_dir.glob("*.csv")):
        destination = _collision_safe_destination(
            archive_dir / csv_file.name
        )
        shutil.move(str(csv_file), str(destination))
        print(f"[ARCHIVE] {csv_file} -> {destination}")
        archived += 1

    print(f"[ARCHIVE] {engine_name}: {archived} ranking archiviati.")
    return archived


def archive_input_file(input_path: Path) -> Path:
    """
    Sposta il file di input in data/input_partite/oldmatches.

    Questa funzione deve essere chiamata soltanto dopo che tutti gli engine
    richiesti hanno completato correttamente l'elaborazione.
    """

    if not input_path.exists():
        raise FileNotFoundError(
            f"File input non più disponibile per l'archiviazione: {input_path}"
        )

    INPUT_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    destination = _collision_safe_destination(
        INPUT_ARCHIVE_DIR / input_path.name
    )

    shutil.move(str(input_path), str(destination))
    print(f"[ARCHIVE] Input: {input_path} -> {destination}")

    return destination

def rank_matches(input_file: str | Path, output_file: str | Path, engine_name: str = "v20") -> None:
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
        home = row["Home"].strip()
        away = row["Away"].strip()

        league_info = get_league_info(league_id)
        competition_group = get_competition_group(league_id, registry_rows)
        group_league_ids = get_group_league_ids(
            league_id, competition_group, registry_rows
        )
        histories = load_group_histories(group_league_ids)

        # Se non esiste ancora alcun file storico, la competizione è appena iniziata
        # oppure non sono stati ancora acquisiti risultati.
        #
        # In questa situazione la lega equivale ad avere zero partite concluse:
        # non deve interrompere l'elaborazione degli altri campionati, ma deve essere
        # semplicemente esclusa dal ranking fino al raggiungimento della soglia minima.
        if not histories:
            print(
                f"[SKIP] {league_id}: nessuno storico risultati disponibile "
                f"(0 partite concluse, minimo richiesto: 5)."
            )
            continue

        # Per le leghe ordinarie il controllo usa lo storico della singola lega.
        # Per play-in/playoff e CompetitionGroup usa gli storici divisionali
        # disponibili, perché la fase dedicata può non avere ancora un file proprio.
        readiness_matches = (
            [
                match
                for source_matches in histories.values()
                for match in source_matches
            ]
            if competition_group
            else histories.get(league_id, [])
        )

        completed_rounds = count_completed_rounds_before(
            readiness_matches,
            match_date_value,
        )

        if completed_rounds < MIN_COMPLETED_ROUNDS_PER_LEAGUE:
            print(
                f"[SKIP] {league_id}: solo {completed_rounds} turni conclusi "
                f"prima del {match_date_text}; minimo richiesto: "
                f"{MIN_COMPLETED_ROUNDS_PER_LEAGUE}."
            )
            continue

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
        # L'unione è sicura perché build_match_statistics filtra per squadra.
        statistics_matches = [
            match
            for source_matches in histories.values()
            for match in source_matches
        ]

        target_matches = histories.get(league_id, [])
        round_number = infer_next_round(target_matches)
        # Con storici interdivisionali deve includere tutte le gare precedenti.
        statistics_before_round = infer_next_round(statistics_matches)

        match_stats = build_match_statistics(
            matches=statistics_matches,
            home_team=home,
            away_team=away,
            before_round=statistics_before_round,
        )
        score = engine.calculate_score(match_stats, league_info)

        # ------------------------------------------------------------------
        # Driver contestuali opzionali dell'engine
        # ------------------------------------------------------------------
        # Gli engine precedenti non espongono apply_contextual_band e quindi
        # continuano a funzionare esattamente come prima.
        #
        # v26 usa invece il PPG delle due squadre prima della partita:
        #   - almeno 10 gare per entrambe;
        #   - gap PPG <= 0.30;
        #   - ALTA  -> PROX-ALTA
        #   - MEDIA -> PROX-MEDIA
        contextual_band = None

        apply_contextual_band = getattr(
            engine,
            "apply_contextual_band",
            None,
        )

        if callable(apply_contextual_band):
            (
                home_played,
                home_points,
                home_ppg,
            ) = calculate_team_ppg_before_match(
                team=home,
                source_league_id=home_source,
                histories=histories,
                match_date=match_date_value,
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
            )

            base_band = score_value(
                score,
                "band",
            )

            contextual_band = apply_contextual_band(
                base_band,
                home_played=home_played,
                away_played=away_played,
                home_ppg=home_ppg,
                away_ppg=away_ppg,
            )

            if contextual_band != base_band:
                print(
                    f"[{engine_name}][PROX] "
                    f"{home} - {away}: "
                    f"{base_band} -> {contextual_band} | "
                    f"GP={home_played}/{away_played} | "
                    f"PPG={home_ppg:.3f}/{away_ppg:.3f} | "
                    f"gap={abs(home_ppg - away_ppg):.3f}"
                )

        results.append(build_output_row(
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
        ))

    results.sort(key=lambda x: float(x["Score"] or 0), reverse=True)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter=";")
        writer.writeheader()
        writer.writerows(results)

    print(f"[{engine_name}] Ranking generato: {output_path.resolve()}")
    append_predictions(results, engine_name=engine_name, algorithm_version=algorithm_version)


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera ranking partite GioOver2.5 v2.0")
    parser.add_argument("input_file", help="CSV partite da analizzare")
    parser.add_argument(
        "--engine", default="v20", choices=get_available_engines() + ["all"],
        help="Motore di scoring da usare",
    )
    parser.add_argument("--output", default=None, help="CSV output ranking")
    args = parser.parse_args()
    input_path = Path(args.input_file)
    base_name = input_path.stem.replace("partite", "ranking")

    if args.engine == "all":
        engine_names = get_available_engines()

        # Prima di generare i nuovi ranking, archivia gli output precedenti
        # nella cartella old_ranking specifica di ciascun engine.
        for engine_name in engine_names:
            archive_output_rankings(engine_name)

        # Se uno degli engine solleva un errore, l'esecuzione si interrompe e
        # il file di input non viene archiviato.
        for engine_name in engine_names:
            output_file = OUTPUT_DIR / engine_name / f"{base_name}_{engine_name}.csv"
            rank_matches(args.input_file, output_file, engine_name)
    else:
        archive_output_rankings(args.engine)

        output_file = (
            Path(args.output)
            if args.output
            else OUTPUT_DIR / args.engine / f"{base_name}_{args.engine}.csv"
        )
        rank_matches(args.input_file, output_file, args.engine)

    # Questo punto viene raggiunto soltanto se tutti gli engine richiesti
    # hanno completato correttamente la generazione del ranking.
    archive_input_file(input_path)


if __name__ == "__main__":
    main()
