from gioover25.scoring_v24 import calculate_score_v24

ENGINE_NAME = "v24"
ENGINE_VERSION = "2.4.0"


def calculate_score(match_stats, league_info):
    return calculate_score_v24(match_stats, league_info)