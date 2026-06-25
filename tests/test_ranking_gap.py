from gioover25.history import read_results_file
from gioover25.match_statistics import build_match_statistics
from gioover25.ranking_gap import calculate_ranking_gap
from gioover25.registry import get_league_info


def test_ranking_gap():
    league_id = "Norway_3rdDivision_Group1_2026"

    matches = read_results_file(
        f"data/storico/risultati/{league_id}.csv"
    )

    match_stats = build_match_statistics(
        matches=matches,
        home_team="Gamle Oslo",
        away_team="Lokomotiv Oslo",
        before_round=12,
    )

    league_info = get_league_info(league_id)

    gap = calculate_ranking_gap(match_stats, league_info)

    assert gap.score >= 0
    assert gap.score <= 1

    print(gap)