from gioover25.registry import load_league_registry


def test_load_registry():
    registry = load_league_registry()

    assert len(registry) > 0

    league = registry["Norway_3rdDivision_Group1_2026"]

    assert league.country == "Norway"
    assert league.teams == 14