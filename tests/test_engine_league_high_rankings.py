from analysis.metrics.build_engine_league_high_rankings import (
    build_engine_ranking,
    detect_delimiter,
)


def test_header_controls_delimiter_when_reason_contains_commas(tmp_path):
    history = tmp_path / "history.csv"
    history.write_text(
        "LeagueId;Band;Over25;MatchDate;Reason\n"
        "League_A;ALTA;OK;2026-09-01;uno,due,tre,quattro\n",
        encoding="utf-8",
    )

    assert detect_delimiter(history) == ";"
    ranking = build_engine_ranking("v25", history)

    assert len(ranking) == 1
    assert ranking.iloc[0]["OK"] == 1


def test_unquoted_extra_separator_does_not_drop_ranking_row(tmp_path):
    history = tmp_path / "history.csv"
    history.write_text(
        "LeagueId;Band;Over25;MatchDate;Reason\n"
        "League_A;ALTA;KO;2026-09-01;parte 1;parte 2\n",
        encoding="utf-8",
    )

    ranking = build_engine_ranking("v25", history)

    assert len(ranking) == 1
    assert ranking.iloc[0]["KO"] == 1


def test_headerless_history_is_supported(tmp_path):
    history = tmp_path / "history.csv"
    history.write_text(
        "2026-09-01;2026-09-02;League_A;1;Home;Away;91;ALTA;"
        "FINAL;2;1;3;OK;OK;reason,with,many,commas\n",
        encoding="utf-8",
    )

    assert detect_delimiter(history) == ";"
    ranking = build_engine_ranking("v25", history)

    assert len(ranking) == 1
    assert ranking.iloc[0]["OK"] == 1
