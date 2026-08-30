from gioover25.xg.build_features import build_point_in_time_features
from gioover25.xg.summarize_xg import summarize


def sample_rows():
    return [
        {'LeagueId':'Italy_SerieA','MatchDate':'2026-08-01','Home':'A','Away':'B','HomeXG':'1.50','AwayXG':'0.50','Source':'test'},
        {'LeagueId':'Italy_SerieA','MatchDate':'2026-08-08','Home':'B','Away':'A','HomeXG':'1.00','AwayXG':'2.00','Source':'test'},
    ]


def test_summary_team_averages():
    rows = summarize(sample_rows(), last_n=5)
    by_team = {row['Team']: row for row in rows}
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


def test_same_day_is_blocked_from_leakage():
    rows = [
        {'LeagueId':'Italy_SerieA','MatchDate':'2026-08-01','Home':'A','Away':'B','HomeXG':'1.0','AwayXG':'1.0','Source':'test'},
        {'LeagueId':'Italy_SerieA','MatchDate':'2026-08-01','Home':'A','Away':'C','HomeXG':'3.0','AwayXG':'0.5','Source':'test'},
    ]
    features = build_point_in_time_features(rows)
    assert features[0]['HomeXGPlayed'] == 0
    assert features[1]['HomeXGPlayed'] == 0
