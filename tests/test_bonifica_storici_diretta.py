from tools.bonifica_storici_diretta import Result, compare, parse_results_feed, team_overlap


def test_parse_results_feed_finished_matches_only():
    payload = (
        "ZA÷ITALIA: Serie A¬~"
        "ER÷Giornata 2¬~"
        "AA÷m1¬AD÷1788037200¬AE÷Inter¬AF÷Napoli¬AG÷3¬AH÷2¬~"
        "AA÷m2¬AD÷1788040800¬AE÷Roma¬AF÷Milan¬AG÷¬AH÷¬~"
    )
    rows = parse_results_feed(payload)
    assert len(rows) == 1
    assert rows[0].home == "Inter"
    assert rows[0].away == "Napoli"
    assert (rows[0].hg, rows[0].ag) == (3, 2)


def test_compare_detects_missing_extra_and_score_diff():
    local = [
        Result("2026-09-01", "Inter", "Napoli", 2, 2),
        Result("2026-09-02", "Roma", "Milan", 1, 0),
    ]
    remote = [
        Result("2026-09-01", "Inter", "Napoli", 3, 2),
        Result("2026-09-03", "Lazio", "Genoa", 1, 0),
    ]
    equal, missing, extra, score_diff = compare("Italy_SerieA", local, remote)
    assert equal == 0
    assert len(missing) == 1
    assert len(extra) == 1
    assert len(score_diff) == 1


def test_team_overlap_rejects_unrelated_competition():
    local = [Result("2026-09-01", "Inter", "Napoli", 1, 0)]
    remote = [Result("2026-09-01", "Chelsea", "Arsenal", 1, 0)]
    overlap, union = team_overlap("Italy_SerieA", local, remote)
    assert overlap == 0
    assert union == 4
