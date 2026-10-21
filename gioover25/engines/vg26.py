"""VG2.6: derived BTTS ranking from unchanged original VG1 scoring."""
from dataclasses import replace
from . import vg1

ENGINE_NAME = "vg26"
ENGINE_VERSION = "1.0.0"
MARKET = "GOAL"
SELECTION_ONLY = True


def calculate_score(match_stats, league_info):
    base = vg1.calculate_score(match_stats, league_info)
    min_gf = min(float(match_stats.home.last5.gf_per_match), float(match_stats.away.last5.gf_per_match))
    selected = base.band == "ALTA" and min_gf > 2.6
    # Keep original numeric VG1 score and all feature diagnostics.
    # ALTA means selected by this variant; otherwise retain a non-ALTA band.
    band = "ALTA" if selected else ("MEDIA" if base.band == "ALTA" else base.band)
    return replace(base, band=band, reason="VG2.2.6 " + ("SELECTED" if selected else "EXCLUDED") + " | " + base.reason)
