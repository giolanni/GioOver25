from gioover25 import ranking_history


def _row(
    match_date: str,
    *,
    round_value: str = "6",
    status: str = "SCHEDULED",
    hg: str = "",
    ag: str = "",
) -> dict:
    return {
        "PredictionDate": "2026-08-21",
        "MatchDate": match_date,
        "LeagueId": "Bulgaria_ParvaLiga",
        "Round": round_value,
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


def test_append_predictions_corrects_match_date_within_two_days(monkeypatch):
    existing = _row("2026-08-28")
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
    assert written["rows"][0]["MatchDate"] == "2026-08-30"
    assert written["rows"][0]["MatchStatus"] == "SCHEDULED"


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


def test_append_predictions_allows_third_home_away_fixture_later_in_season(monkeypatch):
    first = _row("2026-03-10", round_value="4", status="FINAL", hg="2", ag="1")
    second = _row("2026-06-15", round_value="13", status="FINAL", hg="1", ag="0")
    written = {}

    monkeypatch.setattr(
        ranking_history,
        "_read_history",
        lambda engine_name: [first, second],
    )
    monkeypatch.setattr(
        ranking_history,
        "_write_history",
        lambda engine_name, rows: written.update(engine=engine_name, rows=rows),
    )

    ranking_history.append_predictions(
        [_row("2026-09-20", round_value="22")],
        engine_name="v25",
        algorithm_version="2.5",
    )

    assert len(written["rows"]) == 3
    assert written["rows"][2]["MatchDate"] == "2026-09-20"
    assert written["rows"][2]["Round"] == "22"
    assert written["rows"][2]["MatchStatus"] == "SCHEDULED"
