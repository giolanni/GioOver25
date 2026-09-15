from gioover25.scoring_vg1 import calculate_score_vg1


ENGINE_NAME = "vg1"
ENGINE_VERSION = "1.0.0"
MARKET = "GOAL"


def calculate_score(match_stats, league_info):
    return calculate_score_vg1(match_stats, league_info)
