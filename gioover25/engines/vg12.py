"""VG1.2: derived BTTS ranking from unchanged original VG1 scoring."""
from dataclasses import replace
from . import vg1

ENGINE_NAME = "vg12"
ENGINE_VERSION = "1.0.0"
MARKET = "GOAL"
SELECTION_ONLY = True


def calculate_score(match_stats, league_info):
    base = vg1.calculate_score(match_stats, league_info)
    selected = base.band != "ALTA" and (65.0 <= float(base.score) < 70.0)
    # Select only the additional score window, never the original VG1 ALTA.
    band = "ALTA" if selected else ("MEDIA" if base.band == "ALTA" else base.band)
    return replace(base, band=band, reason="VG1.2 " + ("SELECTED" if selected else "EXCLUDED") + " | " + base.reason)
