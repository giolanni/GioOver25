from __future__ import annotations

import json
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
    """Downloader xG per gli endpoint AJAX pubblicamente accessibili di Understat.

    Da gennaio 2026 Understat carica i dati principali tramite endpoint JSON
    dinamici (es. ``getLeagueData/Serie_A/2026``), quindi non e' piu' affidabile
    cercare ``datesData`` incorporato nell'HTML della pagina della lega.
    """

    base_url = "https://understat.com"

    @staticmethod
    def _get_json(url: str) -> dict:
        req = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 GioOver2.5-xG/1.0",
                "Accept": "application/json,text/plain,*/*",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        with urlopen(req, timeout=30) as response:
            payload = response.read().decode("utf-8", errors="replace")
        data = json.loads(payload)
        if not isinstance(data, dict):
            raise ValueError(f"Risposta Understat inattesa da {url}")
        return data

    def download_league_matches(self, league_id: str, season_start_year: int) -> list[XGMatch]:
        code = UNDERSTAT_LEAGUES.get(league_id)
        if not code:
            raise ValueError(f"LeagueId non supportato da Understat: {league_id}")

        url = f"{self.base_url}/getLeagueData/{code}/{int(season_start_year)}"
        payload = self._get_json(url)
        rows = payload.get("dates", [])
        if not isinstance(rows, list):
            raise ValueError("Payload Understat senza lista 'dates'")

        output: list[XGMatch] = []
        for row in rows:
            if not isinstance(row, dict):
                continue

            xg = row.get("xG") or {}
            home_xg = xg.get("h")
            away_xg = xg.get("a")
            if home_xg in (None, "") or away_xg in (None, ""):
                # Fixture future: Understat non dispone ancora degli xG reali.
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
        payload = self._get_json(f"{self.base_url}/getMatchData/{match_id}")
        shots = payload.get("shots", {})
        if not isinstance(shots, dict):
            raise ValueError(f"Payload Understat shots inatteso per match {match_id}")
        return shots
