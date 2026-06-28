import csv
from pathlib import Path

from gioover25.history import MatchResult, write_results_file
from gioover25.league_over_map import (
    calculate_league_over_row,
    rebuild_league_over_map,
)


def read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def test_calculate_league_over_row():
    matches = [
        MatchResult("Norway", "3rd Division Group 1", 2026, 1, "2026-06-01", "A", "B", 2, 1, ""),
        MatchResult("Norway", "3rd Division Group 1", 2026, 2, "2026-06-08", "C", "D", 1, 0, ""),
        MatchResult("Norway", "3rd Division Group 1", 2026, 3, "2026-06-15", "E", "F", 3, 3, ""),
        MatchResult("Norway", "3rd Division Group 1", 2026, 4, "2026-06-22", "G", "H", 0, 0, ""),
    ]

    row = calculate_league_over_row("Norway_3rdDivision_Group1_2026", matches)

    assert row["LeagueId"] == "Norway_3rdDivision_Group1_2026"
    assert row["Matches"] == 4

    assert row["Over15"] == 2
    assert row["Over15Pct"] == 50.0

    assert row["Over25"] == 2
    assert row["Over25Pct"] == 50.0

    assert row["Over35"] == 1
    assert row["Over35Pct"] == 25.0

    assert row["BTTS"] == 2
    assert row["BTTSPct"] == 50.0

    assert row["AvgGoals"] == 2.5


def test_rebuild_league_over_map(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    results_dir = data_dir / "storico" / "risultati"

    league_file = results_dir / "Norway_3rdDivision_Group1_2026.csv"

    matches = [
        MatchResult("Norway", "3rd Division Group 1", 2026, 1, "2026-06-01", "A", "B", 2, 1, ""),
        MatchResult("Norway", "3rd Division Group 1", 2026, 2, "2026-06-08", "C", "D", 1, 0, ""),
        MatchResult("Norway", "3rd Division Group 1", 2026, 3, "2026-06-15", "E", "F", 3, 3, ""),
        MatchResult("Norway", "3rd Division Group 1", 2026, 4, "2026-06-22", "G", "H", 0, 0, ""),
    ]

    results_dir.mkdir(parents=True, exist_ok=True)
    write_results_file(matches, league_file)

    import gioover25.league_over_map as league_over_map_module

    monkeypatch.setattr(league_over_map_module, "DATA_DIR", data_dir)

    output_file = rebuild_league_over_map()

    assert output_file == data_dir / "storico" / "league_over_map.csv"
    assert output_file.exists()

    rows = read_csv(output_file)

    assert len(rows) == 1

    row = rows[0]

    assert row["LeagueId"] == "Norway_3rdDivision_Group1_2026"
    assert row["Matches"] == "4"
    assert row["Over15"] == "2"
    assert row["Over15Pct"] == "50.0"
    assert row["Over25"] == "2"
    assert row["Over25Pct"] == "50.0"
    assert row["Over35"] == "1"
    assert row["Over35Pct"] == "25.0"
    assert row["BTTS"] == "2"
    assert row["BTTSPct"] == "50.0"
    assert row["AvgGoals"] == "2.5"