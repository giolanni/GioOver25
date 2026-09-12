from gioover25.scoring_v31 import calculate_score_v31


ENGINE_NAME = "v31"
ENGINE_VERSION = "3.1.0"


def calculate_score(match_stats, league_info):
    return calculate_score_v31(
        match_stats,
        league_info,
    )
