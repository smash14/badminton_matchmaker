import os
import sys
import json
import datetime
import logging
from utils import convert_date_string_to_datetime, convert_date_string_list_to_datetime,\
    convert_datetime_list_to_string, convert_datetime_to_string

logger = logging.getLogger(__name__)


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
            logging.error(f"Fehler, konnte Datei {path_to_file} nicht finden")
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

            self.general_blocked_dates = convert_date_string_list_to_datetime(parsed_json['general_blocked_dates'])
            self.consecutive_matches = {'allow': parsed_json['consecutive_matches']['allow'],
                                        'probability': parsed_json['consecutive_matches']['probability']}
            self.shuffle_matches = {'allow': parsed_json['shuffle_matches']['allow'],
                                    'shuffle_part': parsed_json['shuffle_matches']['shuffle_part']}
            if self.max_iterations == 0:
                self.max_iterations = sys.maxsize
            self._sort_all_datetime_lists()
        except Exception as e:
            logging.error(f"Fehler beim Verarbeiten der teams.json Datei mit folgender Fehlermeldung: {e}")
            return False
        return True

    def save_settings_file(self, path_to_file):
        try:
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
                logging.info(f"Settings File written to {path_to_file}")
                return True
        except Exception as e:
            logging.error(f"Error while saving settings file: {e}")
            return False

    @staticmethod
    def remove_settings_file(path_to_file):
        try:
            os.remove(path_to_file)
            logging.info(f"File '{path_to_file}' deleted successfully before creating a new one.")
        except FileNotFoundError:
            logging.warning(f"File '{path_to_file}' not found.")
        except OSError as e:
            logging.error("Error deleting old file: %s - %s." % (e.filename, e.strerror))

    @staticmethod
    def check_for_settings_file(path_to_file):
        return os.path.exists(path_to_file)

    def set_start_date_first_round(self, date):
        if date is None or date == "":
            self.start_date_first_round = None
        else:
            self.start_date_first_round = date

    def set_start_date_second_round(self, date):
        if date is None or date == "":
            self.start_date_second_round = None
        else:
            self.start_date_second_round = date

    def set_end_date_first_round(self, date):
        if date is None or date == "":
            self.end_date_first_round = None
        else:
            self.end_date_first_round = date

    def add_general_blocked_date(self, date):
        if not type(date) is datetime.datetime:
            logging.error(f"add general blocked date: incorrect date type. Expected datetime, got: {type(date)}")
            return
        if date not in self.general_blocked_dates:
            self.general_blocked_dates.append(date)
            self._sort_all_datetime_lists()

    def remove_general_blocked_date(self, date):
        if not type(date) is datetime.datetime:
            logging.error(f"remove general blocked date: incorrect date type. Expected datetime, got: {type(date)}")
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
        if team_name is None:
            return
        if not type(date) is datetime.datetime:
            logging.error(f"add home match date: incorrect date type. Expected datetime, got: {type(date)}")
            return
        try:
            if date not in self.teams[team_name]["available_dates_home_matches"]:
                self.teams[team_name]["available_dates_home_matches"].append(date)
                self._sort_all_datetime_lists()
        except KeyError:
            logging.error(f"add home match date: {team_name} is not available")
            return

    def remove_home_match_date(self, team_name, date):
        if not type(date) is datetime.datetime:
            raise TypeError(f"remove home match date: Incorrect date type. Expected datetime, got: {type(date)}")
        try:
            self.teams[team_name]["available_dates_home_matches"].remove(date)
        except KeyError:
            raise KeyError(f"{team_name} or {date} is not available")
        self._sort_all_datetime_lists()

    def get_all_home_match_dates(self, team_name, show_as_string=True, date_format='%Y-%m-%d'):
        home_match_dates = []
        if team_name is None:
            return home_match_dates
        if team_name not in self.teams:
            logger.error(f'Trying to show home match dates for team that does not exist: {team_name}')
            return home_match_dates
        for home_match_date in self.teams[team_name]['available_dates_home_matches']:
            if show_as_string:
                home_match_dates.append(convert_datetime_to_string(home_match_date, date_format))
            else:
                home_match_dates.append(home_match_date)
        return home_match_dates

    def get_all_general_blocked_dates(self, show_as_string=True, date_format='%Y-%m-%d'):
        general_blocked_dates = []
        for blocked_date in self.general_blocked_dates:
            if show_as_string:
                general_blocked_dates.append(convert_datetime_to_string(blocked_date, date_format))
            else:
                general_blocked_dates.append(blocked_date)
        return general_blocked_dates

    def add_blocked_match_date(self, team_name, date):
        if team_name is None:
            return
        if not type(date) is datetime.datetime:
            logging.error(f"add blocked date: Incorrect date type. Expected datetime, got: {type(date)}")
            return
        try:
            if date not in self.teams[team_name]["blocked_dates_matches"]:
                self.teams[team_name]["blocked_dates_matches"].append(date)
                self._sort_all_datetime_lists()
        except KeyError:
            logging.error(f"add blocked date: {team_name} is not available")
            return

    def remove_blocked_match_date(self, team_name, date):
        if not type(date) is datetime.datetime:
            raise TypeError(f"incorrect date type. Expected datetime, got: {type(date)}")
        try:
            self.teams[team_name]["blocked_dates_matches"].remove(date)
        except KeyError:
            raise KeyError(f"{team_name} or {date} is not available")
        self._sort_all_datetime_lists()

    def show_all_blocked_match_dates(self, team_name, show_as_string=True, date_format='%Y-%m-%d'):
        blocked_match_dates = []
        try:
            for blocked_match_date in self.teams[team_name]['blocked_dates_matches']:
                if show_as_string:
                    blocked_match_dates.append(convert_datetime_to_string(blocked_match_date, date_format))
                else:
                    blocked_match_dates.append(blocked_match_date)
        except KeyError:
            pass
        return blocked_match_dates

    def add_unwanted_match_date(self, team_name, date):
        if team_name is None:
            return
        if not type(date) is datetime.datetime:
            logging.error(f"add unwanted match date: incorrect date type. Expected datetime, got: {type(date)}")
            return
        try:
            if date not in self.teams[team_name]["please_dont_play_dates"]:
                self.teams[team_name]["please_dont_play_dates"].append(date)
                self._sort_all_datetime_lists()
        except KeyError:
            logging.error(f"{team_name} is not available")
            return

    def remove_unwanted_match_date(self, team_name, date):
        if not type(date) is datetime.datetime:
            raise TypeError(f"incorrect date type. Expected datetime, got: {type(date)}")
        try:
            self.teams[team_name]["please_dont_play_dates"].remove(date)
        except KeyError:
            raise KeyError(f"{team_name} or {date} is not available")
        self._sort_all_datetime_lists()

    def show_all_unwanted_match_dates(self, team_name, show_as_string=True, date_format='%Y-%m-%d'):
        unwanted_match_dates = []
        try:
            for unwanted_match_date in self.teams[team_name]['please_dont_play_dates']:
                if show_as_string:
                    unwanted_match_dates.append(convert_datetime_to_string(unwanted_match_date, date_format))
                else:
                    unwanted_match_dates.append(unwanted_match_date)
        except KeyError:
            pass
        return unwanted_match_dates

    def _sort_all_datetime_lists(self):
        self.general_blocked_dates.sort()
        for team in self.teams:
            self.teams[team]['available_dates_home_matches'].sort()
            self.teams[team]['blocked_dates_matches'].sort()
            self.teams[team]['please_dont_play_dates'].sort()




