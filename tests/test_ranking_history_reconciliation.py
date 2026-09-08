import pytest

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


def test_read_history_rejects_a_data_row_used_as_header(monkeypatch, tmp_path):
    history_file = tmp_path / "storico_ranking_v20.csv"
    history_file.write_text(
        "2026-09-05;2026-09-05;Finland_Kakkonen_GroupC;21;GBK;JBK\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        ranking_history,
        "_history_file",
        lambda engine_name: history_file,
    )

    with pytest.raises(ValueError, match="intestazione non valida"):
        ranking_history._read_history("v20")


def test_read_history_rejects_rows_lost_by_a_previous_bad_parse(
    monkeypatch, tmp_path
):
    history_file = tmp_path / "storico_ranking_v20.csv"
    fieldnames = ";".join(ranking_history.BASE_FIELDNAMES)
    empty_row = ";".join("" for _ in ranking_history.BASE_FIELDNAMES)
    history_file.write_text(
        f"{fieldnames}\n{empty_row}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        ranking_history,
        "_history_file",
        lambda engine_name: history_file,
    )

    with pytest.raises(ValueError, match="riga 2 non valida"):
        ranking_history._read_history("v20")


def test_read_history_rejects_git_conflict_markers(monkeypatch, tmp_path):
    history_file = tmp_path / "storico_ranking_v20.csv"
    fieldnames = ";".join(ranking_history.BASE_FIELDNAMES)
    values = {name: "" for name in ranking_history.BASE_FIELDNAMES}
    values.update(
        {
            "PredictionDate": "<<<<<<< Updated upstream",
            "LeagueId": "Test_League",
            "Home": "Home",
            "Away": "Away",
        }
    )
    conflict_row = ";".join(values[name] for name in ranking_history.BASE_FIELDNAMES)
    history_file.write_text(
        f"{fieldnames}\n{conflict_row}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        ranking_history,
        "_history_file",
        lambda engine_name: history_file,
    )

    with pytest.raises(ValueError, match="PredictionDate non valida"):
        ranking_history._read_history("v20")


def test_append_predictions_preserves_existing_history(monkeypatch, tmp_path):
    history_file = tmp_path / "storico_ranking_v20.csv"
    monkeypatch.setattr(
        ranking_history,
        "_history_file",
        lambda engine_name: history_file,
    )

    existing = _prediction("2026-08-21")
    ranking_history._write_history("v20", [existing])

    new_prediction = _prediction("2026-09-05")
    new_prediction["Home"] = "LASK"
    new_prediction["Away"] = "Rapid Vienna"
    ranking_history.append_predictions(
        [new_prediction],
        engine_name="v20",
        algorithm_version="2.0.0",
    )

    rows = ranking_history._read_history("v20")
    assert len(rows) == 2
    assert rows[0]["Home"] == "Edelweiss"
    assert rows[1]["Home"] == "LASK"


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
