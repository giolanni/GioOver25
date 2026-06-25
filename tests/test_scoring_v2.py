from gioover25.history import read_results_file
from gioover25.match_statistics import build_match_statistics
from gioover25.registry import get_league_info
from gioover25.scoring_v2 import calculate_score_v2


def test_scoring_v2():
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

    result = calculate_score_v2(match_stats, league_info)

    assert result.score >= 0
    assert result.score <= 100

    print(result)