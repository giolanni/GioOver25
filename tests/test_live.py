import csv
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from gioover25.live import (
    LIVE_FIELDS,
    OUTCOME_KO,
    OUTCOME_OK,
    OUTCOME_UNAVAILABLE,
    OUTCOME_WAITING,
    STATUS_FINAL,
    STATUS_LIVE,
    STATUS_POSTPONED,
    STATUS_SCHEDULED,
    LiveMatch,
    deduplicate_live,
    evaluate_market,
    freshness,
    load_engine_rankings,
    match_rankings,
    parse_live_feed,
    read_live_csv,
    summarize_engine,
    write_live_csv,
)


class LiveFeedParserTest(unittest.TestCase):
    def setUp(self):
        self.day = date(2026, 11, 7)
        self.now = datetime(2026, 11, 7, 13, 10, tzinfo=timezone.utc)
        scheduled = int(datetime(2026, 11, 7, 15, 0, tzinfo=timezone.utc).timestamp())
        live = int(datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc).timestamp())
        final = int(datetime(2026, 11, 7, 9, 0, tzinfo=timezone.utc).timestamp())
        tomorrow = int(datetime(2026, 11, 8, 9, 0, tzinfo=timezone.utc).timestamp())
        self.payload = (
            "~ZA÷ITALIA: Serie A¬"
            f"~AA÷scheduled1¬AD÷{scheduled}¬AB÷1¬AC÷1¬AE÷Roma¬AF÷Lazio¬"
            f"~AA÷live1¬AD÷{live}¬AB÷2¬AC÷13¬AE÷Inter¬AF÷Milan¬AG÷2¬AH÷0¬"
            f"~AA÷final1¬AD÷{final}¬AB÷3¬AC÷3¬AE÷Napoli¬AF÷Torino¬AG÷1¬AH÷1¬"
            f"~AA÷post1¬AD÷{scheduled}¬AB÷4¬AC÷Posticipata¬AE÷Como¬AF÷Parma¬"
            f"~AA÷tomorrow1¬AD÷{tomorrow}¬AB÷1¬AC÷1¬AE÷Udinese¬AF÷Pisa¬"
        )

    @staticmethod
    def resolve(country, league, home, away):
        return "Italy_SerieA" if country == "ITALIA" and league == "Serie A" else None

    def test_status_score_minute_and_date_filter(self):
        matches = parse_live_feed(self.payload, self.day, self.resolve, self.now)
        self.assertEqual(4, len(matches))
        by_id = {row.match_id: row for row in matches}
        self.assertEqual(STATUS_SCHEDULED, by_id["scheduled1"].status)
        self.assertEqual(STATUS_LIVE, by_id["live1"].status)
        self.assertEqual("56'", by_id["live1"].minute)
        self.assertEqual((2, 0), (by_id["live1"].hg, by_id["live1"].ag))
        self.assertEqual(STATUS_FINAL, by_id["final1"].status)
        self.assertEqual("FT", by_id["final1"].minute)
        self.assertEqual(STATUS_POSTPONED, by_id["post1"].status)
        self.assertNotIn("tomorrow1", by_id)

    def test_unmapped_competitions_are_excluded(self):
        matches = parse_live_feed(self.payload, self.day, lambda *_args: None, self.now)
        self.assertEqual([], matches)


class LiveDeduplicationTest(unittest.TestCase):
    def test_match_id_keeps_most_advanced_state(self):
        scheduled = LiveMatch("2026-11-07", "Italy_A", "Roma", "Lazio", "abc", status=STATUS_SCHEDULED)
        final = LiveMatch("2026-11-07", "Italy_A", "Roma", "Lazio", "abc", hg=3, ag=1, status=STATUS_FINAL)
        result = deduplicate_live([scheduled, final])
        self.assertEqual([final], result)

    def test_composite_fallback_deduplicates_accents_and_punctuation(self):
        first = LiveMatch("2026-11-07", "France_L1", "Paris Saint-Germain", "Lyon", status=STATUS_SCHEDULED)
        second = LiveMatch("2026-11-07", "France_L1", "Paris Saint Germain", "Lyon", hg=1, ag=0, status=STATUS_LIVE)
        result = deduplicate_live([first, second])
        self.assertEqual(1, len(result))
        self.assertEqual(STATUS_LIVE, result[0].status)


