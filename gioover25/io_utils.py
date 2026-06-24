import csv
from pathlib import Path
from .models import MatchInput, TeamStats


def _int(row: dict, key: str) -> int:
    value = row.get(key, "")
    if value is None or str(value).strip() == "":
        return 0
    return int(str(value).strip())


def read_matches_from_csv(path: str | Path) -> list[MatchInput]:
    matches: list[MatchInput] = []

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")

        for row in reader:
            home = TeamStats(
                name=row["Home"].strip(),
                position=_int(row, "PosHome"),
                goals_for=_int(row, "GFHome"),
                goals_against=_int(row, "GSHome"),
                played=_int(row, "MatchHome"),
                last10_over25=_int(row, "WinHome"),
                last10_goals_for=_int(row, "GFH10"),
                last10_goals_against=_int(row, "GSH10"),
            )

            away = TeamStats(
                name=row["Away"].strip(),
                position=_int(row, "PosAway"),
                goals_for=_int(row, "GFAway"),
                goals_against=_int(row, "GSAway"),
                played=_int(row, "MatchAway"),
                last10_over25=_int(row, "WinAway"),
                last10_goals_for=_int(row, "GFA10"),
                last10_goals_against=_int(row, "GSA10"),
            )

            matches.append(
            MatchInput(
                country=row["country"].strip(),
                league=row["league"].strip(),
                teams_league=_int(row, "TeamsLeague"),
                home=home,
                away=away,
                )
            )
            
    return matches


def write_results_to_csv(results: list[dict], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    if not results:
        return

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(results[0].keys()),
            delimiter=";"
        )
        writer.writeheader()
        writer.writerows(results)