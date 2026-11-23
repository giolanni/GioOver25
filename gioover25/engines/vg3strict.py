"""Intersezione giornaliera delle TOP2 VG3 e del modello BTTS sui driver V25."""
import json
import math
from collections import defaultdict
from pathlib import Path

ENGINE_NAME = "vg3strict"
ENGINE_VERSION = "3.0.0-strict.1"
MARKET = "GOAL"
MODEL = Path(__file__).with_name("vg3strict_model.json")


def fixture(row):
    return tuple(row[c] for c in ("MatchDate", "LeagueId", "Home", "Away"))


def select(vg3_rows, v25_rows):
    model = json.loads(MODEL.read_text())
    v25 = {fixture(row): row for row in v25_rows}
    by_day = defaultdict(list)
    for row in vg3_rows:
        key = fixture(row)
        if key not in v25 or row["Score"] == "":
            continue
        driver_row = v25[key]
        raw = {c: float(driver_row[c]) for c in model["weights"] if c in driver_row}
        raw.update(vg3=row["Score"] / 100,
                   balanced_att=min(raw["HomeAttackScore"], raw["AwayAttackScore"]),
                   balanced_def=min(raw["HomeDefenseWeaknessScore"], raw["AwayDefenseWeaknessScore"]),
                   balanced_venue=min(raw["HomeVenueOverScore"], raw["AwayVenueOverScore"]))
        z = model["intercept"] + sum(w * raw[c] for c, w in model["weights"].items())
        cross = 100 / (1 + math.exp(-z))
        by_day[key[0]].append((key, row, cross, raw["balanced_venue"]))

    selections = []
    for candidates in by_day.values():
        alta = sorted((r for r in candidates if r[1]["Band"] == "ALTA"),
                      key=lambda r: (-r[1]["Score"], r[0]))[:2]
        cross = sorted((r for r in candidates if r[3] >= 7.5),
                       key=lambda r: (-r[2], r[0]))[:2]
        positions = {r[0]: i for i, r in enumerate(cross, 1)}
        for i, (key, row, score, venue) in enumerate(alta, 1):
            if key in positions:
                selections.append(dict(v25[key], Score=row["Score"], Band="ALTA",
                                       AlgorithmVersion=ENGINE_VERSION,
                                       Reason=f"VG3 #{i} | BTTS su V25 #{positions[key]} ({score:.2f}) | MinVenue={venue:.2f}"))
    return selections