class LiveCsvTest(unittest.TestCase):
    def test_atomic_round_trip_and_exact_header(self):
        match = LiveMatch(
            "2026-11-07", "Italy_SerieA", "Roma", "Lazio", "abc", "71'",
            2, 1, STATUS_LIVE, "2026-11-07T19:41:00+01:00",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data" / "live" / "partite_live.csv"
            write_live_csv(path, [match])
            with path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.reader(stream, delimiter=";")
                self.assertEqual(list(LIVE_FIELDS), next(reader))
            self.assertEqual([match], read_live_csv(path))
            self.assertFalse(path.with_name(path.name + ".tmp").exists())


class LiveMatchingTest(unittest.TestCase):
    def test_exact_normalized_and_fuzzy_typo_matching(self):
        rankings = [
            {"MatchDate": "2026-11-07", "LeagueId": "France_L1", "Home": "Paris Saint Germain", "Away": "Lyon"},
            {"MatchDate": "2026-11-07", "LeagueId": "Italy_A", "Home": "Juventuus", "Away": "Roma"},
        ]
        live = [
            LiveMatch("2026-11-07", "France_L1", "Paris Saint-Germain", "Lyon", "a"),
            LiveMatch("2026-11-07", "Italy_A", "Juventus", "Roma", "b"),
        ]
        matched = match_rankings(rankings, live)
        self.assertEqual(["a", "b"], [row.match_id if row else None for _, row in matched])

    def test_fuzzy_ambiguous_match_is_rejected(self):
        ranking = [{"MatchDate": "2026-11-07", "LeagueId": "X", "Home": "United", "Away": "City"}]
        live = [
            LiveMatch("2026-11-07", "X", "United A", "City", "a"),
            LiveMatch("2026-11-07", "X", "United B", "City", "b"),
        ]
        self.assertIsNone(match_rankings(ranking, live, fuzzy_threshold=0.75)[0][1])

    def test_engine_loader_deduplicates_same_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "v25" / "storico_ranking_v25.csv"
            path.parent.mkdir(parents=True)
            path.write_text(
                "PredictionDate;MatchDate;LeagueId;Home;Away;Score\n"
                "2026-11-06;2026-11-07;Italy_A;Roma;Lazio;70\n"
                "2026-11-07;2026-11-07;Italy_A;Roma;Lazio;71\n",
                encoding="utf-8",
            )
            loaded = load_engine_rankings(root, "2026-11-07", "v25")
            self.assertEqual(1, len(loaded["v25"]))
            self.assertEqual("71", loaded["v25"][0]["Score"])


class MarketEvaluationTest(unittest.TestCase):
    def test_ok_is_irreversible_while_ko_requires_final(self):
        live_over = LiveMatch("2026-11-07", "X", "A", "B", hg=2, ag=1, status=STATUS_LIVE)
        live_waiting = LiveMatch("2026-11-07", "X", "A", "B", hg=2, ag=0, status=STATUS_LIVE)
        final_ko = LiveMatch("2026-11-07", "X", "A", "B", hg=2, ag=0, status=STATUS_FINAL)
        self.assertEqual(OUTCOME_OK, evaluate_market(live_over, "Over2.5"))
        self.assertEqual(OUTCOME_OK, evaluate_market(live_over, "BTTS"))
        self.assertEqual(OUTCOME_WAITING, evaluate_market(live_waiting, "Over2.5"))
        self.assertEqual(OUTCOME_WAITING, evaluate_market(live_waiting, "BTTS"))
        self.assertEqual(OUTCOME_KO, evaluate_market(final_ko, "Over2.5"))
        self.assertEqual(OUTCOME_KO, evaluate_market(final_ko, "BTTS"))
        self.assertEqual(OUTCOME_UNAVAILABLE, evaluate_market(None, "BTTS"))

    def test_summary_percentages_use_final_matches_only(self):
        rankings = [
            {"Home": "A"}, {"Home": "B"}, {"Home": "C"},
        ]
        matches = [
            LiveMatch("2026-11-07", "X", "A", "Z", hg=2, ag=1, status=STATUS_FINAL),
            LiveMatch("2026-11-07", "X", "B", "Z", hg=2, ag=0, status=STATUS_FINAL),
            LiveMatch("2026-11-07", "X", "C", "Z", hg=4, ag=1, status=STATUS_LIVE),
        ]
        summary = summarize_engine("v25", list(zip(rankings, matches)))
        self.assertEqual(2, summary.final_matches)
        self.assertEqual(50.0, summary.over_pct)
        self.assertEqual(50.0, summary.btts_pct)


class FreshnessTest(unittest.TestCase):
    def test_stale_state_uses_last_update(self):
        now = datetime(2026, 11, 7, 20, 0, tzinfo=timezone.utc)
        old = (now - timedelta(seconds=181)).isoformat(timespec="seconds")
        row = LiveMatch("2026-11-07", "X", "A", "B", last_update=old)
        state = freshness([row], Path("not-created.csv"), stale_after=180, now=now)
        self.assertEqual("STALE", state.state)


if __name__ == "__main__":
    unittest.main()
