"""Five BTTS VG1-derived experimental engine selectors.

No changes to the original VG1 scorer. Use on the *same* original
VG1 scoring result (and original match_stats) to prevent divergence.

Names are VG1.2, VG1.3, VG1.4, VG2.2 and VG2.6.
The selection criterion is an explicit boolean; callers must not infer
it from the original VG1 band after applying a variant.
"""
from dataclasses import dataclass
import re

VARIANTS = ("VG1.2", "VG1.3", "VG1.4", "VG2.2", "VG2.6")
FAKE_RANGES = {"VG1.2": (65.0, 70.0),
               "VG1.3": (68.0, 72.0),
               "VG1.4": (65.0, 72.0)}
MIN_GF_THRESHOLDS = {"VG2.2": 2.2, "VG2.6": 2.6}
_GF_PATTERN = re.compile(r"(?:^|[,\\s])MinGFL5=([+-]?\\d+(?:\\.\\d+)?)")


@dataclass(frozen=True)
class VariantDecision:
    engine: str
    selected: bool
    original_vg1_alta: bool
    original_vg1_score: float
    min_gf_l5: float | None
    reason: str


def decide_variant(variant, vg1_result, match_stats=None):
    """Decide using unmodified VG1 result.

    VG1 ALTA includes every original VG1 result with band == ALTA.
    For VG2.x the MinGFL5 feature is read from original match_stats
    (preferred, full precision); reason is fallback only, with a guard
    against its two-decimal rounding at the threshold.
    """
    if variant not in VARIANTS:
        raise ValueError(f"Unknown variant {variant!r}; choose {VARIANTS}")
    score = float(vg1_result.score)
    band = str(vg1_result.band).strip().upper()
    original_alta = band == "ALTA"
    gf = None
    if match_stats is not None:
        gf = min(float(match_stats.home.last5.gf_per_match),
                 float(match_stats.away.last5.gf_per_match))
    if variant in FAKE_RANGES:
        low, high = FAKE_RANGES[variant]
        selected = original_alta or low <= score < high
        reason = f"VG1 ALTA or original VG1 score in [{low:g},{high:g})"
    else:
        if gf is None:
            match = _GF_PATTERN.search(str(vg1_result.reason))
            if match:
                gf = float(match.group(1))
            else:
                raise ValueError("VG2.x requires match_stats or MinGFL5 in VG1 reason")
        threshold = MIN_GF_THRESHOLDS[variant]
        selected = original_alta and gf > threshold
        reason = f"Original VG1 ALTA and MinGFL5 > {threshold:g}"
    return VariantDecision(variant, selected, original_alta, score, gf, reason)


def evaluate_all(vg1_result, match_stats=None):
    """Return all five decisions using a single VG1 score computation."""
    return {variant: decide_variant(variant, vg1_result, match_stats)
            for variant in VARIANTS}
