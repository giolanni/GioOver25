from gioover25.scoring_v25 import calculate_score_v25


ENGINE_NAME = "v25"
ENGINE_VERSION = "2.5.0"


def calculate_score(match_stats, league_info):
    return calculate_score_v25(
        match_stats,
        league_info,
    )