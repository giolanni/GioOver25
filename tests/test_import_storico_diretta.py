from datetime import date
from pathlib import Path

from tools.import_storico_diretta import extract
from tools.prepare_input import load_registry


def test_import_serie_d_only_selected_group():
    registry = load_registry(Path("data/league_registry.csv"))
    # Timestamp is resolved in the local timezone, as in the daily provider.
    from datetime import datetime
    stamp = int(datetime(2026, 10, 11, 15).timestamp())
    payload = (
        "ZA÷ITALIA: Serie D - Girone A¬~"
        f"AA÷testA¬AD÷{stamp}¬AE÷Casa A¬AF÷Ospiti A¬AG÷2¬AH÷1¬AB÷3¬~"
        "ZA÷ITALIA: Serie D - Girone B¬~"
        f"AA÷testB¬AD÷{stamp}¬AE÷Casa B¬AF÷Ospiti B¬AG÷3¬AH÷0¬AB÷3¬~"
    )
    rows, rejected = extract(payload, registry, {"Italy_SerieD_GironeA"},
                             date(2026, 9, 1), date(2026, 11, 15))
    assert len(rows) == 1
    assert rows[0]["LeagueId"] == "Italy_SerieD_GironeA"
    assert (rows[0]["HG"], rows[0]["AG"]) == ("2", "1")
    assert rejected["LEAGUE_UNMAPPED_OR_OUTSIDE_SELECTION"] == 1


def test_import_excludes_missing_scores():
    registry = load_registry(Path("data/league_registry.csv"))
    from datetime import datetime
    stamp = int(datetime(2026, 10, 11, 15).timestamp())
    payload = (f"ZA÷ITALIA: Serie D - Girone A¬~"
               f"AA÷test¬AD÷{stamp}¬AE÷Casa¬AF÷Ospiti¬AG÷¬AH÷¬AB÷1¬~")
    rows, rejected = extract(payload, registry, {"Italy_SerieD_GironeA"},
                             date(2026, 9, 1), date(2026, 11, 15))
    assert not rows
    assert rejected["NOT_CONFIRMED_FINAL"] == 1
