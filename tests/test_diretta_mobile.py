import unittest

from tools.diretta_mobile import parse_mobile


class DirettaMobileParserTest(unittest.TestCase):
    def test_scheduled_and_finished_matches(self):
        page = """
        <html><body>
          <h4>BHUTAN: Premier League <a href="/classifiche/x/y/">Classifiche</a></h4>
          <div>14:00 BFF Academy U19 - Thimphu FC <a href="/partita/a/"> - </a></div>
          <h4>NORVEGIA: Division 3 - Group 4 <a href="/classifiche/x/y/">Classifiche</a></h4>
          <div>00:30 Haugesund 2 - Hinna <a href="/partita/b/">2-4</a></div>
          <div>18:00 Rinviata Team A - Team B <a href="/partita/c/"> - </a></div>
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


if __name__ == "__main__":
    unittest.main()
