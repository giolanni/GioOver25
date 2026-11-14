"""Sanity checks for the nine Serie D group names and registry rows."""
from gioover25.serie_d_registry import SERIE_D_GROUPS, league_id_for_title, validate_registry


def test_nine_distinct_groups():
    assert len(SERIE_D_GROUPS) == 9
    assert len({v.league_id for v in SERIE_D_GROUPS.values()}) == 9


def test_group_resolution():
    assert league_id_for_title("Serie D - Girone A") == "Italy_SerieD_GironeA"
    assert league_id_for_title("ITALIA: Serie D - Girone I") == "Italy_SerieD_GironeI"
    assert league_id_for_title("Serie D") is None
    assert league_id_for_title("Serie C Girone A") is None


def test_registered():
    assert validate_registry("data/league_registry.csv") == []
