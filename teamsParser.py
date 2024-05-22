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
        self.max_iterations = 10000
        self.return_on_first_match_plan = False
        self.start_date_first_round = None
        self.end_date_first_round = None
        self.start_date_second_round = None
        self.general_blocked_dates = []
        self.consecutive_matches = {'allow': 1, 'probability': 50}
        self.shuffle_matches = {'allow': 1, 'shuffle_part': 0.5}
        self.weight = {
            'amount_consecutive_matches': 1,
            'distribution_game_days': 2,
            'amount_please_dont_play_dates': 1,
            'distribution_home_away_matches': 2
        }
        self.teams = {}
        if path_to_teams_file is not None:
            self.open_and_parse_settings_file(path_to_teams_file)
        logging.info(f"class init finished ")

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

    def set_max_iterations(self, max_iterations):
        if type(max_iterations) is not int:
            logging.error(f"set_max_iterations: Expected type int, got {type(max_iterations)}: {max_iterations}")
            return False
        if max_iterations > sys.maxsize:
            max_iterations = sys.maxsize
        self.max_iterations = max_iterations
        logging.info(f"set max_iterations to {max_iterations}")
        return True

    def set_return_on_first_match_plan(self, return_on_first_match_plan):
        if type(return_on_first_match_plan) is not bool:
            logging.error(f"set_return_on_first_match_plan: Expected type bool,"
                          f" got {type(return_on_first_match_plan)}: {return_on_first_match_plan}")
            return False
        self.return_on_first_match_plan = return_on_first_match_plan
        logging.info(f"set return_on_first_match_plan to {return_on_first_match_plan}")
        return True

    def set_settings_consecutive_matches(self, allow_bool, probability):
        if type(allow_bool) is not bool:
            logging.error(f"set_consecutive_match: Expected type bool, got {type(allow_bool)}: {allow_bool}")
            return False
        if type(probability) is not int:
            logging.error(f"set_consecutive_match: Expected type int, got {type(probability)}: {probability}")
            return False
        if allow_bool:
            allow = 1
        else:
            allow = 0
        self.consecutive_matches = {
            'allow': allow,
            'probability': probability
        }
        logging.info(f"set consecutive_matches to {allow}, {probability}")
        return True

    def set_settings_shuffle_matches(self, allow_bool, shuffle_part):
        if type(allow_bool) is not bool:
            logging.error(f"set_settings_shuffle_matches: Expected type bool, got {type(allow_bool)}: {allow_bool}")
            return False
        if type(shuffle_part) is not float:
            logging.error(f"set_settings_shuffle_matches: Expected type float, got {type(shuffle_part)}: {shuffle_part}")
            return False
        if allow_bool:
            allow = 1
        else:
            allow = 0
        if shuffle_part > 1.0:
            shuffle_part = 1.0
        if shuffle_part < 0.1:
            shuffle_part = 0.1
        self.shuffle_matches = {
            'allow': allow,
            'shuffle_part': shuffle_part
        }
        logging.info(f"set shuffle_matches to {allow}, {shuffle_part}")
        return True

    def set_settings_weight(self, amount_consecutive_matches, distribution_game_days, amount_please_dont_play_dates,
                            distribution_home_away_matches):
        if type(amount_consecutive_matches) is not int:
            logging.error(f"set_settings_weight: Expected type int,"
                          f" got {type(amount_consecutive_matches)}: {amount_consecutive_matches}")
            return False
        if type(distribution_game_days) is not int:
            logging.error(f"set_settings_weight: Expected type int,"
                          f" got {type(distribution_game_days)}: {distribution_game_days}")
            return False
        if type(amount_please_dont_play_dates) is not int:
            logging.error(f"set_settings_weight: Expected type int,"
                          f" got {type(amount_please_dont_play_dates)}: {amount_please_dont_play_dates}")
            return False
        if type(distribution_home_away_matches) is not int:
            logging.error(f"set_settings_weight: Expected type int,"
                          f" got {type(distribution_home_away_matches)}: {distribution_home_away_matches}")
            return False

        self.weight = {
            'amount_consecutive_matches': amount_consecutive_matches,
            'distribution_game_days': distribution_game_days,
            'amount_please_dont_play_dates': amount_please_dont_play_dates,
            'distribution_home_away_matches': distribution_home_away_matches
        }
        logging.info(f"set weight to amount_consecutive_matches: {amount_consecutive_matches},"
                     f"distribution_game_days: {distribution_game_days}, "
                     f"amount_please_dont_play_dates: {amount_please_dont_play_dates},"
                     f"distribution_home_away_matches: {distribution_home_away_matches}")
        return True

    def set_start_date_first_round(self, date):
        if date is None or date == "":
            self.start_date_first_round = None
            return True
        if not type(date) is datetime.datetime:
            logging.error(f"set_start_date_first_round: Expected datetime, got: {type(date)}, {date}")
            return False
        self.start_date_first_round = date
        logging.info(f"set start_date_first_round to {date}")
        return True

    def set_start_date_second_round(self, date):
        if date is None or date == "":
            self.start_date_second_round = None
            return True
        if not type(date) is datetime.datetime:
            logging.error(f"set_start_date_second_round: Expected datetime, got: {type(date)}, {date}")
            return False
        self.start_date_second_round = date
        logging.info(f"set start_date_second_round to {date}")
        return True

    def set_end_date_first_round(self, date):
        if date is None or date == "":
            self.end_date_first_round = None
            return True
        if not type(date) is datetime.datetime:
            logging.error(f"set_end_date_first_round: Expected datetime, got: {type(date)}, {date}")
            return False
        self.end_date_first_round = date
        logging.info(f"set end_date_first_round to {date}")
        return True

    def add_general_blocked_date(self, date):
        if not type(date) is datetime.datetime:
            logging.error(f"add general blocked date: incorrect date type. Expected datetime, got: {type(date)}")
            return
        if date not in self.general_blocked_dates:
            self.general_blocked_dates.append(date)
            logging.info(f"add general blocked date: {date}")
            self._sort_all_datetime_lists()

    def remove_general_blocked_date(self, date):
        if not type(date) is datetime.datetime:
            logging.error(f"remove general blocked date: incorrect date type. Expected datetime, got: {type(date)}")
        try:
            self.general_blocked_dates.remove(date)
            logging.info(f"remove general blocked date: {date}")
        except ValueError:
            logging.warning(f"could not find {date} in general blocked date")
            pass

    def add_team(self, team_name):
        self.teams[team_name] = {
            "available_dates_home_matches": [],
            "blocked_dates_matches": [],
            "please_dont_play_dates": []
        }
        logging.info(f"add new team: {team_name}")

    def remove_team(self, team_name):
        try:
            self.teams.pop(team_name)
            logging.info(f"remove team {team_name}")
            return True
        except KeyError:
            logging.error(f"Could not remove team {team_name}, not in list")
            return False

    def get_all_teams(self):
        list_of_all_teams = []
        for team in self.teams:
            list_of_all_teams.append(team)
        return list_of_all_teams

    def add_home_match_date(self, team_name, date):
        if team_name is None:
            logging.warning("add_home_match_date: team_name is None")
            return False
        if type(team_name) is not str:
            logging.error(f"add_home_match_date: Expected string, got: {type(team_name)}, {team_name}")
            return False
        if not type(date) is datetime.datetime:
            logging.error(f"add_home_match_date: Expected datetime, got: {type(date)}, {date}")
            return False
        try:
            if date not in self.teams[team_name]["available_dates_home_matches"]:
                self.teams[team_name]["available_dates_home_matches"].append(date)
                self._sort_all_datetime_lists()
                logging.info(f"add home match date for {team_name}: {date}")
                return True
        except KeyError:
            logging.error(f"add_home_match_date: {team_name} is not available")
            return False

    def remove_home_match_date(self, team_name, date):
        if not type(date) is datetime.datetime:
            logging.error(f"remove_home_match_date: Expected datetime, got: {type(date)}, {date}")
            return False
        try:
            self.teams[team_name]["available_dates_home_matches"].remove(date)
        except KeyError:
            logging.error(f"remove_home_match_date: {team_name} or {date} is not available")
            return False
        logging.info(f"remove home match date for {team_name}: {date}")
        self._sort_all_datetime_lists()
        return True

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
            logging.error("add_blocked_match_date: team_name is None")
            return False
        if type(team_name) is not str:
            logging.error(f"add_blocked_match_date: Expected string, got: {type(team_name)}, {team_name}")
            return False
        if not type(date) is datetime.datetime:
            logging.error(f"add_blocked_date: Expected datetime, got: {type(date)}, {date}")
            return False
        try:
            if date not in self.teams[team_name]["blocked_dates_matches"]:
                self.teams[team_name]["blocked_dates_matches"].append(date)
                self._sort_all_datetime_lists()
                logging.info(f"add blocked match date for {team_name}: {date}")
                return True
        except KeyError:
            logging.error(f"add blocked date: {team_name} is not available")
            return False

    def remove_blocked_match_date(self, team_name, date):
        if not type(date) is datetime.datetime:
            logging.error(f"remove_blocked_match. Expected datetime, got: {type(date)}, {date}")
            return False
        try:
            self.teams[team_name]["blocked_dates_matches"].remove(date)
        except KeyError:
            logging.error(f"remove_blocked_date {team_name} or {date} is not available")
            return False
        self._sort_all_datetime_lists()
        logging.info(f"remove blocked match date for {team_name}: {date}")
        return True

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
            logging.warning("add_unwanted_match_date: team_name is None")
            return False
        if type(team_name) is not str:
            logging.error(f"add_unwanted_match_date: Expected string, got: {type(team_name)}, {team_name}")
            return False
        if not type(date) is datetime.datetime:
            logging.error(f"add_unwanted_match_date: Expected datetime, got: {type(date)}, {date}")
            return False
        try:
            if date not in self.teams[team_name]["please_dont_play_dates"]:
                self.teams[team_name]["please_dont_play_dates"].append(date)
                self._sort_all_datetime_lists()
                logging.info(f"add unwanted match date for {team_name}: {date}")
                return True
        except KeyError:
            logging.error(f"add_unwanted_match_date: {team_name} is not available")
            return False

    def remove_unwanted_match_date(self, team_name, date):
        if not type(date) is datetime.datetime:
            logging.error(f"remove_unwanted_match_date: Expected datetime, got: {type(date)}, {date}")
        try:
            self.teams[team_name]["please_dont_play_dates"].remove(date)
        except KeyError:
            logging.error(f"remove_unwanted_match_date: {team_name} or {date} is not available")
            return False
        self._sort_all_datetime_lists()
        logging.info(f"remove unwanted match date for {team_name}: {date}")
        return True

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




