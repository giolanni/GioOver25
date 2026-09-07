import pytest

from gioover25.team_names import (
    canonicalize_team_display_name,
    get_real_team_name,
    normalize_team_name,
)


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
        ("Norway_2ndDivision_Group1", "Mjoendalen", "Mjondalen"),
        ("Norway_2ndDivision_Group2", "Kjelsaas", "Kjelsås"),
        ("Norway_3rdDivision_Group1", "Vaalerenga IF 2", "Vålerenga IF 2"),
        ("Norway_3rdDivision_Group1", "Vaalerenga IF 2", "Vålerenga 2"),
        ("Norway_3rdDivision_Group1", "Baerum", "Bærum"),
        ("Norway_3rdDivision_Group1", "Baerum", "Baerum Sportsklubb"),
        ("Norway_3rdDivision_Group3", "Foerde", "Førde"),
        ("Norway_3rdDivision_Group5", "Floeya", "Fløya"),
        ("Norway_3rdDivision_Group5", "Floeya", "Floya"),
        ("Norway_3rdDivision_Group5", "Skjervoey", "Skjervøy"),
        ("USA_USLChampionship", "Birmingham Legion", "Birmingham"),
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


@pytest.mark.parametrize(
    "source_name",
    ["VJS/Akatemia", "VJS/2", "VJS Vantaa B", "VJS Akatemia", "VJS 2"],
)
def test_vjs_aliases_share_one_canonical_display_name(source_name):
    assert canonicalize_team_display_name(
        source_name,
        "Finland_Kolmonen_Southern_Group2",
    ) == "VJS 2"


def test_real_name_is_available_from_dictionary():
    assert get_real_team_name(
        "Finland_Kolmonen_Southern_Group2",
        "VJS/2",
    ) == "VJS/Akatemia"


@pytest.mark.parametrize("source_name", ["PeKa", "FC Peli-Karhut", "Peli-Karhut"])
def test_peka_aliases_share_one_canonical_display_name(source_name):
    assert canonicalize_team_display_name(
        source_name,
        "Finland_Kolmonen_Eastern_Group3",
    ) == "PeKa"


@pytest.mark.parametrize(
    "source_name",
    ["Hercules-j", "Hercules 2", "Hercules II", "JS Hercules II", "Hercules-J"],
)
def test_hercules_reserve_aliases_share_one_canonical_display_name(source_name):
    assert canonicalize_team_display_name(
        source_name,
        "Finland_Kolmonen_North",
    ) == "Hercules-j"


@pytest.mark.parametrize("source_name", ["TPV/2", "TPV 2", "TPV II"])
def test_tpv_reserve_aliases_share_one_canonical_display_name(source_name):
    assert canonicalize_team_display_name(
        source_name,
        "Finland_Kolmonen_Western_Group2",
    ) == "TPV/2"


@pytest.mark.parametrize("source_name", ["RoPS", "Rovaniemi", "Rovaniemen Palloseura"])
def test_rops_aliases_share_one_canonical_display_name(source_name):
    assert canonicalize_team_display_name(source_name, "Finland_Ykkonen") == "RoPS"
