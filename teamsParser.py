import sys
import json
import datetime


class Teams:
    def __init__(self, path_to_teams_file=None):
        self.teams_json = []
        self.weight = 0
        self.start_date_first_round = datetime.datetime(1970, 1, 1)
        self.start_date_second_round = datetime.datetime(1970, 1, 1)
        self.end_date_first_round = datetime.datetime(1970, 1, 1)
        self.general_blocked_dates = []
        self.allow_consecutive_matches = True
        self.allow_shuffle_matches = True
        self.iterations = 99
        self.return_on_first_match_plan = True
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
            self.teams_json = parsed_json['teams']
            self.weight = parsed_json['weight']
            self.start_date_first_round = parsed_json['start_date_first_round']
            self.start_date_second_round = parsed_json['start_date_second_round']
            self.end_date_first_round = parsed_json['end_date_first_round']
            self.general_blocked_dates = parsed_json['general_blocked_dates']
            self.allow_consecutive_matches = [parsed_json['consecutive_matches']['allow'],
                                         parsed_json['consecutive_matches']['probability']]
            self.allow_shuffle_matches = [parsed_json['shuffle_matches']['allow'],
                                     parsed_json['shuffle_matches']['shuffle_part']]
            self.iterations = parsed_json['max_iterations']
            if self.iterations == 0:
                self.iterations = sys.maxsize
            self.return_on_first_match_plan = parsed_json['return_on_first_match_plan']
        except Exception as e:
            print("Fehler beim Verarbeiten der teams.json Datei mit folgender Fehlermeldung:")
            print("")
            print(e)
            input("Druecke eine Taste um zu Beenden ...")
            sys.exit(1)

