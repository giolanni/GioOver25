"""VG1.2: derived BTTS ranking from unchanged original VG1 scoring."""
from dataclasses import replace
from . import vg1

ENGINE_NAME = "vg12"
ENGINE_VERSION = "1.0.0"
MARKET = "GOAL"


def calculate_score(match_stats, league_info):
    base = vg1.calculate_score(match_stats, league_info)
    selected = base.band == "ALTA" or (65.0 <= float(base.score) < 70.0)
    # Keep original numeric VG1 score and all feature diagnostics.
    # ALTA means selected by this variant; otherwise retain a non-ALTA band.
    band = "ALTA" if selected else ("MEDIA" if base.band == "ALTA" else base.band)
    return replace(base, band=band, reason="VG1.2 " + ("SELECTED" if selected else "EXCLUDED") + " | " + base.reason)
