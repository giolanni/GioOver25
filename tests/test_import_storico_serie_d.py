from tools.import_storico_serie_d import summarize


def test_summarize_empty():
    assert summarize([]) == ("-", "-", 0, "")


def test_summarize_dates_and_counts():
    rows = [{"MatchDate": "2026-09-13"}, {"MatchDate": "2026-09-06"},
            {"MatchDate": "2026-09-13"}]
    assert summarize(rows) == ("2026-09-06", "2026-09-13", 2,
                               "2026-09-06:1, 2026-09-13:2")
