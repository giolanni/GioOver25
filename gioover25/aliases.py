import csv
from pathlib import Path


ALIASES_FILE = Path("data/league_aliases.csv")


def load_aliases() -> dict[tuple[str, str, str], str]:
    """
    Restituisce un dizionario:

    (Source, CountryAlias, LeagueAlias) -> LeagueId
    """

    if not ALIASES_FILE.exists():
        raise FileNotFoundError(ALIASES_FILE)

    aliases = {}

    with open(ALIASES_FILE, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")

        for row in reader:
            key = (
                row["Source"].strip().lower(),
                row["CountryAlias"].strip().lower(),
                row["LeagueAlias"].strip().lower(),
            )

            aliases[key] = row["LeagueId"].strip()

    return aliases


def get_league_id(source: str, country: str, league: str) -> str:
    aliases = load_aliases()

    key = (
        source.strip().lower(),
        country.strip().lower(),
        league.strip().lower(),
    )

    if key not in aliases:
        raise ValueError(
            f"Nessun alias trovato per:\n"
            f"Source={source}\n"
            f"Country={country}\n"
            f"League={league}"
        )

    return aliases[key]