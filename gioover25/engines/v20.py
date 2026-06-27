from gioover25.scoring_v2 import calculate_score_v2


ENGINE_NAME = "v20"
ENGINE_VERSION = "2.0.0"


def calculate_score(match_stats, league_info):
    return calculate_score_v2(match_stats, league_info)