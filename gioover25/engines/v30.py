from gioover25.scoring_v30 import calculate_score_v30


ENGINE_NAME = "v30"
ENGINE_VERSION = "3.0.0"


def calculate_score(match_stats, league_info):
    return calculate_score_v30(match_stats, league_info)
