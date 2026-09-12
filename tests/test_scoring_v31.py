from types import SimpleNamespace

from gioover25.scoring_v30 import calculate_score_v30
from gioover25.scoring_v31 import calculate_score_v31


def _summary(*, played, gf_per_match, over25_rate):
    return SimpleNamespace(
        played=played,
        gf_per_match=gf_per_match,
        ga_per_match=1.5,
        over25_rate=over25_rate,
        over25=round(over25_rate * played),
        btts=0,
        points=0,
    )


def _team(*, played=7, gf_full=1.6, gf_l5=1.6, over_l5=0.8):
    return SimpleNamespace(
        overall=_summary(played=played, gf_per_match=gf_full, over25_rate=0.7),
        last5=_summary(played=5, gf_per_match=gf_l5, over25_rate=over_l5),
        last10=_summary(played=played, gf_per_match=gf_full, over25_rate=0.7),
        home=_summary(played=played, gf_per_match=gf_full, over25_rate=0.7),
        away=_summary(played=played, gf_per_match=gf_full, over25_rate=0.7),
        position=3,
        points=12,
        ppg=1.7,
    )


def _match_stats(**team_kwargs):
    return SimpleNamespace(
        home=_team(**team_kwargs),
        away=_team(**team_kwargs),
        position_gap=1,
        points_gap=1,
        ppg_gap=0.1,
    )


def _league_info():
    return SimpleNamespace(teams=14)


def test_v31_accepts_stable_high_scoring_signal_that_v30_rejects():
    stats = _match_stats(played=7, gf_full=1.6, gf_l5=1.6, over_l5=0.8)

    v30 = calculate_score_v30(stats, _league_info())
    v31 = calculate_score_v31(stats, _league_info())

    assert v30.band != "ALTA"
    assert v31.band == "ALTA"
    assert v31.score >= 80
    assert "V31 BASE" in v31.reason


def test_v31_delta20_boosts_floor():
    stats = _match_stats(played=7, gf_full=1.6, gf_l5=1.85, over_l5=0.8)
    result = calculate_score_v31(stats, _league_info())

    assert result.band == "ALTA"
    assert result.score >= 85
    assert "V31 BOOST" in result.reason


def test_v31_delta30_is_strong():
    stats = _match_stats(played=7, gf_full=1.6, gf_l5=1.95, over_l5=0.8)
    result = calculate_score_v31(stats, _league_info())

    assert result.band == "ALTA"
    assert result.score >= 90
    assert "V31 STRONG" in result.reason
