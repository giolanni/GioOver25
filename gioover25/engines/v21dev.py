from gioover25.scoring_v21dev import calculate_score_v21dev

ENGINE_NAME = "v21dev"
ENGINE_VERSION = "2.1-dev"


def calculate_score(match_stats, league_info):
    return calculate_score_v21dev(match_stats, league_info)