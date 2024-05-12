import sys
import json
import datetime
from utils import convert_date_string_to_datetime, convert_date_string_list_to_datetime,\
    convert_datetime_list_to_string, convert_datetime_to_string


class Teams:
    def __init__(self, path_to_teams_file=None):
        self.max_iterations = 99
        self.return_on_first_match_plan = False
        self.start_date_first_round = None
        self.end_date_first_round = None
        self.start_date_second_round = None
        self.general_blocked_dates = []
        self.consecutive_matches = {'allow': 1, 'probability': 50}
        self.shuffle_matches = {'allow': 1, 'shuffle_part': 0.4}
        self.weight = {
            'amount_consecutive_matches': 1,
            'distribution_game_days': 100,
            'amount_please_dont_play_dates': 10,
            'distribution_home_away_matches': 1
        }
        self.teams = {}
        if path_to_teams_file is not None:
            self.open_and_parse_settings_file(path_to_teams_file)

    def open_and_parse_settings_file(self, path_to_file):
        try:
            with open(path_to_file) as file:
                file_contents = file.read()
        except FileNotFoundError:
            print(f"Fehler, konnte Datei {path_to_file} nicht finden")
            return False

        try:
            parsed_json = json.loads(file_contents)
            self.max_iterations = parsed_json['max_iterations']
            self.return_on_first_match_plan = parsed_json['return_on_first_match_plan']
            self.start_date_first_round = convert_date_string_to_datetime(parsed_json['start_date_first_round'])
            self.start_date_second_round = convert_date_string_to_datetime(parsed_json['start_date_second_round'])
            self.end_date_first_round = convert_date_string_to_datetime(parsed_json['end_date_first_round'])
            teams_json = parsed_json['teams']
            for team in teams_json:
                self.teams[team] = {}
                self.teams[team]['available_dates_home_matches'] =\
                    convert_date_string_list_to_datetime(teams_json[team]['available_dates_home_matches'])
                self.teams[team]['blocked_dates_matches'] = \
                    convert_date_string_list_to_datetime(teams_json[team]['blocked_dates_matches'])
                self.teams[team]['please_dont_play_dates'] = \
                    convert_date_string_list_to_datetime(teams_json[team]['please_dont_play_dates'])
            self.weight = parsed_json['weight']

            self.general_blocked_dates = parsed_json['general_blocked_dates']
            self.consecutive_matches = {'allow': parsed_json['consecutive_matches']['allow'],
                                        'probability': parsed_json['consecutive_matches']['probability']}
            self.shuffle_matches = {'allow': parsed_json['shuffle_matches']['allow'],
                                    'shuffle_part': parsed_json['shuffle_matches']['shuffle_part']}
            if self.max_iterations == 0:
                self.max_iterations = sys.maxsize
        except Exception as e:
            print("Fehler beim Verarbeiten der teams.json Datei mit folgender Fehlermeldung:")
            print("")
            print(e)
            return False

    def save_settings_file(self, path_to_file):
        export_plan = {}
        export_plan['max_iterations'] = self.max_iterations
        export_plan['return_on_first_match_plan'] = self.return_on_first_match_plan
        export_plan['start_date_first_round'] = convert_datetime_to_string(self.start_date_first_round)
        export_plan['end_date_first_round'] = convert_datetime_to_string(self.end_date_first_round)
        export_plan['start_date_second_round'] = convert_datetime_to_string(self.start_date_second_round)
        export_plan['general_blocked_dates'] = convert_datetime_list_to_string(self.general_blocked_dates)
        export_plan['consecutive_matches'] = self.consecutive_matches
        export_plan['shuffle_matches'] = self.shuffle_matches
        export_plan['weight'] = self.weight
        export_plan['teams'] = {}
        for team in self.teams:
            export_plan['teams'][team] = {}
            export_plan['teams'][team]['available_dates_home_matches'] = \
                convert_datetime_list_to_string(self.teams[team]['available_dates_home_matches'])
            export_plan['teams'][team]['blocked_dates_matches'] = \
                convert_datetime_list_to_string(self.teams[team]['blocked_dates_matches'])
            export_plan['teams'][team]['please_dont_play_dates'] = \
                convert_datetime_list_to_string(self.teams[team]['please_dont_play_dates'])
        json_object = json.dumps(export_plan, indent=2)
        with open(path_to_file, "w") as outfile:
            outfile.write(json_object)

    def set_start_date_first_round(self, date):
        self.start_date_first_round = date

    def set_start_date_second_round(self, date):
        self.start_date_second_round = date

    def set_end_date_first_round(self, date):
        self.end_date_first_round = date

    def add_general_blocked_date(self, date):
        if not type(date) is datetime.datetime:
            raise TypeError(f"incorrect date type. Expected datetime, got: {type(date)}")
        self.general_blocked_dates.append(date)

    def remove_general_blocked_date(self, date):
        if not type(date) is datetime.datetime:
            raise TypeError(f"incorrect date type. Expected datetime, got: {type(date)}")
        try:
            self.general_blocked_dates.remove(date)
        except ValueError:
            pass

    def add_team(self, team_name):
        self.teams[team_name] = {
            "available_dates_home_matches": [],
            "blocked_dates_matches": [],
            "please_dont_play_dates": []
        }

    def remove_team(self, team_name):
        self.teams.pop(team_name)

    def get_all_teams(self):
        list_of_all_teams = []
        for team in self.teams:
            list_of_all_teams.append(team)
        return list_of_all_teams

    def add_home_match_date(self, team_name, date):
        if not type(date) is datetime.datetime:
            raise TypeError(f"incorrect date type. Expected datetime, got: {type(date)}")
        try:
            self.teams[team_name]["available_dates_home_matches"].append(date)
        except KeyError:
            raise KeyError(f"{team_name} is not available")

    def remove_home_match_date(self, team_name, date):
        if not type(date) is datetime.datetime:
            raise TypeError(f"incorrect date type. Expected datetime, got: {type(date)}")
        try:
            self.teams[team_name]["available_dates_home_matches"].remove(date)
        except KeyError:
            raise KeyError(f"{team_name} or {date} is not available")

    def show_all_home_match_dates(self, team_name, show_as_string=True):
        home_match_dates = []
        try:
            for home_match_date in self.teams[team_name]['available_dates_home_matches']:
                if show_as_string:
                    home_match_dates.append(convert_datetime_to_string(home_match_date))
                else:
                    home_match_dates.append(home_match_date)
        except KeyError:
            pass
        return home_match_dates

    def add_blocked_match_date(self, team_name, date):
        if not type(date) is datetime.datetime:
            raise TypeError(f"incorrect date type. Expected datetime, got: {type(date)}")
        try:
            self.teams[team_name]["blocked_dates_matches"].append(date)
        except KeyError:
            raise KeyError(f"{team_name} is not available")

    def remove_blocked_match_date(self, team_name, date):
        if not type(date) is datetime.datetime:
            raise TypeError(f"incorrect date type. Expected datetime, got: {type(date)}")
        try:
            self.teams[team_name]["blocked_dates_matches"].remove(date)
        except KeyError:
            raise KeyError(f"{team_name} or {date} is not available")

    def show_all_blocked_match_dates(self, team_name, show_as_string=True):
        blocked_match_dates = []
        try:
            for blocked_match_date in self.teams[team_name]['blocked_dates_matches']:
                if show_as_string:
                    blocked_match_dates.append(convert_datetime_to_string(blocked_match_date))
                else:
                    blocked_match_dates.append(blocked_match_date)
        except KeyError:
            pass
        return blocked_match_dates

    def add_unwanted_match_date(self, team_name, date):
        if not type(date) is datetime.datetime:
            raise TypeError(f"incorrect date type. Expected datetime, got: {type(date)}")
        try:
            self.teams[team_name]["please_dont_play_dates"].append(date)
        except KeyError:
            raise KeyError(f"{team_name} is not available")

    def remove_unwanted_match_date(self, team_name, date):
        if not type(date) is datetime:
            raise TypeError(f"incorrect date type. Expected datetime, got: {type(date)}")
        try:
            self.teams[team_name]["please_dont_play_dates"].remove(date)
        except KeyError:
            raise KeyError(f"{team_name} or {date} is not available")

    def show_all_unwanted_match_dates(self, team_name, show_as_string=True):
        unwanted_match_dates = []
        try:
            for unwanted_match_date in self.teams[team_name]['please_dont_play_dates']:
                if show_as_string:
                    unwanted_match_dates.append(convert_datetime_to_string(unwanted_match_date))
                else:
                    unwanted_match_dates.append(unwanted_match_date)
        except KeyError:
            pass
        return unwanted_match_dates



