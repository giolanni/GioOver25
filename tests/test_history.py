from gioover25.history import read_results_file


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