import unittest
from teamsParser import Teams
from datetime import datetime
from utils import return_clean_stdout_text


class TestUtilsMethods(unittest.TestCase):

    def test_clean_stdout_return(self):
        sample_1 = "Standard Text\\r\\nMit Unterbrechung\\r\\n"
        return_1_obs = return_clean_stdout_text(sample_1)
        return_1_exp = ['Standard Text', 'Mit Unterbrechung']
        self.assertEqual(return_1_obs, return_1_exp, "Lists are not the same")

        sample_2 = "Standard Text\\r\\nRUN:50\\r\\n"
        return_2_obs = return_clean_stdout_text(sample_2)
        return_2_exp = ['Standard Text', 'RUN:50']
        self.assertEqual(return_2_obs, return_2_exp, "Lists are not the same")



class TestMatchPlanMethods(unittest.TestCase):

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

    def test_get_all_match_dates(self):
        self.MatchPlan = Teams("testdata/teams.json")
        home_match_dates = self.MatchPlan.show_all_home_match_dates('Oldesloe')
        expected_dates = ["2023-09-23", "2023-10-01", "2023-11-05", "2023-11-11", "2023-11-19", "2023-12-03",
                          "2023-12-09", "2024-01-27", "2024-02-12"]
        self.assertEqual(home_match_dates, expected_dates)

        blocked_match_dates = self.MatchPlan.show_all_blocked_match_dates('Luebeck')
        expected_dates = ["2023-09-02", "2023-09-03", "2023-09-09", "2023-09-10", "2023-09-30", "2023-10-01",
                          "2023-11-11", "2023-11-12"]
        self.assertEqual(blocked_match_dates, expected_dates)

        unwanted_match_dates = self.MatchPlan.show_all_unwanted_match_dates('Schwarzenbek/Buechen/Muessen')
        expected_dates = ["2023-09-16", "2023-09-17", "2023-09-30", "2023-10-01", "2023-10-08", "2023-10-28",
                          "2023-10-29", "2023-11-04", "2023-03-10"]
        self.assertEqual(unwanted_match_dates, expected_dates)

    def test_remove_team_01(self):
        self.MatchPlan = Teams("testdata/teams.json")
        self.MatchPlan.remove_team('Luebeck')

        self.MatchPlan.save_settings_file("testdata/test_remove_team_01.json")
        with open("testdata/test_remove_team_01.json") as file:
            file_to_test = file.read()
        with open("testdata/test_remove_team_01.ref.json") as file:
            file_ref = file.read()
        self.assertEqual(file_to_test, file_ref)

    def test_sort_lists_01(self):
        self.MatchPlan = Teams("testdata/test_sort_lists_unsorted_01.ref.json")
        self.MatchPlan.save_settings_file("testdata/test_sort_lists_sorted_01.json")
        with open("testdata/test_sort_lists_sorted_01.json") as file:
            file_to_test = file.read()
        with open("testdata/test_sort_lists_sorted_01.ref.json") as file:
            file_ref = file.read()
        self.assertEqual(file_to_test, file_ref)


if __name__ == '__main__':
    unittest.main()
