from __future__ import annotations

import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ..models import XGMatch


BIGBALLS_LEAGUES = {
    "England_PremierLeague": "premier-league",
    "Spain_LaLiga": "la-liga",
    "Germany_Bundesliga": "bundesliga",
    "Italy_SerieA": "serie-a",
    "France_Ligue1": "ligue-1",
    "USA_MLS": "mls",
}


class BigBallsProvider:
    """Client REST minimale per Big Balls Sports Data.

    Richiede la variabile d'ambiente BBS_API_KEY. Il provider conserva il raw
    JSON così da poter adattare rapidamente il normalizzatore se lo schema del
    servizio cambia.
    """

    base_url = "https://api.bigballsdata.com"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("BBS_API_KEY", "")
        if not self.api_key:
            raise RuntimeError("BBS_API_KEY non configurata")

    def _get_json(self, path: str, params: dict[str, object] | None = None):
        query = f"?{urlencode(params)}" if params else ""
        req = Request(
            f"{self.base_url}{path}{query}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "User-Agent": "GioOver2.5-xG/1.0",
            },
        )
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    @staticmethod
    def _items(payload) -> list[dict]:
        if isinstance(payload, list):
            return payload
        if not isinstance(payload, dict):
            return []
        for key in ("data", "matches", "results", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
        return []

    @staticmethod
    def _nested(obj: dict, *paths, default=None):
        for path in paths:
            cur = obj
            ok = True
            for part in path.split("."):
                if not isinstance(cur, dict) or part not in cur:
                    ok = False
                    break
                cur = cur[part]
            if ok and cur not in (None, ""):
                return cur
        return default

    def list_matches(self, league_id: str) -> list[dict]:
        league = BIGBALLS_LEAGUES.get(league_id)
        if not league:
            raise ValueError(f"LeagueId non supportato da Big Balls: {league_id}")
        payload = self._get_json("/v1/matches", {"sport": "football", "league": league})
        return self._items(payload)

    def match_stats(self, match_id: str) -> dict:
        return self._get_json(f"/v1/stored/matches/{match_id}/stats")

    def download_league_matches(self, league_id: str) -> list[XGMatch]:
        """Scarica fixture e xG disponibili, saltando match senza xG.

        Big Balls dichiara esplicitamente che la copertura xG può essere
        parziale: l'assenza di xG non viene trasformata in zero.
        """
        output: list[XGMatch] = []
        for match in self.list_matches(league_id):
            match_id = str(self._nested(match, "id", "uuid", "match_id", default=""))
            if not match_id:
                continue
            try:
                stats = self.match_stats(match_id)
            except Exception:
                continue

            home_xg = self._nested(
                stats,
                "home.xg", "home.expected_goals", "stats.home.xg",
                "data.home.xg", "xg.home",
            )
            away_xg = self._nested(
                stats,
                "away.xg", "away.expected_goals", "stats.away.xg",
                "data.away.xg", "xg.away",
            )
            if home_xg in (None, "") or away_xg in (None, ""):
                continue

            score_home = self._nested(match, "score.home", "home_score")
            score_away = self._nested(match, "score.away", "away_score")
            output.append(
                XGMatch(
                    league_id=league_id,
                    match_date=str(self._nested(match, "date", "kickoff", "start_time", default=""))[:10],
                    home=str(self._nested(match, "home.name", "home_team.name", "home", default="")),
                    away=str(self._nested(match, "away.name", "away_team.name", "away", default="")),
                    home_xg=float(home_xg),
                    away_xg=float(away_xg),
                    source="bigballs",
                    source_match_id=match_id,
                    home_goals=int(score_home) if score_home not in (None, "") else None,
                    away_goals=int(score_away) if score_away not in (None, "") else None,
                    raw={"match": match, "stats": stats},
                )
            )
        return output
