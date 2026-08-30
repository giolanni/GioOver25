from __future__ import annotations

import html
import json
import re
from urllib.request import Request, urlopen

from ..models import XGMatch


UNDERSTAT_LEAGUES = {
    "England_PremierLeague": "EPL",
    "Spain_LaLiga": "La_liga",
    "Germany_Bundesliga": "Bundesliga",
    "Italy_SerieA": "Serie_A",
    "France_Ligue1": "Ligue_1",
    "Russia_PremierLeague": "RFPL",
}


class UnderstatProvider:
    """Downloader leggero per i JSON incorporati nelle pagine Understat.

    Understat non pubblica una API ufficiale: il provider legge esclusivamente
    dati pubblici presenti nelle pagine league/match e li normalizza.
    """

    base_url = "https://understat.com"

    @staticmethod
    def _get(url: str) -> str:
        req = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 GioOver2.5-xG/1.0",
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        with urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace")

    @staticmethod
    def _extract_json(page: str, variable: str):
        # Formato normalmente usato da Understat:
        # var datesData = JSON.parse('...');
        patterns = [
            rf"var\s+{re.escape(variable)}\s*=\s*JSON\.parse\('(.+?)'\)",
            rf"{re.escape(variable)}\s*=\s*JSON\.parse\('(.+?)'\)",
        ]
        for pattern in patterns:
            match = re.search(pattern, page, flags=re.S)
            if not match:
                continue
            encoded = html.unescape(match.group(1))
            # Il payload è una stringa JS escaped. Decodifica prima gli escape
            # unicode/slash, poi il JSON reale.
            decoded = bytes(encoded, "utf-8").decode("unicode_escape")
            return json.loads(decoded)
        raise ValueError(f"Payload Understat non trovato: {variable}")

    def download_league_matches(self, league_id: str, season_start_year: int) -> list[XGMatch]:
        code = UNDERSTAT_LEAGUES.get(league_id)
        if not code:
            raise ValueError(f"LeagueId non supportato da Understat: {league_id}")

        page = self._get(f"{self.base_url}/league/{code}/{int(season_start_year)}")
        rows = self._extract_json(page, "datesData")
        output: list[XGMatch] = []

        for row in rows:
            xg = row.get("xG") or {}
            home_xg = xg.get("h")
            away_xg = xg.get("a")
            if home_xg in (None, "") or away_xg in (None, ""):
                continue

            home = (row.get("h") or {}).get("title", "")
            away = (row.get("a") or {}).get("title", "")
            goals = row.get("goals") or {}
            output.append(
                XGMatch(
                    league_id=league_id,
                    match_date=str(row.get("datetime") or "")[:10],
                    home=home,
                    away=away,
                    home_xg=float(home_xg),
                    away_xg=float(away_xg),
                    source="understat",
                    source_match_id=str(row.get("id") or ""),
                    home_goals=int(goals["h"]) if goals.get("h") not in (None, "") else None,
                    away_goals=int(goals["a"]) if goals.get("a") not in (None, "") else None,
                    raw=row,
                )
            )
        return output

    def download_match_shots(self, match_id: str) -> dict:
        """Restituisce lo shot-level xG grezzo di una singola partita."""
        page = self._get(f"{self.base_url}/match/{match_id}")
        return self._extract_json(page, "shotsData")
