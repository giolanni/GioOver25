"""VEG90 experimental high-confidence Over 2.5 selection.

Frozen candidate rule from exploratory lab:
ExpectedGoals >= 5.0, both teams' GA last5 >= 1.2,
both teams' Over2.5 rate last5 >= 0.8.
"""
from gioover25.scoring_v21dev import ScoreV21DevResult

ENGINE_NAME = "veg90"
ENGINE_VERSION = "1.0.0"
SELECTION_ONLY = True
REQUIRES_DEFENSE_LAST5 = True
REQUIRES_EXPECTED_GOALS = True

def calculate_score(match_stats, league_info, *, expected_goals=None,
                    home_ga_last5=None, away_ga_last5=None):
    min_over = min(float(match_stats.home.last5.over25_rate),
                   float(match_stats.away.last5.over25_rate))
    ga = None if home_ga_last5 is None or away_ga_last5 is None else min(float(home_ga_last5), float(away_ga_last5))
    selected = (expected_goals is not None and ga is not None
                and float(expected_goals) >= 5.0 and ga >= 1.2 and min_over >= 0.8)
    score = 90.0 if selected else 0.0
    reason = (f"VEG90 {'SELECTED' if selected else 'NO-SIGNAL'}: "
              f"EG={expected_goals}, MinGA_L5={ga}, MinOver_L5={min_over:.2f}; "
              "thresholds EG>=5.0, MinGA>=1.2, MinOver>=0.8")
    return ScoreV21DevResult(score=score, band="ALTA" if selected else "BASSA",
        reason=reason, ranking_gap_score=0.0, home_attack_score=0.0,
        away_attack_score=0.0, home_defense_weakness_score=0.0,
        away_defense_weakness_score=0.0, home_last10_over_score=0.0,
        away_last10_over_score=0.0, home_venue_over_score=0.0,
        away_venue_over_score=0.0, btts_profile_score=0.0)
