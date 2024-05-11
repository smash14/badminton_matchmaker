import unittest
from teamsParser import Teams
from datetime import datetime


class TestStringMethods(unittest.TestCase):

    def test_plan_types_variables(self):
        self.MatchPlanEmpty = Teams()
        self.assertEqual(type(self.MatchPlanEmpty.teams), dict, "teams are not a dict")

    def test_add_team_to_empty_plan(self):
        self.MatchPlanEmpty = Teams()
        self.MatchPlanEmpty.add_team("teamtest01")
        self.assertEqual(type(self.MatchPlanEmpty.teams), dict, "teams are not a dict")
        try:
            available_dates_home_matches = self.MatchPlanEmpty.teams["teamtest01"]["available_dates_home_matches"]
            blocked_dates_matches = self.MatchPlanEmpty.teams["teamtest01"]["blocked_dates_matches"]
            please_dont_play_dates = self.MatchPlanEmpty.teams["teamtest01"]["please_dont_play_dates"]
        except Exception:
            self.fail('unexpected exception raised')
        self.assertEqual(type(available_dates_home_matches), list, "available_dates_home_matches is not a list")
        self.assertEqual(type(blocked_dates_matches), list, "blocked_dates_matches is not a list")
        self.assertEqual(type(please_dont_play_dates), list, "please_dont_play_dates is not a list")

    def test_add_date_wrong_format(self):
        self.MatchPlanEmpty = Teams()
        testdatetime = datetime.now()
        self.assertRaises(TypeError, self.MatchPlanEmpty.add_home_match_date, "TeamNotExist", "2024-04-04")
        self.assertRaises(KeyError, self.MatchPlanEmpty.add_home_match_date, "TeamNotExist", testdatetime)

    def test_sample_match_plan_01(self):
        date_home_match_team = datetime(2021, 2, 19)
        date_blocked_match_team = datetime(2020, 5, 22)
        date_unwanted_match_team = datetime(1999, 9, 10)
        date_blocked_match_general = datetime(2019, 1, 17)
        date_start_date_first_round = datetime(2000, 1, 17)
        date_end_date_first_round = datetime(2001, 8, 30)
        date_start_date_second_round = datetime(2001, 1, 1)
        self.MatchPlanEmpty = Teams()
        self.assertRaises(KeyError, self.MatchPlanEmpty.remove_team, "TeamNotExist")
        self.MatchPlanEmpty.add_team("DreamTeam")
        self.MatchPlanEmpty.add_home_match_date("DreamTeam", date_home_match_team)
        self.MatchPlanEmpty.add_blocked_match_date("DreamTeam", date_blocked_match_team)
        self.MatchPlanEmpty.add_unwanted_match_date("DreamTeam", date_unwanted_match_team)
        self.MatchPlanEmpty.add_general_blocked_date(date_blocked_match_general)
        self.MatchPlanEmpty.set_start_date_first_round(date_start_date_first_round)
        self.MatchPlanEmpty.set_end_date_first_round(date_end_date_first_round)
        self.MatchPlanEmpty.set_start_date_second_round(date_start_date_second_round)
        self.MatchPlanEmpty.save_settings_file("testdata/test_sample_match_plan_01.json")

        with open("testdata/test_sample_match_plan_01.json") as file:
            file_to_test = file.read()
        with open("testdata/test_sample_match_plan_01.ref.json") as file:
            file_ref = file.read()
        self.assertEqual(file_to_test, file_ref)

    def test_get_all_teams(self):
        self.MatchPlanEmpty = Teams()
        self.MatchPlanEmpty.add_team("DreamTeam")
        self.MatchPlanEmpty.add_team("BadTeam")
        self.MatchPlanEmpty.add_team("YetAnotherTeam")
        all_teams = self.MatchPlanEmpty.get_all_teams()
        expected_teams = ["DreamTeam", "BadTeam", "YetAnotherTeam"]
        self.assertEqual(all_teams, expected_teams)




if __name__ == '__main__':
    unittest.main()
