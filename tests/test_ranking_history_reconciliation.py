from gioover25.history import MatchResult
from gioover25 import ranking_history


def _prediction(match_date="2026-08-21", status="SCHEDULED"):
    return {
        "PredictionDate": "2026-08-20",
        "MatchDate": match_date,
        "LeagueId": "Austria_Oberosterreich",
        "Round": "4",
        "Home": "Edelweiss",
        "Away": "Perg",
        "MatchStatus": status,
        "HG": "",
        "AG": "",
        "Goals": "",
        "Over25": "",
        "BTTS": "",
    }


def _result(match_date="2026-08-25"):
    return MatchResult(
        country="Austria",
        league="Oberosterreich",
        round=4,
        date=match_date,
        home="Edelweiss",
        away="Perg",
        home_goals=2,
        away_goals=1,
    )


def test_unique_fixture_can_recover_shifted_date(monkeypatch, tmp_path):
    history = [_prediction()]
    written = {}

    monkeypatch.setattr(ranking_history, "_read_history", lambda engine: history)
    monkeypatch.setattr(
        ranking_history,
        "_write_history",
        lambda engine, rows: written.setdefault("rows", rows),
    )
    monkeypatch.setattr(ranking_history, "DEBUG_DIR", tmp_path)

    ranking_history.update_finished_matches(
        "v20",
        [("Austria_Oberosterreich", _result())],
    )

    row = written["rows"][0]
    assert row["MatchDate"] == "2026-08-25"
    assert row["HG"] == "2"
    assert row["AG"] == "1"
    assert row["Over25"] == "OK"
    assert row["MatchStatus"] == "FINAL"


def test_shifted_date_is_not_forced_when_fixture_is_ambiguous(monkeypatch, tmp_path):
    history = [
        _prediction("2026-08-21"),
        _prediction("2026-08-22"),
    ]
    written = {}

    monkeypatch.setattr(ranking_history, "_read_history", lambda engine: history)
    monkeypatch.setattr(
        ranking_history,
        "_write_history",
        lambda engine, rows: written.setdefault("rows", rows),
    )
    monkeypatch.setattr(ranking_history, "DEBUG_DIR", tmp_path)

    ranking_history.update_finished_matches(
        "v20",
        [("Austria_Oberosterreich", _result("2026-08-25"))],
        match_date_tolerance_days=2,
    )

    assert all(row["HG"] == "" for row in written["rows"])
    assert all(row["MatchStatus"] == "SCHEDULED" for row in written["rows"])
