"""VG2.2: derived BTTS ranking from unchanged original VG1 scoring."""
from dataclasses import replace
from . import vg1

ENGINE_NAME = "vg22"
ENGINE_VERSION = "1.0.0"
MARKET = "GOAL"


def calculate_score(match_stats, league_info):
    base = vg1.calculate_score(match_stats, league_info)
    min_gf = min(float(match_stats.home.last5.gf_per_match), float(match_stats.away.last5.gf_per_match))
        selected = base.band == "ALTA" and min_gf > 2.2
    # Keep original numeric VG1 score and all feature diagnostics.
    # ALTA means selected by this variant; otherwise retain a non-ALTA band.
    band = "ALTA" if selected else ("MEDIA" if base.band == "ALTA" else base.band)
    return replace(base, band=band, reason=f"VG2.2 [{'selected' if False else ''}] " + ("SELECTED" if selected else "EXCLUDED") + " | " + base.reason)
