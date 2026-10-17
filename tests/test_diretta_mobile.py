import unittest

from tools.diretta_mobile import parse_mobile
from tools.prepare_input import RegistryRow, resolve, resolve_match


class DirettaMobileParserTest(unittest.TestCase):
    def test_scheduled_and_finished_matches(self):
        page = """
        <html><body>
          <div id="score-data">
          <h4>BHUTAN: Premier League <a href="/classifiche/x/y/">Classifiche</a></h4>
          <div>14:00 BFF Academy U19 - Thimphu FC <a href="/partita/a/"> - </a></div>
          <h4>NORVEGIA: Division 3 - Group 4 <a href="/classifiche/x/y/">Classifiche</a></h4>
          <div>00:30 Haugesund 2 - Hinna <a href="/partita/b/">2-4</a></div>
          <div>18:00 Rinviata Team A - Team B <a href="/partita/c/"> - </a></div>
          </div>
        </body></html>
        """
        rows = parse_mobile(page)
        self.assertEqual(3, len(rows))
        self.assertEqual(("BHUTAN", "Premier League"), (rows[0].country, rows[0].league))
        self.assertEqual(("BFF Academy U19", "Thimphu FC"), (rows[0].home, rows[0].away))
        self.assertEqual("-", rows[0].score)
        self.assertEqual("2-4", rows[1].score)
        self.assertTrue(rows[1].borderline)
        self.assertEqual("Rinviata", rows[2].status)


class LeagueGenderMappingTest(unittest.TestCase):
    def setUp(self):
        self.registry = [
            RegistryRow("Italy_SerieA", "Italy", "Serie A"),
            RegistryRow("Italy_SerieAWomen", "Italy", "Serie A Femminile"),
            RegistryRow("Italy_SerieB", "Italy", "Serie B"),
        ]

    def test_serie_a_women_maps_to_women_registry(self):
        self.assertEqual(
            "Italy_SerieAWomen",
            resolve(self.registry, "Italy", "Serie A Women"),
        )

    def test_unregistered_women_league_never_falls_back_to_male(self):
        self.assertIsNone(resolve(self.registry, "Italy", "Serie B Women"))

    def test_male_serie_a_is_unchanged(self):
        self.assertEqual("Italy_SerieA", resolve(self.registry, "Italy", "Serie A"))

    def test_generic_male_league_rejects_female_teams(self):
        self.assertIsNone(
            resolve_match(self.registry, "Italy", "Serie A", "Juventus D", "Roma D")
        )

    def test_generic_senior_league_rejects_youth_teams(self):
        registry = [RegistryRow("England_PremierLeague", "England", "Premier League")]
        self.assertIsNone(
            resolve_match(registry, "England", "Premier League", "Chelsea U21", "Arsenal U21")
        )

    def test_senior_match_is_unchanged(self):
        self.assertEqual(
            "Italy_SerieA",
            resolve_match(self.registry, "Italy", "Serie A", "Juventus", "Roma"),
        )


if __name__ == "__main__":
    unittest.main()
