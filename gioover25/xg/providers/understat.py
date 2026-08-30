from __future__ import annotations

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
    """Downloader xG per gli endpoint AJAX di Understat.

    Replica il comportamento usato dall'attuale progetto ``understatAPI``:
    sessione ``requests`` persistente e header ``X-Requested-With`` per le
    chiamate ``getLeagueData`` / ``getMatchData``.
    """

    base_url = "https://understat.com/"

    def __init__(self) -> None:
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError(
                "Il provider Understat richiede il pacchetto 'requests'. "
                "Installa con: python -m pip install requests"
            ) from exc

        self._requests = requests
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://understat.com/",
            }
        )

    def _get_json(self, endpoint: str) -> dict:
        url = self.base_url + endpoint.lstrip("/")
        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        # Evitiamo l'errore criptico "Expecting value: line 1 column 1" e
        # mostriamo cosa ha realmente risposto Understat se non arriva JSON.
        try:
            data = response.json()
        except ValueError as exc:
            preview = (response.text or "").strip().replace("\n", " ")[:250]
            content_type = response.headers.get("Content-Type", "")
            raise RuntimeError(
                "Understat non ha restituito JSON "
                f"(HTTP {response.status_code}, Content-Type={content_type!r}, "
                f"body={preview!r})"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(f"Risposta Understat inattesa da {url}: {type(data).__name__}")
        return data

    def download_league_matches(self, league_id: str, season_start_year: int) -> list[XGMatch]:
        code = UNDERSTAT_LEAGUES.get(league_id)
        if not code:
            raise ValueError(f"LeagueId non supportato da Understat: {league_id}")

        payload = self._get_json(f"getLeagueData/{code}/{int(season_start_year)}")
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
                # Fixture future: gli xG reali non esistono ancora.
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
        payload = self._get_json(f"getMatchData/{match_id}")
        shots = payload.get("shots", {})
        if not isinstance(shots, dict):
            raise ValueError(f"Payload Understat shots inatteso per match {match_id}")
        return shots
