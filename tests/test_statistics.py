from gioover25.history import read_results_file
from gioover25.statistics import get_team_statistics


def test_team_statistics_asker():
    matches = read_results_file(
        "data/storico/risultati/Norway_3rdDivision_Group1_2026.csv"
    )

    stats = get_team_statistics(matches, "Asker")

    assert stats.played == 11
    assert stats.wins == 9
    assert stats.draws == 1
    assert stats.losses == 1
    assert stats.points == 28
    assert stats.gf == 37
    assert stats.ga == 11


def test_team_last_5_statistics():
    matches = read_results_file(
        "data/storico/risultati/Norway_3rdDivision_Group1_2026.csv"
    )

    stats = get_team_statistics(matches, "Asker", last_n=5)

    assert stats.played == 5
    print(stats)


def test_home_statistics():
    matches = read_results_file(
        "data/storico/risultati/Norway_3rdDivision_Group1_2026.csv"
    )

    stats = get_team_statistics(matches, "Asker", venue="home")

    assert stats.played > 0
    print(stats)