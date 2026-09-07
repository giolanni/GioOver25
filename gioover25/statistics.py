from dataclasses import dataclass
from .history import MatchResult
from .team_names import normalize_team_name


@dataclass
class StatsSummary:
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    points: int = 0
    gf: int = 0
    ga: int = 0
    over15: int = 0
    over25: int = 0
    over35: int = 0
    btts: int = 0

    @property
    def gd(self) -> int:
        return self.gf - self.ga

    @property
    def gf_per_match(self) -> float:
        return self.gf / self.played if self.played else 0.0

    @property
    def ga_per_match(self) -> float:
        return self.ga / self.played if self.played else 0.0

    @property
    def over25_rate(self) -> float:
        return self.over25 / self.played if self.played else 0.0


def _match_team_key(match: MatchResult, team: object, league_id: str | None = None) -> str:
    effective_league = league_id or getattr(match, "league", "")
    return normalize_team_name(effective_league, team)


def summarize_team_matches(matches: list[MatchResult], team: str, league_id: str | None = None) -> StatsSummary:
    summary = StatsSummary()

    for match in matches:
        target_key = _match_team_key(match, team, league_id)
        home_key = _match_team_key(match, match.home, league_id)
        away_key = _match_team_key(match, match.away, league_id)
        is_home = home_key == target_key
        is_away = away_key == target_key

        if not is_home and not is_away:
            continue

        gf = match.home_goals if is_home else match.away_goals
        ga = match.away_goals if is_home else match.home_goals

        summary.played += 1
        summary.gf += gf
        summary.ga += ga

        if gf > ga:
            summary.wins += 1
            summary.points += 3
        elif gf < ga:
            summary.losses += 1
        else:
            summary.draws += 1
            summary.points += 1

        total_goals = gf + ga
        if total_goals >= 2:
            summary.over15 += 1
        if total_goals >= 3:
            summary.over25 += 1
        if total_goals >= 4:
            summary.over35 += 1
        if gf > 0 and ga > 0:
            summary.btts += 1

    return summary


def team_matches_before_round(matches: list[MatchResult], team: str, round_number: int, league_id: str | None = None) -> list[MatchResult]:
    return [
        match for match in matches
        if match.round < round_number
        and (
            _match_team_key(match, match.home, league_id) == _match_team_key(match, team, league_id)
            or _match_team_key(match, match.away, league_id) == _match_team_key(match, team, league_id)
        )
    ]


def last_matches(matches: list[MatchResult], team: str, n: int, league_id: str | None = None) -> list[MatchResult]:
    team_matches = team_matches_before_round(matches, team, 10**9, league_id=league_id)
    team_matches.sort(key=lambda m: (m.date, m.round))
    return team_matches[-n:]


def home_matches(matches: list[MatchResult], team: str, league_id: str | None = None) -> list[MatchResult]:
    return [
        match for match in matches
        if _match_team_key(match, match.home, league_id) == _match_team_key(match, team, league_id)
    ]


def away_matches(matches: list[MatchResult], team: str, league_id: str | None = None) -> list[MatchResult]:
    return [
        match for match in matches
        if _match_team_key(match, match.away, league_id) == _match_team_key(match, team, league_id)
    ]


def get_team_statistics(
    matches: list[MatchResult],
    team: str,
    before_round: int | None = None,
    last_n: int | None = None,
    venue: str | None = None,
    league_id: str | None = None,
) -> StatsSummary:
    filtered = matches

    if before_round is not None:
        filtered = [match for match in filtered if match.round < before_round]

    if venue == "home":
        filtered = home_matches(filtered, team, league_id=league_id)
    elif venue == "away":
        filtered = away_matches(filtered, team, league_id=league_id)
    else:
        filtered = [
            match for match in filtered
            if (
                _match_team_key(match, match.home, league_id) == _match_team_key(match, team, league_id)
                or _match_team_key(match, match.away, league_id) == _match_team_key(match, team, league_id)
            )
        ]

    filtered.sort(key=lambda m: (m.date, m.round))
    if last_n is not None:
        filtered = filtered[-last_n:]

    return summarize_team_matches(filtered, team, league_id=league_id)
