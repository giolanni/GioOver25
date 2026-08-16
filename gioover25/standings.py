import csv
from dataclasses import dataclass
from pathlib import Path

from .history import MatchResult, read_results_file


@dataclass
class TeamStanding:
    team: str
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    gf: int = 0
    ga: int = 0
    points: int = 0

    @property
    def gd(self) -> int:
        return self.gf - self.ga

    @property
    def ppg(self) -> float:
        return self.points / self.played if self.played else 0.0


def _ensure_team(table: dict[str, TeamStanding], team: str) -> TeamStanding:
    if team not in table:
        table[team] = TeamStanding(team=team)
    return table[team]


def calculate_standings_after_round(
    matches: list[MatchResult],
    round_number: int,
    included_teams: set[str] | None = None,
) -> list[TeamStanding]:
    """
    Calcola la classifica dopo il round indicato.

    Comportamento standard
    ----------------------
    Se ``included_teams`` non viene specificato, il comportamento resta
    identico a quello storico: tutte le squadre presenti nelle partite
    contribuiscono alla classifica.

    Classifiche divisionali con gare inter-divisione
    ------------------------------------------------
    Se ``included_teams`` contiene un insieme di squadre, vengono mostrate e
    classificate soltanto quelle squadre, MA valgono comunque anche le partite
    disputate contro avversarie esterne all'insieme.

    Questo è necessario, ad esempio, per MLS Next Pro: una squadra appartiene
    a una divisione ma può giocare partite valide per la propria classifica
    contro squadre di altre divisioni.

    Esempio:
        included_teams = {"Toronto FC 2", "Columbus Crew 2", ...}

    Una partita Toronto FC 2 - Chattanooga viene quindi conteggiata per
    Toronto, senza inserire Chattanooga nella classifica Northeast.
    """

    table: dict[str, TeamStanding] = {}

    filtered_matches = [m for m in matches if m.round <= round_number]

    for match in filtered_matches:
        include_home = (
            included_teams is None
            or match.home in included_teams
        )
        include_away = (
            included_teams is None
            or match.away in included_teams
        )

        # Se nessuna delle due squadre appartiene alla classifica richiesta,
        # la partita non ha alcun effetto su questa classifica.
        if not include_home and not include_away:
            continue

        home = (
            _ensure_team(table, match.home)
            if include_home
            else None
        )
        away = (
            _ensure_team(table, match.away)
            if include_away
            else None
        )

        # Statistiche della squadra di casa, se inclusa nella classifica.
        if home is not None:
            home.played += 1
            home.gf += match.home_goals
            home.ga += match.away_goals

            if match.home_goals > match.away_goals:
                home.wins += 1
                home.points += 3
            elif match.home_goals < match.away_goals:
                home.losses += 1
            else:
                home.draws += 1
                home.points += 1

        # Statistiche della squadra ospite, se inclusa nella classifica.
        if away is not None:
            away.played += 1
            away.gf += match.away_goals
            away.ga += match.home_goals

            if match.away_goals > match.home_goals:
                away.wins += 1
                away.points += 3
            elif match.away_goals < match.home_goals:
                away.losses += 1
            else:
                away.draws += 1
                away.points += 1

    standings = list(table.values())

    standings.sort(
        key=lambda x: (
            -x.points,
            -x.gd,
            -x.gf,
            x.team
        )
    )

    return standings


def calculate_all_round_standings(matches: list[MatchResult]) -> list[dict]:
    if not matches:
        return []

    max_round = max(match.round for match in matches)
    rows: list[dict] = []

    for round_number in range(1, max_round + 1):
        standings = calculate_standings_after_round(matches, round_number)

        for position, standing in enumerate(standings, start=1):
            rows.append(
                {
                    "Round": round_number,
                    "Position": position,
                    "Team": standing.team,
                    "Played": standing.played,
                    "Wins": standing.wins,
                    "Draws": standing.draws,
                    "Losses": standing.losses,
                    "GF": standing.gf,
                    "GA": standing.ga,
                    "GD": standing.gd,
                    "Points": standing.points,
                    "PPG": round(standing.ppg, 3),
                }
            )

    return rows


def write_standings_csv(rows: list[dict], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "Round",
        "Position",
        "Team",
        "Played",
        "Wins",
        "Draws",
        "Losses",
        "GF",
        "GA",
        "GD",
        "Points",
        "PPG",
    ]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def generate_standings_file(
    results_file: str | Path,
    output_file: str | Path
) -> None:
    matches = read_results_file(results_file)
    rows = calculate_all_round_standings(matches)
    write_standings_csv(rows, output_file)


def calculate_current_standings(matches: list[MatchResult]) -> list[dict]:
    if not matches:
        return []

    max_round = max(match.round for match in matches)

    standings = calculate_standings_after_round(matches, max_round)

    rows = []

    for position, standing in enumerate(standings, start=1):
        rows.append(
            {
                "Round": max_round,
                "Position": position,
                "Team": standing.team,
                "Played": standing.played,
                "Wins": standing.wins,
                "Draws": standing.draws,
                "Losses": standing.losses,
                "GF": standing.gf,
                "GA": standing.ga,
                "GD": standing.gd,
                "Points": standing.points,
                "PPG": round(standing.ppg, 3),
            }
        )

    return rows


def generate_current_standings_file(results_file: Path, output_file: Path) -> None:
    matches = read_results_file(results_file)
    rows = calculate_current_standings(matches)
    write_standings_csv(rows, output_file)
