from gioover25.scoring_v21 import calculate_score_v21

ENGINE_NAME = "v21"
ENGINE_VERSION = "2.1.0"


def calculate_score(match_stats, league_info):
    return calculate_score_v21(match_stats, league_info)