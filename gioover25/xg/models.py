from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class XGMatch:
    league_id: str
    match_date: str
    home: str
    away: str
    home_xg: float
    away_xg: float
    source: str
    source_match_id: str = ""
    home_goals: int | None = None
    away_goals: int | None = None
    raw: dict[str, Any] | None = None

    def to_csv_row(self) -> dict[str, object]:
        row = asdict(self)
        row.pop("raw", None)
        return {
            "LeagueId": row["league_id"],
            "MatchDate": row["match_date"],
            "Home": row["home"],
            "Away": row["away"],
            "HomeXG": row["home_xg"],
            "AwayXG": row["away_xg"],
            "HomeGoals": "" if row["home_goals"] is None else row["home_goals"],
            "AwayGoals": "" if row["away_goals"] is None else row["away_goals"],
            "Source": row["source"],
            "SourceMatchId": row["source_match_id"],
        }
