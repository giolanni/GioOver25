from gioover25.history import read_results_file


def test_read_results_uses_league_team_dictionary(tmp_path):
    results_file = tmp_path / "Finland_Kolmonen_Southern_Group2.csv"
    results_file.write_text(
        "Country;League;Round;MatchDate;Home;Away;HG;AG;Notes\n"
        "Finland;Kolmonen Southern Group 2;1;2026-04-23;Atlantis 2;VJS/2;3;6;\n",
        encoding="utf-8",
    )

    matches = read_results_file(results_file)

    assert matches[0].away == "VJS 2"


def test_read_results_file():
    path = "data/storico/risultati/Norway_3rdDivision_Group1_2026.csv"

    matches = read_results_file(path)

    assert len(matches) > 0

    first = matches[0]

    assert first.country == "Norway"
    assert first.season == 2026
    assert first.round > 0
    assert first.home != ""
    assert first.away != ""
    assert isinstance(first.home_goals, int)
    assert isinstance(first.away_goals, int)
    assert first.result in {"H", "D", "A"}


def test_first_five_matches_print():
    path = "data/storico/risultati/Norway_3rdDivision_Group1_2026.csv"

    matches = read_results_file(path)

    for match in matches[:5]:
        print(
            f"{match.date} - Round {match.round}: "
            f"{match.home} {match.home_goals}-{match.away_goals} {match.away} "
            f"({match.result})"
        )
