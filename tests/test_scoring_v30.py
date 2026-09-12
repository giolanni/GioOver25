from types import SimpleNamespace

import gioover25.scoring_v30 as v30
from gioover25.scoring_v21dev import ScoreV21DevResult


def _summary(*, played, gf_per_match, over25_rate):
    gf = round(gf_per_match * played)
    over25 = round(over25_rate * played)
    return SimpleNamespace(
        played=played,
        gf=gf,
        ga=0,
        over25=over25,
        gf_per_match=gf_per_match,
        over25_rate=over25_rate,
    )


def _team(*, played, full_gf, l5_gf, l5_over):
    return SimpleNamespace(
        overall=_summary(
            played=played,
            gf_per_match=full_gf,
            over25_rate=0.5,
        ),
        last5=_summary(
            played=5,
            gf_per_match=l5_gf,
            over25_rate=l5_over,
        ),
    )


def _base(score=82.0):
    return ScoreV21DevResult(
        score=score,
        band="ALTA",
        reason="base",
        ranking_gap_score=0.0,
        home_attack_score=0.0,
        away_attack_score=0.0,
        home_defense_weakness_score=0.0,
        away_defense_weakness_score=0.0,
        home_last10_over_score=0.0,
        away_last10_over_score=0.0,
        home_venue_over_score=0.0,
        away_venue_over_score=0.0,
        btts_profile_score=0.0,
    )


def test_v30_caps_non_target_high_score(monkeypatch):
    monkeypatch.setattr(v30, "calculate_score_v25", lambda *_: _base(88.0))
    stats = SimpleNamespace(
        home=_team(played=9, full_gf=1.5, l5_gf=1.8, l5_over=0.8),
        away=_team(played=9, full_gf=1.5, l5_gf=1.8, l5_over=0.8),
    )

    result = v30.calculate_score_v30(stats, SimpleNamespace())

    assert result.score == 74.99
    assert result.band == "MEDIA"
    assert "V30 NO-SIGNAL" in result.reason


def test_v30_core_signal_becomes_alta(monkeypatch):
    monkeypatch.setattr(v30, "calculate_score_v25", lambda *_: _base(68.0))
    stats = SimpleNamespace(
        home=_team(played=7, full_gf=1.5, l5_gf=1.75, l5_over=0.8),
        away=_team(played=8, full_gf=1.5, l5_gf=1.75, l5_over=0.8),
    )

    result = v30.calculate_score_v30(stats, SimpleNamespace())

    assert result.score == 80.0
    assert result.band == "ALTA"
    assert "V30 CORE" in result.reason


def test_v30_strong_signal_gets_90_floor(monkeypatch):
    monkeypatch.setattr(v30, "calculate_score_v25", lambda *_: _base(72.0))
    stats = SimpleNamespace(
        home=_team(played=7, full_gf=1.4, l5_gf=1.8, l5_over=0.8),
        away=_team(played=8, full_gf=1.4, l5_gf=1.8, l5_over=0.8),
    )

    result = v30.calculate_score_v30(stats, SimpleNamespace())

    assert result.score == 90.0
    assert result.band == "ALTA"
    assert "V30 STRONG" in result.reason
