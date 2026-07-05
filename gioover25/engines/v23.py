from gioover25.scoring_v23 import calculate_score_v23

ENGINE_NAME = "v23"
ENGINE_VERSION = "2.3.0"


def calculate_score(match_stats, league_info):
    return calculate_score_v23(match_stats, league_info)