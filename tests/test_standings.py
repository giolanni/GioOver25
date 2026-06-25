from gioover25.history import read_results_file
from gioover25.standings import (
    calculate_standings_after_round,
    calculate_all_round_standings,
)


def test_calculate_standings_after_round():
    path = "data/storico/risultati/Norway_3rdDivision_Group1_2026.csv"
    matches = read_results_file(path)

    standings = calculate_standings_after_round(matches, 1)

    assert len(standings) > 0

    first = standings[0]

    assert first.team != ""
    assert first.played > 0
    assert first.points >= 0
    assert first.gf >= 0
    assert first.ga >= 0


def test_calculate_all_round_standings():
    path = "data/storico/risultati/Norway_3rdDivision_Group1_2026.csv"
    matches = read_results_file(path)

    rows = calculate_all_round_standings(matches)

    assert len(rows) > 0

    first = rows[0]

    assert "Round" in first
    assert "Position" in first
    assert "Team" in first
    assert "Points" in first
    assert "PPG" in first


def test_print_round_1_standings():
    path = "data/storico/risultati/Norway_3rdDivision_Group1_2026.csv"
    matches = read_results_file(path)

    standings = calculate_standings_after_round(matches, 1)

    for position, row in enumerate(standings, start=1):
        print(
            f"{position}. {row.team} "
            f"{row.played}G {row.points}pt "
            f"GF {row.gf} GA {row.ga} GD {row.gd} PPG {row.ppg:.3f}"
        )