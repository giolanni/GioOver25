from pathlib import Path

from gioover25.missing_results import (
    MissingMatch,
    exclude_matches_already_in_results,
    load_results_index,
)


def test_results_without_league_id_use_canonical_filename(tmp_path: Path) -> None:
    results = tmp_path / "Croatia_PrvaNL.csv"
    results.write_text(
        "Country;League;Round;MatchDate;Home;Away;HG;AG;Notes\n"
        "Croatia;Prva NL;9;2026-10-17;Dubrava;Vukovar 1991;3;2;\n",
        encoding="utf-8",
    )

    index = load_results_index(tmp_path)

    assert (
        "croatia_prvanl",
        "2026-10-17",
        "dubrava",
        "vukovar 1991",
    ) in index


def test_explicit_league_id_keeps_precedence(tmp_path: Path) -> None:
    results = tmp_path / "fallback_name.csv"
    results.write_text(
        "LeagueId;League;MatchDate;Home;Away;HG;AG\n"
        "Canonical_League;Display League;2026-10-17;Home FC;Away FC;1;0\n",
        encoding="utf-8",
    )

    index = load_results_index(tmp_path)

    assert (
        "canonical_league",
        "2026-10-17",
        "home fc",
        "away fc",
    ) in index
    assert not any(key[0] == "display league" for key in index)


def test_completed_croatia_fixture_is_excluded_from_missing(tmp_path: Path) -> None:
    results = tmp_path / "Croatia_PrvaNL.csv"
    results.write_text(
        "Country;League;Round;MatchDate;Home;Away;HG;AG;Notes\n"
        "Croatia;Prva NL;9;2026-10-17;Dubrava;Vukovar 1991;3;2;\n",
        encoding="utf-8",
    )
    missing = MissingMatch(
        league_id="Croatia_PrvaNL",
        season="",
        round="10",
        match_date="2026-10-17",
        prediction_date="2026-10-17",
        home="Dubrava",
        away="Vukovar 1991",
        band="BASSA",
        source_file="storico_ranking_vg2.6.csv",
    )

    index = load_results_index(tmp_path)

    assert exclude_matches_already_in_results([missing], index) == []
