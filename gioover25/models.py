from dataclasses import dataclass


@dataclass
class TeamStats:
    name: str
    position: int
    goals_for: int
    goals_against: int
    played: int
    last10_over25: int
    last10_goals_for: int
    last10_goals_against: int

    @property
    def gf_per_match(self) -> float:
        return self.goals_for / self.played if self.played else 0.0

    @property
    def ga_per_match(self) -> float:
        return self.goals_against / self.played if self.played else 0.0

    @property
    def last10_gf_per_match(self) -> float:
        return self.last10_goals_for / 10.0

    @property
    def last10_ga_per_match(self) -> float:
        return self.last10_goals_against / 10.0

    @property
    def last10_over_rate(self) -> float:
        return self.last10_over25 / 10.0


@dataclass
class MatchInput:
    home: TeamStats
    away: TeamStats
