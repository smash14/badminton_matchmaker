import unittest
from teamsParser import Teams

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.MatchPlanEmpty = Teams()

    def test_plan_types_variables(self):
        self.MatchPlanEmpty = Teams()
        self.assertEqual(type(self.MatchPlanEmpty.teams_json), dict, "teams are not a dict")

    def test_add_team_to_empty_plan(self):
        self.MatchPlanEmpty.add_team("teamtest01")
        self.assertEqual(type(self.MatchPlanEmpty.teams_json), dict, "teams are not a dict")
        try:
            available_dates_home_matches = self.MatchPlanEmpty.teams_json["teamtest01"]["available_dates_home_matches"]
            blocked_dates_matches = self.MatchPlanEmpty.teams_json["teamtest01"]["blocked_dates_matches"]
            please_dont_play_dates = self.MatchPlanEmpty.teams_json["teamtest01"]["please_dont_play_dates"]
        except Exception:
            self.fail('unexpected exception raised')
        self.assertEqual(type(available_dates_home_matches), list, "available_dates_home_matches is not a list")
        self.assertEqual(type(blocked_dates_matches), list, "blocked_dates_matches is not a list")
        self.assertEqual(type(please_dont_play_dates), list, "please_dont_play_dates is not a list")


if __name__ == '__main__':
    unittest.main()