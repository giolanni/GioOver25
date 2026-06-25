import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MatchResult:
    country: str
    league: str
    season: int
    round: int
    date: str
    home: str
    away: str
    home_goals: int
    away_goals: int
    notes: str = ""

    @property
    def result(self) -> str:
        if self.home_goals > self.away_goals:
            return "H"
        if self.home_goals < self.away_goals:
            return "A"
        return "D"

    @property
    def total_goals(self) -> int:
        return self.home_goals + self.away_goals

    @property
    def over15(self) -> bool:
        return self.total_goals >= 2

    @property
    def over25(self) -> bool:
        return self.total_goals >= 3


def _int(value: str) -> int:
    value = (value or "").strip()
    return int(value) if value else 0


def read_results_file(path: str | Path) -> list[MatchResult]:
    results_path = Path(path)

    if not results_path.exists():
        raise FileNotFoundError(f"File risultati non trovato: {results_path}")

    matches: list[MatchResult] = []

    with open(results_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")

        required_columns = {
            "Country",
            "League",
            "Season",
            "Round",
            "Date",
            "Home",
            "Away",
            "HG",
            "AG",
            "Notes",
        }

        missing = required_columns - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                "File risultati non valido. Mancano le colonne: "
                + ", ".join(sorted(missing))
            )

        for row in reader:
            matches.append(
                MatchResult(
                    country=row["Country"].strip(),
                    league=row["League"].strip(),
                    season=_int(row["Season"]),
                    round=_int(row["Round"]),
                    date=row["Date"].strip(),
                    home=row["Home"].strip(),
                    away=row["Away"].strip(),
                    home_goals=_int(row["HG"]),
                    away_goals=_int(row["AG"]),
                    notes=row.get("Notes", "").strip(),
                )
            )

    return matches


def write_results_file(matches: list[MatchResult], path: str | Path) -> None:
    results_path = Path(path)
    results_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "Country",
        "League",
        "Season",
        "Round",
        "Date",
        "Home",
        "Away",
        "HG",
        "AG",
        "Notes",
    ]

    with open(results_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        for match in matches:
            writer.writerow(
                {
                    "Country": match.country,
                    "League": match.league,
                    "Season": match.season,
                    "Round": match.round,
                    "Date": match.date,
                    "Home": match.home,
                    "Away": match.away,
                    "HG": match.home_goals,
                    "AG": match.away_goals,
                    "Notes": match.notes,
                }
            )