import csv
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

from analysis.ranking_statistics import (
    METRIC_BY_KEY,
    build_report,
    calculate_stat,
    common_keys,
    filter_dates,
    load_engine_history,
    main,
    parse_date,
    remove_australia,
)


HEADER = [
    "PredictionDate",
    "MatchDate",
    "LeagueId",
    "Home",
    "Away",
    "Band",
    "HG",
    "AG",
    "Over25",
]


def write_history(root, engine, rows):
    path = root / engine / f"storico_ranking_{engine}.csv"
    path.parent.mkdir(parents=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def row(day, league, home, away, band, hg, ag, over25, match_date=True):
    return {
        "PredictionDate": day,
        "MatchDate": day if match_date else "",
        "LeagueId": league,
        "Home": home,
        "Away": away,
        "Band": band,
        "HG": hg,
        "AG": ag,
        "Over25": over25,
    }


class RankingStatisticsTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_loads_only_finished_rows_and_uses_prediction_date_for_legacy(self):
        write_history(
            self.root,
            "v20",
            [
                row("2026-09-01", "League_A", "A", "B", "ALTA", "2", "1", "OK"),
                row("2026-09-02", "League_A", "C", "D", "MEDIA", "1", "1", "KO", match_date=False),
                row("2026-09-03", "League_A", "E", "F", "ALTA", "", "", ""),
            ],
        )

        rows, legacy, duplicates = load_engine_history(self.root, "v20")

        self.assertEqual(len(rows), 2)
        self.assertEqual(legacy, 1)
        self.assertEqual(duplicates, 0)
        self.assertEqual(rows[1].match_date, date(2026, 9, 2))
        self.assertTrue(rows[1].used_legacy_date)

    def test_metrics_keep_media_and_media_alta_separate_and_offer_combined(self):
        write_history(
            self.root,
            "v20",
            [
                row("2026-09-01", "League_A", "A", "B", "MEDIA", "1", "1", "KO"),
                row("2026-09-02", "League_A", "C", "D", "MEDIA", "1", "0", "KO"),
                row("2026-09-03", "League_A", "E", "F", "MEDIA-ALTA", "2", "0", "KO"),
            ],
        )
        rows, _, _ = load_engine_history(self.root, "v20")

        media = calculate_stat(rows, METRIC_BY_KEY["media_o15"])
        media_alta = calculate_stat(rows, METRIC_BY_KEY["media_alta_o15"])
        combined = calculate_stat(rows, METRIC_BY_KEY["media_totale_o15"])

        self.assertEqual((media.ok, media.ko), (1, 1))
        self.assertEqual((media_alta.ok, media_alta.ko), (1, 0))
        self.assertEqual((combined.ok, combined.ko), (2, 1))

    def test_common_set_is_intersection_of_exact_fixture_keys(self):
        shared = row("2026-09-01", "League_A", "A", "B", "ALTA", "2", "1", "OK")
        write_history(
            self.root,
            "v20",
            [shared, row("2026-09-02", "League_A", "C", "D", "ALTA", "0", "0", "KO")],
        )
        write_history(
            self.root,
            "v25",
            [shared, row("2026-09-03", "League_A", "E", "F", "ALTA", "3", "0", "OK")],
        )
        v20, _, _ = load_engine_history(self.root, "v20")
        v25, _, _ = load_engine_history(self.root, "v25")

        keys, inconsistent = common_keys({"v20": v20, "v25": v25})

        self.assertEqual(inconsistent, 0)
        self.assertEqual(len(keys), 1)
        self.assertEqual(next(iter(keys))[1:], (date(2026, 9, 1), "A", "B"))

    def test_common_set_excludes_inconsistent_results(self):
        write_history(
            self.root,
            "v20",
            [row("2026-09-01", "League_A", "A", "B", "ALTA", "2", "1", "OK")],
        )
        write_history(
            self.root,
            "v25",
            [row("2026-09-01", "League_A", "A", "B", "ALTA", "1", "1", "KO")],
        )
        v20, _, _ = load_engine_history(self.root, "v20")
        v25, _, _ = load_engine_history(self.root, "v25")

        keys, inconsistent = common_keys({"v20": v20, "v25": v25})

        self.assertEqual(keys, set())
        self.assertEqual(inconsistent, 1)

    def test_date_and_australia_filters(self):
        write_history(
            self.root,
            "v20",
            [
                row("2026-09-01", "Australia_NPL", "A", "B", "ALTA", "2", "1", "OK"),
                row("2026-09-02", "League_A", "C", "D", "ALTA", "1", "0", "KO"),
                row("2026-09-03", "League_A", "E", "F", "ALTA", "3", "0", "OK"),
            ],
        )
        rows, _, _ = load_engine_history(self.root, "v20")

        filtered = filter_dates(
            rows,
            start_date=parse_date("02/09/2026"),
            end_date=parse_date("2026-09-03"),
        )

        self.assertEqual(len(filtered), 2)
        self.assertEqual(len(remove_australia(rows)), 2)

    def test_report_has_overall_and_common_populations(self):
        shared = row("2026-09-01", "League_A", "A", "B", "ALTA", "2", "1", "OK")
        write_history(
            self.root,
            "v20",
            [shared, row("2026-09-02", "League_A", "C", "D", "ALTA", "0", "0", "KO")],
        )
        write_history(self.root, "v25", [shared])
        histories = {}
        for engine in ("v20", "v25"):
            histories[engine], _, _ = load_engine_history(self.root, engine)

        report, _, _ = build_report(
            histories,
            [METRIC_BY_KEY["alta_o25"]],
            ["overall", "common"],
            ["all"],
        )
        indexed = {(item.scope, item.engine): item for item in report}

        self.assertEqual(indexed[("overall", "v20")].total, 2)
        self.assertEqual(indexed[("overall", "v20")].percentage, 50.0)
        self.assertEqual(indexed[("common", "v20")].total, 1)
        self.assertEqual(indexed[("common", "v25")].total, 1)

    def test_daily_csv_contains_cumulative_and_each_unique_requested_date(self):
        write_history(
            self.root,
            "v20",
            [
                row("2026-09-04", "League_A", "A", "B", "ALTA", "2", "1", "OK"),
                row("2026-09-05", "League_A", "C", "D", "ALTA", "1", "0", "KO"),
            ],
        )
        output = self.root / "report.csv"

        with redirect_stdout(io.StringIO()):
            result = main(
                [
                    "--history-root",
                    str(self.root),
                    "--engines",
                    "v20",
                    "--dates",
                    "2026-09-05",
                    "2026-09-04",
                    "2026-09-05",
                    "2026-09-08",
                    "--daily",
                    "--metrics",
                    "alta_o25",
                    "--csv",
                    str(output),
                ]
            )

        with output.open(encoding="utf-8-sig", newline="") as handle:
            exported = list(csv.DictReader(handle, delimiter=";"))

        self.assertEqual(result, 0)
        self.assertEqual(len(exported), 4)
        self.assertEqual(exported[0]["TipoPeriodo"], "CUMULATIVO")
        self.assertEqual(exported[0]["Analisi"], "DATE RICHIESTE")
        self.assertEqual(exported[0]["ALTA O2.5"], "1/2 (50.00%)")
        daily = [item for item in exported if item["TipoPeriodo"] == "GIORNO"]
        self.assertEqual(
            [item["Periodo"] for item in daily],
            ["2026-09-04", "2026-09-05", "2026-09-08"],
        )
        self.assertEqual(daily[-1]["ALTA O2.5"], "-")


if __name__ == "__main__":
    unittest.main()
