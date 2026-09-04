from gioover25 import ranking_history


def _row(match_date: str, *, status: str = "SCHEDULED", hg: str = "", ag: str = "") -> dict:
    return {
        "PredictionDate": "2026-08-21",
        "MatchDate": match_date,
        "LeagueId": "Bulgaria_ParvaLiga",
        "Round": "6",
        "Home": "Slavia Sofia",
        "Away": "Septemvri Sofia",
        "Score": "70.0",
        "Band": "MEDIA",
        "MatchStatus": status,
        "HG": hg,
        "AG": ag,
        "Goals": "2" if hg and ag else "",
        "Over25": "KO" if hg and ag else "",
        "BTTS": "OK" if hg and ag else "",
    }


def test_append_predictions_skips_same_fixture_with_match_date_less_than_3_days(monkeypatch):
    existing = _row("2026-08-28", status="FINAL", hg="1", ag="1")
    written = {}

    monkeypatch.setattr(ranking_history, "_read_history", lambda engine_name: [existing])
    monkeypatch.setattr(
        ranking_history,
        "_write_history",
        lambda engine_name, rows: written.update(engine=engine_name, rows=rows),
    )

    ranking_history.append_predictions(
        [_row("2026-08-30")],
        engine_name="v25",
        algorithm_version="2.5",
    )

    assert written["engine"] == "v25"
    assert len(written["rows"]) == 1
    assert written["rows"][0]["MatchDate"] == "2026-08-28"
    assert written["rows"][0]["MatchStatus"] == "FINAL"
    assert written["rows"][0]["HG"] == "1"
    assert written["rows"][0]["AG"] == "1"


def test_append_predictions_allows_same_fixture_at_3_days_distance(monkeypatch):
    existing = _row("2026-08-28", status="FINAL", hg="1", ag="1")
    written = {}

    monkeypatch.setattr(ranking_history, "_read_history", lambda engine_name: [existing])
    monkeypatch.setattr(
        ranking_history,
        "_write_history",
        lambda engine_name, rows: written.update(engine=engine_name, rows=rows),
    )

    ranking_history.append_predictions(
        [_row("2026-08-31")],
        engine_name="v25",
        algorithm_version="2.5",
    )

    assert len(written["rows"]) == 2
    assert written["rows"][1]["MatchDate"] == "2026-08-31"
    assert written["rows"][1]["MatchStatus"] == "SCHEDULED"
    assert written["rows"][1]["HG"] == ""
    assert written["rows"][1]["AG"] == ""
