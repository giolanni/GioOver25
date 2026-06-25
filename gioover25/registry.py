import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LeagueInfo:
    league_id: str
    country: str
    league: str
    season: int
    teams: int
    expected_rounds: int
    home_away: bool
    notes: str = ""


def _bool(value: str) -> bool:
    return str(value).strip().lower() in {"yes", "true", "1", "y", "sì", "si"}


def load_league_registry(path: str | Path = "data/league_registry.csv") -> dict[str, LeagueInfo]:
    registry_path = Path(path)

    if not registry_path.exists():
        raise FileNotFoundError(f"File league_registry non trovato: {registry_path}")

    leagues: dict[str, LeagueInfo] = {}

    with open(registry_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")

        required_columns = {
            "LeagueId",
            "Country",
            "League",
            "Season",
            "Teams",
            "ExpectedRounds",
            "HomeAway",
            "Notes",
        }

        missing = required_columns - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                "league_registry.csv non valido. Mancano le colonne: "
                + ", ".join(sorted(missing))
            )

        for row in reader:
            league = LeagueInfo(
                league_id=row["LeagueId"].strip(),
                country=row["Country"].strip(),
                league=row["League"].strip(),
                season=int(row["Season"]),
                teams=int(row["Teams"]),
                expected_rounds=int(row["ExpectedRounds"]),
                home_away=_bool(row["HomeAway"]),
                notes=row.get("Notes", "").strip(),
            )

            leagues[league.league_id] = league

    return leagues


def get_league_info(
    league_id: str,
    path: str | Path = "data/league_registry.csv"
) -> LeagueInfo:
    registry = load_league_registry(path)

    if league_id not in registry:
        raise KeyError(f"Lega non trovata nel registry: {league_id}")

    return registry[league_id]