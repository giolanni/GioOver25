from gioover25.history import read_results_file
from gioover25.match_statistics import build_match_statistics


def test_build_match_statistics():
    matches = read_results_file(
        "data/storico/risultati/Norway_3rdDivision_Group1_2026.csv"
    )

    stats = build_match_statistics(
        matches=matches,
        home_team="Gamle Oslo",
        away_team="Lokomotiv Oslo",
        before_round=12,
    )

    assert stats.home.team == "Gamle Oslo"
    assert stats.away.team == "Lokomotiv Oslo"

    assert stats.home.position > 0
    assert stats.away.position > 0

    assert stats.position_gap >= 0
    assert stats.points_gap >= 0
    assert stats.ppg_gap >= 0

    print(stats)