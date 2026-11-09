from analysis import data_quality


HEADER = (
    "PredictionDate;MatchDate;LeagueId;Round;Home;Away;Score;Band;"
    "AlgorithmVersion;HG;AG;Outcome\n"
)


def _run_laboratory_check(tmp_path, monkeypatch, rows):
    laboratory = tmp_path / "01_matches.csv"
    laboratory.write_text(HEADER + "".join(rows), encoding="utf-8")
    unmatched = tmp_path / "06_unmatched_matches.csv"
    monkeypatch.setattr(data_quality, "ROOT", tmp_path)
    monkeypatch.setattr(data_quality, "LAB_FILE", laboratory)
    monkeypatch.setattr(data_quality, "LAB_UNMATCHED", unmatched)

    anomalies = []
    data_quality.check_laboratory(anomalies, {"TestLeague"})
    return anomalies


def test_laboratory_rerankings_are_not_duplicate_predictions(tmp_path, monkeypatch):
    anomalies = _run_laboratory_check(
        tmp_path,
        monkeypatch,
        [
            "2026-11-07;2026-11-09;TestLeague;10;Home;Away;80;ALTA;2.5.0;2;1;OK\n",
            "2026-11-08;2026-11-09;TestLeague;10;Home;Away;80;ALTA;2.5.0;2;1;OK\n",
            "2026-11-08;2026-11-09;TestLeague;11;Home;Away;81;ALTA;2.5.0;2;1;OK\n",
        ],
    )

    assert not [item for item in anomalies if item.code == "LAB_DUP_MATCH"]


def test_laboratory_exact_prediction_duplicate_is_reported(tmp_path, monkeypatch):
    row = (
        "2026-11-08;2026-11-09;TestLeague;10;Home;Away;80;ALTA;"
        "2.5.0;2;1;OK\n"
    )
    anomalies = _run_laboratory_check(
        tmp_path,
        monkeypatch,
        [row, row],
    )

    duplicates = [item for item in anomalies if item.code == "LAB_DUP_MATCH"]
    assert len(duplicates) == 1
    assert duplicates[0].severity == "WARNING"
