from datetime import date
from types import SimpleNamespace

from gioover25.rank_matches_v2 import (
    build_output_row,
    calculate_team_ppg_before_match,
    find_team_source_league,
    read_matches_to_rank,
)
from gioover25.team_names import get_team_id, normalize_team_name


def test_ranking_input_and_output_use_canonical_team_name(tmp_path):
    input_file = tmp_path / "matches.csv"
    input_file.write_text(
        "LeagueId;MatchDate;Home;Away\n"
        "Finland_Kolmonen_Southern_Group2;2026-09-07;VJS/Akatemia;Toukolan Teräs\n",
        encoding="utf-8",
    )

    row = read_matches_to_rank(input_file)[0]
    assert row["Home"] == "VJS 2"
    assert row["Away"] == "ToTe"

    output = build_output_row(
        prediction_date="2026-09-07",
        match_date=row["MatchDate"],
        algorithm_version="test",
        league_id=row["LeagueId"],
        round_number=20,
        home="VJS/Akatemia",
        away=row["Away"],
        home_source_league_id=row["LeagueId"],
        away_source_league_id=row["LeagueId"],
        competition_group="",
        score=None,
    )

    assert output["Home"] == "VJS 2"
    assert output["Away"] == "ToTe"


def test_find_team_source_uses_league_specific_aliases():
    league_id = "Finland_Kolmonen_Eastern_Group3"
    histories = {
        league_id: [
            SimpleNamespace(
                date="2026-09-03",
                home="Kultsu",
                away="KoPa",
            )
        ]
    }

    assert find_team_source_league(
        "Kultsu FC",
        histories,
        date(2026, 9, 8),
    ) == league_id


def test_machine_safe_team_ids_are_used_for_identity():
    western = "Finland_Kolmonen_Western_Group2"
    southern = "Finland_Kolmonen_Southern_Group2"

    assert get_team_id(western, "Ylöjärvi Utd.") == "FIN_YLOJARVI_UTD"
    assert get_team_id(western, "Ylojarvi United FC") == "FIN_YLOJARVI_UTD"
    assert normalize_team_name(western, "Ylöjärvi Utd.") == "FIN_YLOJARVI_UTD"

    assert get_team_id(southern, "PPS") == "FIN_PPS"
    assert get_team_id(southern, "Pakkalan Palloseura") == "FIN_PPS"
    assert normalize_team_name(southern, "PPS") == normalize_team_name(
        southern, "Pakkalan Palloseura"
    )


def test_avshar_ararat_inherits_araks_history_before_match_date():
    league_id = "Armenia_FirstLeague"
    histories = {
        league_id: [
            *[
                SimpleNamespace(
                    date=f"2026-09-{day:02d}",
                    home="Araks Ararat",
                    away=f"Opponent {day}",
                    home_goals=1,
                    away_goals=0,
                )
                for day in range(1, 10)
            ],
            SimpleNamespace(
                date="2026-11-02",
                home="Avshar Ararat",
                away="Urartu 2",
                home_goals=4,
                away_goals=1,
            ),
            SimpleNamespace(
                date="2026-11-09",
                home="Bentonit",
                away="Avshar Ararat",
                home_goals=0,
                away_goals=0,
            ),
        ]
    }

    played, points, ppg = calculate_team_ppg_before_match(
        team="Avshar Ararat",
        source_league_id=league_id,
        histories=histories,
        match_date=date(2026, 11, 9),
    )

    assert normalize_team_name(league_id, "Avshar Ararat") == normalize_team_name(
        league_id, "Araks Ararat"
    )
    assert (played, points, ppg) == (10, 30, 3.0)
