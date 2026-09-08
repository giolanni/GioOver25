from analysis.laboratory import build_laboratory
from gioover25 import append_results


def test_incremental_enrichment_reuses_drivers_and_updates_outcome(monkeypatch):
    existing = [{
        "PredictionDate": "2026-09-01",
        "MatchDate": "2026-09-02",
        "LeagueId": "Test_League",
        "Round": "1",
        "Home": "Home",
        "Away": "Away",
        "Score": "91",
        "Band": "ALTA",
        "AlgorithmVersion": "v25",
        "Outcome": "",
        "HomePPGLast5": "1.8",
    }]
    refreshed = [{
        **existing[0],
        "Outcome": "OK",
        "HG": "2",
        "AG": "1",
    }]

    monkeypatch.setattr(
        build_laboratory,
        "enrich_matches_with_recent_form",
        lambda rows: (_ for _ in ()).throw(
            AssertionError("nessuna nuova riga da calcolare")
        ),
    )

    rows, reused, calculated = build_laboratory.enrich_incrementally(
        refreshed,
        existing,
    )

    assert reused == 1
    assert calculated == 0
    assert rows[0]["Outcome"] == "OK"
    assert rows[0]["HomePPGLast5"] == "1.8"


def test_incremental_enrichment_calculates_only_new_rows(monkeypatch):
    old = {
        "LeagueId": "Test_League",
        "MatchDate": "2026-09-02",
        "Home": "Old Home",
        "Away": "Old Away",
        "HomePPGLast5": "1.2",
    }
    new = {
        "LeagueId": "Test_League",
        "MatchDate": "2026-09-03",
        "Home": "New Home",
        "Away": "New Away",
    }

    def fake_enrich(rows):
        assert rows == [new]
        return [{**new, "HomePPGLast5": "2.0"}]

    monkeypatch.setattr(
        build_laboratory,
        "enrich_matches_with_recent_form",
        fake_enrich,
    )

    rows, reused, calculated = build_laboratory.enrich_incrementally(
        [old, new],
        [old],
    )

    assert reused == 1
    assert calculated == 1
    assert [row["HomePPGLast5"] for row in rows] == ["1.2", "2.0"]


def test_routine_post_update_skips_heavy_analyses(monkeypatch):
    commands = []

    class Result:
        returncode = 0

    monkeypatch.setattr(
        append_results.subprocess,
        "run",
        lambda command, check: commands.append(command) or Result(),
    )

    append_results._run_post_update_tasks()

    modules = [
        command[command.index("-m") + 1]
        for command in commands
    ]
    assert modules == [
        "analysis.laboratory.build_laboratory",
        "analysis.metrics.build_engine_league_high_rankings",
    ]
    assert "--incremental" in commands[0]


def test_full_post_update_includes_metrics(monkeypatch):
    commands = []

    class Result:
        returncode = 0

    monkeypatch.setattr(
        append_results.subprocess,
        "run",
        lambda command, check: commands.append(command) or Result(),
    )

    append_results._run_post_update_tasks(full_analysis=True)

    modules = [
        command[command.index("-m") + 1]
        for command in commands
    ]
    assert modules == [
        "analysis.laboratory.run_all",
        "analysis.metrics.analyze_metrics",
        "analysis.metrics.build_engine_league_high_rankings",
    ]


def test_incremental_output_does_not_write_drivers(monkeypatch, tmp_path):
    matches_file = tmp_path / "01_matches.csv"
    calls = []

    monkeypatch.setattr(build_laboratory, "OUTPUT", tmp_path)
    monkeypatch.setattr(build_laboratory, "MATCHES_FILE", matches_file)
    monkeypatch.setattr(
        build_laboratory,
        "write_matches",
        lambda rows, path: calls.append(("matches", path)),
    )
    monkeypatch.setattr(
        build_laboratory,
        "write_drivers",
        lambda rows, path: calls.append(("drivers", path)),
    )

    build_laboratory.write_laboratory_outputs(
        [{"MatchId": 1}],
        incremental=True,
    )

    assert calls == [("matches", matches_file)]


def test_full_output_writes_matches_and_drivers(monkeypatch, tmp_path):
    matches_file = tmp_path / "01_matches.csv"
    calls = []

    monkeypatch.setattr(build_laboratory, "OUTPUT", tmp_path)
    monkeypatch.setattr(build_laboratory, "MATCHES_FILE", matches_file)
    monkeypatch.setattr(
        build_laboratory,
        "write_matches",
        lambda rows, path: calls.append(("matches", path)),
    )
    monkeypatch.setattr(
        build_laboratory,
        "write_drivers",
        lambda rows, path: calls.append(("drivers", path)),
    )

    build_laboratory.write_laboratory_outputs(
        [{"MatchId": 1}],
        incremental=False,
    )

    assert calls == [
        ("matches", matches_file),
        ("drivers", tmp_path / "02_drivers.csv"),
    ]
