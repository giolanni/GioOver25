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
from datetime import date
from pathlib import Path

from .history import read_results_file
from .match_statistics import build_match_statistics
from .registry import get_league_info
from .ranking_history import append_predictions
from .engines.factory import get_engine, get_available_engines


INPUT_REQUIRED_COLUMNS = {"LeagueId", "MatchDate", "Home", "Away"}
RESULTS_DIR = Path("data/storico/risultati")
OUTPUT_DIR = Path("data/output_ranking")
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
) -> str:
    normalized = _normalize_team(team)
    candidates = []
    for league_id, matches in histories.items():
        team_dates = []
        for match in matches:
            if normalized not in {
                _normalize_team(getattr(match, "home", "")),
                _normalize_team(getattr(match, "away", "")),
            }:
                continue
            current_date = _match_date(match)
            if current_date is None:
                continue
            if match_date is not None and current_date >= match_date:
                continue
            team_dates.append(current_date)
        if team_dates:
            candidates.append((max(team_dates), league_id))
    if not candidates:
        raise ValueError(
            f"Squadra non trovata negli storici del CompetitionGroup: {team}"
        )
    candidates.sort(reverse=True)
    return candidates[0][1]


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
) -> dict:
    return {
    "MatchDate": match_date,
    "LeagueId": league_id,
    "Home": home,
    "Away": away,
    "Score": score_value(score, "score"),
    "Band": score_value(score, "band"),
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
        if not histories:
            raise FileNotFoundError(
                f"Nessuno storico risultati disponibile per {league_id}"
            )

        home_source = find_team_source_league(home, histories, match_date_value)
        away_source = find_team_source_league(away, histories, match_date_value)

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
        for engine_name in get_available_engines():
            output_file = OUTPUT_DIR / engine_name / f"{base_name}_{engine_name}.csv"
            rank_matches(args.input_file, output_file, engine_name)
    else:
        output_file = (
            Path(args.output)
            if args.output
            else OUTPUT_DIR / args.engine / f"{base_name}_{args.engine}.csv"
        )
        rank_matches(args.input_file, output_file, args.engine)


if __name__ == "__main__":
    main()
