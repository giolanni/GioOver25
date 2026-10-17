import unittest

from analysis.audit_diretta_standings import (
    LeagueAlias,
    LeagueTarget,
    StandingRow,
    compare_standings,
    parse_standings_feed,
    select_tournament_candidates,
)
from gioover25.registry import LeagueInfo


def standing(
    team,
    position,
    played=6,
    wins=3,
    draws=2,
    losses=1,
    gf=9,
    ga=5,
    points=11,
):
    return StandingRow(
        team=team,
        position=position,
        played=played,
        wins=wins,
        draws=draws,
        losses=losses,
        gf=gf,
        ga=ga,
        gd=gf - ga,
        points=points,
        ppg=points / played,
    )


class StandingsFeedParserTest(unittest.TestCase):
    def test_parses_overall_rows_and_computes_goal_difference(self):
        payload = (
            "TZ÷Standings¬TZS÷Overall¬~"
            "TR÷1¬TN÷Inter¬TM÷6¬TW÷5¬TDR÷1¬TL÷0¬TG÷18:8¬TP÷16¬TPK÷2.67¬~"
            "TR÷2¬TN÷Lazio¬TM÷6¬TW÷5¬TDR÷1¬TL÷0¬TG÷11:4¬TP÷16¬TPK÷2.67¬~"
        )
        rows = parse_standings_feed(payload)
        self.assertEqual(2, len(rows))
        self.assertEqual("Inter", rows[0].team)
        self.assertEqual(10, rows[0].gd)
        self.assertEqual(2.67, rows[0].ppg)

    def test_ignores_non_table_records(self):
        payload = "IPI÷abc¬IPU÷logo.png¬~TZ÷Standings¬~A1÷¬~"
        self.assertEqual([], parse_standings_feed(payload))


class TournamentMappingTest(unittest.TestCase):
    def test_selects_same_country_gender_and_group(self):
        target = LeagueTarget(
            info=LeagueInfo(
                league_id="Italy_SerieC_GironeA",
                country="Italy",
                league="Serie C - Girone A",
                teams=20,
                expected_rounds=38,
                home_away=True,
            ),
            standings_path=None,
            aliases=(LeagueAlias("Italia", "Serie C - Girone A"),),
        )
        search_rows = [
            {
                "id": "template",
                "name": "Serie C - Group A",
                "sport": {"id": 1},
                "gender": {"name": "Men"},
                "defaultCountry": {"name": "Italy"},
                "defaultTournament": {
                    "id": "tournament",
                    "stageWithStatsDataIds": ["stage-a"],
                },
            },
            {
                "id": "women-template",
                "name": "Serie C - Group A Women",
                "sport": {"id": 1},
                "gender": {"name": "Women"},
                "defaultCountry": {"name": "Italy"},
                "defaultTournament": {
                    "id": "women-tournament",
                    "stageWithStatsDataIds": ["women-stage"],
                },
            },
            {
                "id": "brazil-template",
                "name": "Serie C - Group A",
                "sport": {"id": 1},
                "gender": {"name": "Men"},
                "defaultCountry": {"name": "Brazil"},
                "defaultTournament": {
                    "id": "brazil-tournament",
                    "stageWithStatsDataIds": ["brazil-stage"],
                },
            },
        ]
        candidates = select_tournament_candidates(search_rows, target)
        self.assertEqual(1, len(candidates))
        self.assertEqual("tournament", candidates[0].tournament_id)
        self.assertEqual(("stage-a",), candidates[0].stage_ids)


class StandingsComparisonTest(unittest.TestCase):
    def test_known_dictionary_alias_is_not_a_real_difference(self):
        local = [standing("Al-Faysaly", 1)]
        remote = [standing("Al Faysaly", 1)]
        rows = compare_standings("SaudiArabia_ProfessionalLeague", local, remote)
        self.assertEqual(1, len(rows))
        self.assertEqual("ALIAS_ONLY", rows[0].status)
        self.assertEqual("KNOWN_ALIAS", rows[0].name_issue)

    def test_detects_every_requested_statistical_difference(self):
        local = [standing("Inter", 1)]
        remote = [
            StandingRow(
                team="Inter",
                position=2,
                played=7,
                wins=4,
                draws=1,
                losses=2,
                gf=12,
                ga=8,
                gd=4,
                points=13,
                ppg=13 / 7,
            )
        ]
        row = compare_standings("Italy_SerieA", local, remote)[0]
        self.assertEqual("DIFFERENCE", row.status)
        self.assertEqual(
            {
                "position",
                "played",
                "wins",
                "draws",
                "losses",
                "gf",
                "ga",
                "points",
                "ppg",
            },
            set(row.differences.split("|")),
        )

    def test_separates_suspected_alias_from_missing_teams(self):
        local = [standing("Manchester United", 1), standing("Arsenal", 2)]
        remote = [standing("Manchester Utd", 1), standing("Chelsea", 2)]
        rows = compare_standings("Test_League", local, remote)
        by_status = {row.status: row for row in rows}
        self.assertIn("ALIAS_SUSPECTED", by_status)
        self.assertEqual("Manchester United", by_status["ALIAS_SUSPECTED"].local_team)
        self.assertIn("MISSING_ON_DIRETTA", by_status)
        self.assertIn("MISSING_LOCALLY", by_status)


if __name__ == "__main__":
    unittest.main()
