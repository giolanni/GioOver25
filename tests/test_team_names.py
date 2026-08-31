import pytest

from gioover25.team_names import canonicalize_team_display_name, normalize_team_name


@pytest.mark.parametrize(
    ("league_id", "ranking_name", "result_name"),
    [
        ("Australia_NSWLeagueOne", "Canterbury Bankstown FC", "Canterbury Bankstown"),
        ("Australia_NSWLeagueOne", "Newcastle Jets Youth", "Newcastle Jets U23"),
        ("Australia_NSWLeagueOne", "Northbridge FC Bulls", "Bulls Academy"),
        ("Estonia_Esiliiga", "Tartu JK Welco", "Tartu Welco"),
        ("Germany_Oberliga_Bayern_Sud", "TSV Kottern", "Kottern-St. Mang"),
        ("Germany_Oberliga_Bayern_Sud", "TSV Schwabmuenchen", "Schwabmunchen"),
        ("Germany_Oberliga_Hessen", "FC Giessen", "Giessen"),
        ("Germany_Oberliga_SchleswigHolstein", "Holstein Kiel 2", "Kiel 2"),
        ("Germany_Regionalliga_Bayern", "SC Eltersdorf", "Eltersdorf"),
        ("Germany_Regionalliga_Bayern", "DJK Vilzing", "Vilzing"),
        ("Germany_Regionalliga_Bayern", "FC Memmingen", "Memmingen"),
        ("Germany_Regionalliga_Nord", "SC Weiche Flensburg", "SC Weiche-08"),
        ("Germany_Regionalliga_Nord", "SV Drochtersen/Assel", "Drochtersen/Assel"),
        ("Germany_Regionalliga_Nordost", "RW Erfurt", "Erfurt"),
        ("Germany_Regionalliga_Nordost", "FSV Zwickau", "Zwickau"),
        ("Hungary_NBII", "Kecskemeti TE", "Kecskemeti"),
        ("Hungary_NBII", "Mezokovesd SE", "Mezokovesd"),
        ("Iceland_Division_2", "Kormakur/Hvoet", "Kormakur/Hvot"),
        ("Iceland_Division_2", "UMF Selfoss", "Selfoss"),
        ("Iceland_Division_2", "Vikingur Olafsvik", "Olafsvik"),
        ("Norway_2ndDivision_Group1", "Mjoendalen", "Mjøndalen"),
        ("Norway_2ndDivision_Group2", "Kjelsaas", "Kjelsås"),
        ("Norway_3rdDivision_Group1", "Vaalerenga IF 2", "Vålerenga IF 2"),
        ("Norway_3rdDivision_Group1", "Baerum", "Bærum"),
        ("Norway_3rdDivision_Group3", "Foerde", "Førde"),
        ("Norway_3rdDivision_Group5", "Floeya", "Fløya"),
        ("Norway_3rdDivision_Group5", "Skjervoey", "Skjervøy"),
    ],
)
def test_verified_aliases_resolve_to_same_team(league_id, ranking_name, result_name):
    assert normalize_team_name(league_id, ranking_name) == normalize_team_name(
        league_id, result_name
    )


def test_aliases_are_scoped_to_league():
    assert normalize_team_name("Other_League", "FC Giessen") != normalize_team_name(
        "Other_League", "Giessen"
    )


def test_reserve_suffix_ii_is_still_canonicalized_to_2():
    assert canonicalize_team_display_name("Holstein Kiel II") == "Holstein Kiel 2"
