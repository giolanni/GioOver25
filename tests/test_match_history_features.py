from pathlib import Path
from analysis.experiments.match_history_features import build_feature_rows


def test_feature_builder_uses_only_previous_matches(tmp_path: Path):
    results_dir = tmp_path / "risultati"
    results_dir.mkdir()
    path = results_dir / "Test_League.csv"
    path.write_text(
        "Country;League;Round;MatchDate;Home;Away;HG;AG;Notes\n"
        "X;L;1;2026-01-01;A;B;1;1;\n"
        "X;L;2;2026-01-02;A;B;2;1;\n"
        "X;L;3;2026-01-03;A;B;3;0;\n"
        "X;L;4;2026-01-04;A;B;0;0;\n"
        "X;L;5;2026-01-05;A;B;1;2;\n"
        "X;L;6;2026-01-06;A;B;4;2;\n",
        encoding="utf-8",
    )
    rows = build_feature_rows(results_dir=results_dir, min_history=5, windows=(5,))
    assert len(rows) == 1
    row = rows[0]
    assert row["MatchDate"] == "2026-01-06"
    assert row["HomePlayedBefore"] == 5
    assert row["AwayPlayedBefore"] == 5
    assert row["HomeGFFull"] == 1.4
    assert row["AwayGFFull"] == 0.8
    assert row["Over25"] == 1
    assert row["BTTS"] == 1


def test_same_day_matches_do_not_see_each_other(tmp_path: Path):
    results_dir = tmp_path / "risultati"
    results_dir.mkdir()
    path = results_dir / "Test_League.csv"
    lines = ["Country;League;Round;MatchDate;Home;Away;HG;AG;Notes"]
    for day in range(1, 6):
        lines.append(f"X;L;{day};2026-01-0{day};A;B;1;0;")
        lines.append(f"X;L;{day};2026-01-0{day};C;D;1;0;")
    lines += [
        "X;L;6;2026-01-06;A;B;2;2;",
        "X;L;6;2026-01-06;C;D;3;3;",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rows = build_feature_rows(results_dir=results_dir, min_history=5, windows=(5,))
    assert len(rows) == 2
    assert all(row["MinPlayedBefore"] == 5 for row in rows)
