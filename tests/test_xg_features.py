from gioover25.xg.build_features import build_point_in_time_features
from gioover25.xg.summarize_xg import summarize


def sample_rows():
    return [
        {
            'LeagueId': 'Italy_SerieA', 'Season': '2026', 'MatchDate': '2026-08-01',
            'Home': 'A', 'Away': 'B', 'HomeXG': '1.50', 'AwayXG': '0.50',
            'HomeGoals': '2', 'AwayGoals': '1', 'Source': 'test',
        },
        {
            'LeagueId': 'Italy_SerieA', 'Season': '2026', 'MatchDate': '2026-08-08',
            'Home': 'B', 'Away': 'A', 'HomeXG': '1.00', 'AwayXG': '2.00',
            'HomeGoals': '0', 'AwayGoals': '1', 'Source': 'test',
        },
    ]


def test_summary_team_averages():
    rows = summarize(sample_rows(), last_n=5)
    by_team = {row['Team']: row for row in rows}
    assert by_team['A']['Season'] == '2026'
    assert by_team['A']['XGPlayed'] == 2
    assert by_team['A']['XGFAvg'] == 1.75
    assert by_team['A']['XGAAvg'] == 0.75


def test_point_in_time_does_not_see_future_match():
    features = build_point_in_time_features(sample_rows())
    assert features[0]['HomeXGPlayed'] == 0
    assert features[0]['AwayXGPlayed'] == 0
    assert features[1]['HomeXGPlayed'] == 1
    assert features[1]['AwayXGPlayed'] == 1
    assert features[1]['ProjectedTotalXG'] != ''
    assert features[0]['Over25'] == 1
    assert features[1]['Over25'] == 0


def test_same_day_is_blocked_from_leakage():
    rows = [
        {
            'LeagueId': 'Italy_SerieA', 'Season': '2026', 'MatchDate': '2026-08-01',
            'Home': 'A', 'Away': 'B', 'HomeXG': '1.0', 'AwayXG': '1.0', 'Source': 'test',
        },
        {
            'LeagueId': 'Italy_SerieA', 'Season': '2026', 'MatchDate': '2026-08-01',
            'Home': 'A', 'Away': 'C', 'HomeXG': '3.0', 'AwayXG': '0.5', 'Source': 'test',
        },
    ]
    features = build_point_in_time_features(rows)
    assert features[0]['HomeXGPlayed'] == 0
    assert features[1]['HomeXGPlayed'] == 0


def test_new_season_resets_all_team_history():
    rows = [
        {
            'LeagueId': 'Italy_SerieA', 'Season': '2025', 'MatchDate': '2025-08-20',
            'Home': 'A', 'Away': 'B', 'HomeXG': '2.0', 'AwayXG': '1.0', 'Source': 'test',
        },
        {
            'LeagueId': 'Italy_SerieA', 'Season': '2026', 'MatchDate': '2026-08-20',
            'Home': 'A', 'Away': 'B', 'HomeXG': '3.0', 'AwayXG': '2.0', 'Source': 'test',
        },
    ]
    features = build_point_in_time_features(rows)
    assert features[0]['Season'] == '2025'
    assert features[1]['Season'] == '2026'
    assert features[1]['HomeXGPlayed'] == 0
    assert features[1]['AwayXGPlayed'] == 0
    assert features[1]['ProjectedTotalXG'] == ''


def test_summary_does_not_mix_seasons():
    rows = [
        {
            'LeagueId': 'Italy_SerieA', 'Season': '2025', 'MatchDate': '2025-08-20',
            'Home': 'A', 'Away': 'B', 'HomeXG': '2.0', 'AwayXG': '1.0', 'Source': 'test',
        },
        {
            'LeagueId': 'Italy_SerieA', 'Season': '2026', 'MatchDate': '2026-08-20',
            'Home': 'A', 'Away': 'B', 'HomeXG': '4.0', 'AwayXG': '3.0', 'Source': 'test',
        },
    ]
    summary = summarize(rows)
    a_rows = [row for row in summary if row['Team'] == 'A']
    assert len(a_rows) == 2
    assert {row['Season'] for row in a_rows} == {'2025', '2026'}
    assert {row['XGPlayed'] for row in a_rows} == {1}
