import csv

from gioover25 import normalize_team_names


def _read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def test_cleanup_roots_cover_all_persisted_team_name_datasets():
    roots = {str(path).replace("\\", "/") for path in normalize_team_names.ROOTS}

    assert "data/storico/risultati" in roots
    assert "data/storico/classifiche_calcolate" in roots
    assert "data/storico/ranking" in roots
    assert "data/storico/ranking-risultati" in roots
    assert "data/output_ranking" in roots


def test_dry_run_reports_without_modifying_file(tmp_path):
    path = tmp_path / "ranking.csv"
    original = (
        "LeagueId;Home;Away\n"
        "Finland_Kolmonen_Southern_Group2;VJS/Akatemia;Toukolan Teräs\n"
    )
    path.write_text(original, encoding="utf-8")

    changes = normalize_team_names._process_file(path, apply=False)

    assert path.read_text(encoding="utf-8") == original
    assert [(item["Old"], item["New"]) for item in changes] == [
        ("VJS/Akatemia", "VJS 2"),
        ("Toukolan Teräs", "ToTe"),
    ]


def test_apply_rewrites_file_and_creates_backup(tmp_path):
    path = tmp_path / "ranking.csv"
    path.write_text(
        "LeagueId;Home;Away\n"
        "Finland_Kolmonen_Southern_Group2;VJS/2;Toukolan Teräs\n",
        encoding="utf-8",
    )
    backup_root = tmp_path / "backup"

    normalize_team_names._process_file(
        path,
        apply=True,
        backup_root=backup_root,
    )

    row = _read_rows(path)[0]
    assert row["Home"] == "VJS 2"
    assert row["Away"] == "ToTe"
    assert (backup_root / tmp_path.name / "ranking.csv").exists()


def test_results_filename_supplies_league_id(tmp_path):
    results_dir = tmp_path / "risultati"
    results_dir.mkdir()
    path = results_dir / "Finland_Kolmonen_Southern_Group2.csv"
    path.write_text(
        "Home;Away\nVJS/2;Toukolan Teräs\n",
        encoding="utf-8",
    )

    changes = normalize_team_names._process_file(path, apply=False)

    assert {item["LeagueId"] for item in changes} == {
        "Finland_Kolmonen_Southern_Group2"
    }


def test_standings_filename_supplies_league_id(tmp_path):
    standings_dir = tmp_path / "classifiche_calcolate"
    standings_dir.mkdir()
    path = standings_dir / "Finland_Kolmonen_Southern_Group2.csv"
    path.write_text(
        "Team;Played\nVJS/Akatemia;10\nToukolan Teräs;10\n",
        encoding="utf-8",
    )

    changes = normalize_team_names._process_file(path, apply=False)

    assert [(item["Old"], item["New"]) for item in changes] == [
        ("VJS/Akatemia", "VJS 2"),
        ("Toukolan Teräs", "ToTe"),
    ]


def test_regenerate_standings_merges_aliases_and_backs_up(tmp_path, monkeypatch):
    league_id = "Finland_Kolmonen_Southern_Group2"
    results_dir = tmp_path / "risultati"
    standings_dir = tmp_path / "classifiche_calcolate"
    results_dir.mkdir()
    standings_dir.mkdir()

    results_file = results_dir / f"{league_id}.csv"
    results_file.write_text(
        "Country;League;Round;MatchDate;Home;Away;HG;AG;Notes\n"
        "Finland;Kolmonen;1;2026-01-01;VJS/2;A;1;0;\n"
        "Finland;Kolmonen;2;2026-01-02;B;VJS/Akatemia;0;2;\n",
        encoding="utf-8",
    )
    standings_file = standings_dir / f"{league_id}.csv"
    standings_file.write_text("vecchia classifica\n", encoding="utf-8")

    monkeypatch.setattr(normalize_team_names, "RESULTS_DIR", results_dir)
    monkeypatch.setattr(normalize_team_names, "STANDINGS_DIR", standings_dir)
    backup_root = tmp_path / "backup"

    regenerated = normalize_team_names._regenerate_standings(
        {league_id},
        backup_root=backup_root,
    )

    vjs = next(row for row in _read_rows(standings_file) if row["Team"] == "VJS 2")
    assert regenerated == 1
    assert vjs["Played"] == "2"
    assert (
        backup_root / "classifiche_calcolate" / standings_file.name
    ).exists()


def test_eastern_group1_standings_merge_aliases_but_keep_sapa_clubs_distinct(
    tmp_path, monkeypatch
):
    league_id = "Finland_Kolmonen_Eastern_Group1"
    results_dir = tmp_path / "risultati"
    standings_dir = tmp_path / "classifiche_calcolate"
    results_dir.mkdir()
    standings_dir.mkdir()

    results_file = results_dir / f"{league_id}.csv"
    results_file.write_text(
        "Country;League;Round;MatchDate;Home;Away;HG;AG;Notes\n"
        "Finland;Kolmonen;1;2026-01-01;SAPA;SaPa;2;1;\n"
        "Finland;Kolmonen;2;2026-01-02;JJK/2;FC Vaajakoski/2;1;0;\n"
        "Finland;Kolmonen;3;2026-01-03;JJK Jyvaskyla 2;FC Vaajakoski 2;2;2;\n"
        "Finland;Kolmonen;4;2026-01-04;Komeetat;Jyväskylän Komeetat;3;1;\n",
        encoding="utf-8",
    )
    standings_file = standings_dir / f"{league_id}.csv"

    monkeypatch.setattr(normalize_team_names, "RESULTS_DIR", results_dir)
    monkeypatch.setattr(normalize_team_names, "STANDINGS_DIR", standings_dir)
    normalize_team_names._regenerate_standings(
        {league_id},
        backup_root=tmp_path / "backup",
    )

    rows = {row["Team"]: row for row in _read_rows(standings_file)}
    assert set(rows) == {
        "SAPA",
        "Savon Pallo",
        "JJK/2",
        "FC Vaajakoski/2",
        "Komeetat",
    }
    assert rows["SAPA"]["Played"] == "1"
    assert rows["Savon Pallo"]["Played"] == "1"
    assert rows["JJK/2"]["Played"] == "2"
    assert rows["FC Vaajakoski/2"]["Played"] == "2"
    assert rows["Komeetat"]["Played"] == "2"
