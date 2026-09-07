from gioover25.rank_matches_v2 import build_output_row, read_matches_to_rank


def test_ranking_input_and_output_use_canonical_team_name(tmp_path):
    input_file = tmp_path / "matches.csv"
    input_file.write_text(
        "LeagueId;MatchDate;Home;Away\n"
        "Finland_Kolmonen_Southern_Group2;2026-09-07;VJS/Akatemia;Toukolan Teräs\n",
        encoding="utf-8",
    )

    row = read_matches_to_rank(input_file)[0]
    assert row["Home"] == "VJS 2"
    assert row["Away"] == "ToTe"

    output = build_output_row(
        prediction_date="2026-09-07",
        match_date=row["MatchDate"],
        algorithm_version="test",
        league_id=row["LeagueId"],
        round_number=20,
        home="VJS/Akatemia",
        away=row["Away"],
        home_source_league_id=row["LeagueId"],
        away_source_league_id=row["LeagueId"],
        competition_group="",
        score=None,
    )

    assert output["Home"] == "VJS 2"
    assert output["Away"] == "ToTe"
