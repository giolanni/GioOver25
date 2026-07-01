from gioover25.scoring_v22 import calculate_score_v22

ENGINE_NAME = "v22"
ENGINE_VERSION = "2.2.0"


def calculate_score(match_stats, league_info):
    return calculate_score_v22(match_stats, league_info)