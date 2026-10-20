from gioover25.engines import v27
from gioover25.engines.factory import get_available_engines, get_engine
from gioover25.scoring_v21dev import ScoreV21DevResult


def _base(home_attack: float) -> ScoreV21DevResult:
    return ScoreV21DevResult(
        score=70.0,
        band="MEDIA",
        reason="base",
        ranking_gap_score=0.0,
        home_attack_score=home_attack,
        away_attack_score=0.0,
        home_defense_weakness_score=0.0,
        away_defense_weakness_score=0.0,
        home_last10_over_score=0.0,
        away_last10_over_score=0.0,
        home_venue_over_score=0.0,
        away_venue_over_score=0.0,
        btts_profile_score=0.0,
    )


def test_v27_selects_exact_frozen_thresholds(monkeypatch):
    monkeypatch.setattr(v27.v26, "calculate_score", lambda *_: _base(12.428))

    result = v27.calculate_score(
        object(),
        object(),
        away_ga_last5=2.20,
    )

    assert result.band == "ALTA"
    assert "V27_OVER25_ATTACK_AWAYGA" in result.reason


def test_v27_rejects_below_home_attack_threshold(monkeypatch):
    monkeypatch.setattr(v27.v26, "calculate_score", lambda *_: _base(12.427))

    result = v27.calculate_score(
        object(),
        object(),
        away_ga_last5=2.20,
    )

    assert result.band == "BASSA"


def test_v27_rejects_below_away_ga_threshold(monkeypatch):
    monkeypatch.setattr(v27.v26, "calculate_score", lambda *_: _base(12.428))

    result = v27.calculate_score(
        object(),
        object(),
        away_ga_last5=2.19,
    )

    assert result.band == "BASSA"


def test_v27_rejects_missing_recent_away_ga(monkeypatch):
    monkeypatch.setattr(v27.v26, "calculate_score", lambda *_: _base(13.0))

    result = v27.calculate_score(
        object(),
        object(),
        away_ga_last5=None,
    )

    assert result.band == "BASSA"


def test_v27_is_available_through_factory():
    assert "v27" in get_available_engines()
    assert get_engine("v27") is v27
