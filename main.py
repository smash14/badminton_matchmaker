import os.path

from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QFileDialog, QTableWidgetItem, QHeaderView
from main_window import Ui_MainWindow
from datetime import datetime
from utils import convert_qt_date_to_datetime, convert_date_string_to_datetime, return_clean_stdout_text, get_script_folder
import sys
import shutil
import logging
import pandas as pd
from teamsParser import Teams

logger = logging.getLogger(__name__)
EXPERT_SETTINGS_TAB = 2


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.today = datetime.today()
        script_path = get_script_folder()
        self.path_to_settings_json = os.path.join(script_path, "tools", "matchmaker_core", "bin", "teams.json")
        self.path_to_matchmaker_core = os.path.join(script_path, "tools", "matchmaker_core", "bin", "matchmaker_core.exe")
        self.path_to_matchplan_csv = os.path.join(script_path, "tools", "matchmaker_core", "bin", "spielplan.csv")
        print(f"Path to settings JSON file: {self.path_to_settings_json}")
        print(f"Path to matchmaker_core: {self.path_to_matchmaker_core}")
        print(f"Path to Match Plan: {self.path_to_matchplan_csv}")
        self.MatchPlan = Teams()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.display_date_format = '%d.%m.%Y'
        self.current_selection_team = None

        # TAB 00 - "Main Menu"
        self.ui.action_save_settings_file_as.triggered.connect(self.save_settings_file_as)
        self.ui.action_reset_settings_file.triggered.connect(self.reset_settings_file)
        self.ui.action_open_settings_file.triggered.connect(self.open_settings_file)

        # TAB 01 - "Globale Einstellungen"
        self.ui.checkBox_start_date_first_round_activate.clicked.connect(self.set_start_date_first_round)
        self.ui.dateEdit_start_date_first_round.dateChanged.connect(self.set_start_date_first_round)
        self.ui.checkBox_end_date_first_round_activate.clicked.connect(self.set_end_date_first_round)
        self.ui.dateEdit_end_date_first_round.dateChanged.connect(self.set_end_date_first_round)
        self.ui.checkBox_start_date_second_round_activate.clicked.connect(self.set_start_date_second_round)
        self.ui.dateEdit_start_date_second_round.dateChanged.connect(self.set_start_date_second_round)
        self.ui.pushButton_add_general_blocked_date.clicked.connect(self.add_general_blocked_date)
        self.ui.pushButton_remove_general_blocked_date.clicked.connect(self.remove_general_blocked_date)
        self.ui.dateEdit_general_blocked_dates.setDate(QDate(self.today.year, self.today.month, self.today.day))
        self.ui.checkBox_expert_settings.clicked.connect(self.show_expert_settings)

        # TAB 02 - "Mannschaften"
        # Set Date and Time to Date Edits
        self.ui.dateEdit_home_match_date.setDate(QDate(self.today.year, self.today.month, self.today.day))
        self.ui.dateEdit_blocked_match_date.setDate(QDate(self.today.year, self.today.month, self.today.day))
        self.ui.dateEdit_unwanted_match_date.setDate(QDate(self.today.year, self.today.month, self.today.day))

        # Connection if user clicks on teams
        self.ui.listWidget_teams.itemSelectionChanged.connect(self.update_selected_team)
        self.ui.pushButton_add_team.clicked.connect(self.add_team)
        self.ui.pushButton_remove_team.clicked.connect(self.remove_team)

        # Connection if user wants to add any match dates (home, blocked, unwanted)
        self.ui.pushButton_add_home_match_date.clicked.connect(self.add_home_match_date)
        self.ui.pushButton_remove_home_match_date.clicked.connect(self.remove_home_match_date)
        self.ui.pushButton_add_blocked_match_date.clicked.connect(self.add_blocked_match_date)
        self.ui.pushButton_remove_blocked_match_date.clicked.connect(self.remove_blocked_match_date)
        self.ui.pushButton_add_unwanted_match_date.clicked.connect(self.add_unwanted_match_date)
        self.ui.pushButton_remove_unwanted_match_date.clicked.connect(self.remove_unwanted_match_date)

        # TAB 03 - "Erweiterte Einstellungen"
        self.ui.tabWidget.setTabVisible(EXPERT_SETTINGS_TAB, False)
        self.ui.spinBox_max_iterations.valueChanged.connect(self.set_max_iterations)
        self.ui.checkBox_return_on_first_match_plan.clicked.connect(self.set_return_on_first_match_plan)
        self.ui.checkBox_consecutive_matches_allow.clicked.connect(self.set_consecutive_matches)
        self.ui.spinBox_consecutive_matches_probability.valueChanged.connect(self.set_consecutive_matches)
        self.ui.checkBox_shuffle_matches_allow.clicked.connect(self.set_shuffle_matches)
        self.ui.doubleSpinBox_shuffle_matches_shuffle_part.valueChanged.connect(self.set_shuffle_matches)
        self.ui.spinBox_weight_amount_consecutive_matches.valueChanged.connect(self.set_weight)
        self.ui.spinBox_weight_distribution_home_away_matches.valueChanged.connect(self.set_weight)
        self.ui.spinBox_weight_amount_please_dont_play_dates.valueChanged.connect(self.set_weight)
        self.ui.spinBox_weight_distribution_game_days.valueChanged.connect(self.set_weight)

        # TAB 04 - "Spielplan Erstellen"
        # Connection to create match plan
        self.ui.pushButton_download_matchplan.setEnabled(False)
        self.ui.tableWidget_match_plan.setEnabled(False)
        self.ui.pushButton_generate_matchplan.clicked.connect(self.generate_match_plan)
        self.ui.pushButton_download_matchplan.clicked.connect(self.save_match_plan)

        # Connection to matchmaker_core process
        self.process = QtCore.QProcess(self)
        self.process.readyRead.connect(self.stdout_ready)  # alternative to use print('',flush=True) instead of stdout
        self.process.started.connect(self.matchmaker_core_process_started)
        self.process.finished.connect(self.matchmaker_core_process_finished)

        self.ui.progressBar_matchplan_generation.hide()

        self.refresh_all_tabs()
        #self.show_generated_matchplan()  # TODO

    def refresh_all_tabs(self):
        self.refresh_tab_teams()
        self.refresh_tab_global_settings()
        self.refresh_tab_expert_settings()

    # TAB 00 - "Main Menu"
    def save_settings_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Spielplan Einstellungen Speichern", "", "(*.json)")
        if file_path:
            file_name = os.path.normpath(file_path)
            if self.MatchPlan.save_settings_file(file_name):
                QMessageBox.information(
                    self, "Einstellungen gespeichert", "Die Einstellungen für den Spielplan wurden erfolgreich gespeichert",
                    buttons=QMessageBox.Ok)
            else:
                QMessageBox.Critical(
                    self, "Fehler", "Die Einstellungen konnten nicht gespeichert werden.",
                    buttons=QMessageBox.Ok)

    def open_settings_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Spielplan Einstellungen öffnen", "", "(*.json)")
        if file_path:
            file_name = os.path.normpath(file_path)
            self.MatchPlan = Teams()
            if self.MatchPlan.open_and_parse_settings_file(file_name):
                QMessageBox.information(
                    self, "Spielplan geladen", "Die Einstellungen für den Spielplan wurden erfolgreich geladen",
                    buttons=QMessageBox.Ok)
            else:
                QMessageBox.critical(
                    self, "Fehler", "Die Einstellungen konnten nicht geladen werden.",
                    buttons=QMessageBox.Ok)

            self.refresh_all_tabs()

    def reset_settings_file(self):
        button = QMessageBox.warning(self, "Löschen bestätigen", "Alle Einstellungen für den Spielplan zurücksetzen?",
                                     buttons=QMessageBox.Ok | QMessageBox.Discard)
        if button == QMessageBox.Ok:
            self.ui.statusbar.showMessage("Alle Einstellungen zurückgesetzt", 5000)
            self.MatchPlan = Teams()
            self.refresh_all_tabs()

    # TAB 01 - "Globale Einstellungen"
    def refresh_tab_global_settings(self):
        start_date_first_round = self.MatchPlan.start_date_first_round
        start_date_second_round = self.MatchPlan.start_date_first_round
        end_date_first_round = self.MatchPlan.start_date_first_round

        if start_date_first_round is None:
            self.ui.checkBox_start_date_first_round_activate.setChecked(False)
            self.ui.dateEdit_start_date_first_round.setEnabled(False)
            self.ui.dateEdit_start_date_first_round.setDate(QDate(self.today.year, self.today.month, self.today.day))
        else:
            self.ui.checkBox_start_date_first_round_activate.setChecked(True)
            self.ui.dateEdit_start_date_first_round.setEnabled(True)
            date = self.MatchPlan.start_date_first_round
            self.ui.dateEdit_start_date_first_round.setDate(QDate(date.year, date.month, date.day))

        if end_date_first_round is None:
            self.ui.checkBox_end_date_first_round_activate.setChecked(False)
            self.ui.dateEdit_end_date_first_round.setEnabled(False)
            self.ui.dateEdit_end_date_first_round.setDate(QDate(self.today.year, self.today.month, self.today.day))
        else:
            self.ui.checkBox_end_date_first_round_activate.setChecked(True)
            self.ui.dateEdit_end_date_first_round.setEnabled(True)
            date = self.MatchPlan.end_date_first_round
            self.ui.dateEdit_end_date_first_round.setDate(QDate(date.year, date.month, date.day))

        if start_date_second_round is None:
            self.ui.checkBox_start_date_second_round_activate.setChecked(False)
            self.ui.dateEdit_start_date_second_round.setEnabled(False)
            self.ui.dateEdit_start_date_second_round.setDate(QDate(self.today.year, self.today.month, self.today.day))
        else:
            self.ui.checkBox_start_date_second_round_activate.setChecked(True)
            self.ui.dateEdit_start_date_second_round.setEnabled(True)
            date = self.MatchPlan.start_date_second_round
            self.ui.dateEdit_start_date_second_round.setDate(QDate(date.year, date.month, date.day))

        # General Blocked Dates
        self.ui.listWidget_general_blocked_dates.clear()
        self.ui.listWidget_general_blocked_dates.addItems(self.MatchPlan.get_all_general_blocked_dates(
            show_as_string=True, date_format=self.display_date_format))

    def set_start_date_first_round(self):
        if self.ui.checkBox_start_date_first_round_activate.isChecked():
            self.ui.dateEdit_start_date_first_round.setEnabled(True)
            selected_date = convert_qt_date_to_datetime(self.ui.dateEdit_start_date_first_round.date().getDate())
            self.MatchPlan.set_start_date_first_round(selected_date)
        else:
            self.ui.dateEdit_start_date_first_round.setEnabled(False)
            self.MatchPlan.set_start_date_first_round(None)

    def set_end_date_first_round(self):
        if self.ui.checkBox_end_date_first_round_activate.isChecked():
            self.ui.dateEdit_end_date_first_round.setEnabled(True)
            selected_date = convert_qt_date_to_datetime(self.ui.dateEdit_end_date_first_round.date().getDate())
            self.MatchPlan.set_end_date_first_round(selected_date)
        else:
            self.ui.dateEdit_end_date_first_round.setEnabled(False)
            self.MatchPlan.set_end_date_first_round(None)

    def set_start_date_second_round(self):
        if self.ui.checkBox_start_date_second_round_activate.isChecked():
            self.ui.dateEdit_start_date_second_round.setEnabled(True)
            selected_date = convert_qt_date_to_datetime(self.ui.dateEdit_start_date_second_round.date().getDate())
            self.MatchPlan.set_start_date_second_round(selected_date)
        else:
            self.ui.dateEdit_start_date_second_round.setEnabled(False)
            self.MatchPlan.set_start_date_second_round(None)

    def show_general_blocked_dates(self):
        self.ui.listWidget_general_blocked_dates.clear()
        self.ui.listWidget_general_blocked_dates.addItems(self.MatchPlan.get_all_general_blocked_dates(
            show_as_string=True, date_format=self.display_date_format))

    def add_general_blocked_date(self):
        selected_date_qt = self.ui.dateEdit_general_blocked_dates.date().getDate()  # Year, Month, Day
        selected_date = convert_qt_date_to_datetime(selected_date_qt)
        self.MatchPlan.add_general_blocked_date(selected_date)
        self.show_general_blocked_dates()

    def remove_general_blocked_date(self):
        current_index = self.ui.listWidget_general_blocked_dates.currentRow()
        if current_index != -1:
            date_string = self.ui.listWidget_general_blocked_dates.item(current_index).text()
            date_object = convert_date_string_to_datetime(date_string, date_format=self.display_date_format)
            self.MatchPlan.remove_general_blocked_date(date_object)
            self.show_general_blocked_dates()

    def show_expert_settings(self):
        if self.ui.checkBox_expert_settings.isChecked():
            self.ui.tabWidget.setTabVisible(EXPERT_SETTINGS_TAB, True)
        else:
            self.ui.tabWidget.setTabVisible(EXPERT_SETTINGS_TAB, False)

    # TAB 02 - "Mannschaften"
    def refresh_tab_teams(self):
        self.show_teams()

    def update_selected_team(self):
        current_index = self.ui.listWidget_teams.currentRow()
        self.current_selection_team = self.ui.listWidget_teams.item(current_index).text()
        if self.current_selection_team is not None:
            self.show_home_match_dates()
            self.show_blocked_match_dates()
            self.show_unwanted_match_dates()

    def show_teams(self):
        self.ui.listWidget_teams.clear()
        #if not self.MatchPlan.get_all_teams():
        #    self.ui.pushButton_add_home_match_date.setEnabled(False)
        self.ui.listWidget_teams.addItems(self.MatchPlan.get_all_teams())
        current_index = self.ui.listWidget_teams.currentRow()
        #amount_of_teams = self.ui.listWidget_teams.items()
        if current_index == -1:
            self.ui.listWidget_teams.setCurrentRow(0)

    def add_team(self):
        text, ok = QInputDialog.getText(self, "Neue Mannschaft anlegen", "Mannschaftsname")
        if ok and text is not None and text != "":
            self.MatchPlan.add_team(text)
            self.show_teams()
        self.show_teams()

    def remove_team(self):
        current_index = self.ui.listWidget_teams.currentRow()
        if current_index != -1:
            team = self.ui.listWidget_teams.item(current_index).text()
            button = QMessageBox.warning(self, "Löschen bestätigen", "Verein und alle zugehörigen Daten entfernen?",
                                     buttons=QMessageBox.Ok | QMessageBox.Discard)
            if button == QMessageBox.Ok:
                self.MatchPlan.remove_team(team)
            self.show_teams()

    def show_home_match_dates(self):
        self.ui.listWidget_home_match_dates.clear()
        self.ui.listWidget_home_match_dates.addItems(
            self.MatchPlan.get_all_home_match_dates(self.current_selection_team, show_as_string=True,
                                                     date_format=self.display_date_format))

    def add_home_match_date(self):
        selected_date_qt = self.ui.dateEdit_home_match_date.date().getDate()  # Year, Month, Day
        selected_date = convert_qt_date_to_datetime(selected_date_qt)
        self.MatchPlan.add_home_match_date(self.current_selection_team, selected_date)
        self.show_home_match_dates()

    def remove_home_match_date(self):
        current_index = self.ui.listWidget_home_match_dates.currentRow()
        if current_index != -1:
            date_string = self.ui.listWidget_home_match_dates.item(current_index).text()
            date_object = convert_date_string_to_datetime(date_string, date_format=self.display_date_format)
            self.MatchPlan.remove_home_match_date(self.current_selection_team, date_object)
            self.show_home_match_dates()

    def show_blocked_match_dates(self):
        self.ui.listWidget_blocked_match_dates.clear()
        self.ui.listWidget_blocked_match_dates.addItems(
            self.MatchPlan.show_all_blocked_match_dates(self.current_selection_team, show_as_string=True,
                                                        date_format=self.display_date_format))

    def add_blocked_match_date(self):
        selected_date_qt = self.ui.dateEdit_blocked_match_date.date().getDate()  # Year, Month, Day
        selected_date = convert_qt_date_to_datetime(selected_date_qt)
        self.MatchPlan.add_blocked_match_date(self.current_selection_team, selected_date)
        self.show_blocked_match_dates()

    def remove_blocked_match_date(self):
        current_index = self.ui.listWidget_blocked_match_dates.currentRow()
        if current_index != -1:
            date_string = self.ui.listWidget_blocked_match_dates.item(current_index).text()
            date_object = convert_date_string_to_datetime(date_string, date_format=self.display_date_format)
            self.MatchPlan.remove_blocked_match_date(self.current_selection_team, date_object)
            self.show_blocked_match_dates()

    def show_unwanted_match_dates(self):
        self.ui.listWidget_unwanted_match_dates.clear()
        self.ui.listWidget_unwanted_match_dates.addItems(
            self.MatchPlan.show_all_unwanted_match_dates(self.current_selection_team, show_as_string=True,
                                                         date_format=self.display_date_format))

    def add_unwanted_match_date(self):
        selected_date_qt = self.ui.dateEdit_unwanted_match_date.date().getDate()  # Year, Month, Day
        selected_date = convert_qt_date_to_datetime(selected_date_qt)
        self.MatchPlan.add_unwanted_match_date(self.current_selection_team, selected_date)
        self.show_unwanted_match_dates()

    def remove_unwanted_match_date(self):
        current_index = self.ui.listWidget_unwanted_match_dates.currentRow()
        if current_index != -1:
            date_string = self.ui.listWidget_unwanted_match_dates.item(current_index).text()
            date_object = convert_date_string_to_datetime(date_string, date_format=self.display_date_format)
            self.MatchPlan.remove_unwanted_match_date(self.current_selection_team, date_object)
            self.show_unwanted_match_dates()

    # TAB 03 - "Erweiterte Einstellungen"
    def refresh_tab_expert_settings(self):
        self.ui.spinBox_max_iterations.setValue(self.MatchPlan.max_iterations)
        self.ui.checkBox_return_on_first_match_plan.setChecked(self.MatchPlan.return_on_first_match_plan)
        if self.MatchPlan.consecutive_matches['allow'] == 1:
            self.ui.checkBox_consecutive_matches_allow.setChecked(True)
        else:
            self.ui.checkBox_consecutive_matches_allow.setChecked(False)
        self.ui.spinBox_consecutive_matches_probability.setValue(self.MatchPlan.consecutive_matches['probability'])
        if self.MatchPlan.shuffle_matches['allow'] == 1:
            self.ui.checkBox_shuffle_matches_allow.setChecked(True)
        else:
            self.ui.checkBox_shuffle_matches_allow.setChecked(False)
        self.ui.doubleSpinBox_shuffle_matches_shuffle_part.setValue(self.MatchPlan.shuffle_matches['shuffle_part'])
        self.ui.spinBox_weight_amount_consecutive_matches.setValue(self.MatchPlan.weight['amount_consecutive_matches'])
        self.ui.spinBox_weight_distribution_game_days.setValue(self.MatchPlan.weight['distribution_game_days'])
        self.ui.spinBox_weight_amount_please_dont_play_dates.setValue(
            self.MatchPlan.weight['amount_please_dont_play_dates'])
        self.ui.spinBox_weight_distribution_home_away_matches.setValue(
            self.MatchPlan.weight['distribution_home_away_matches'])

    def set_max_iterations(self):
        self.MatchPlan.set_max_iterations(self.ui.spinBox_max_iterations.value())

    def set_return_on_first_match_plan(self):
        self.MatchPlan.set_return_on_first_match_plan(self.ui.checkBox_return_on_first_match_plan.isChecked())

    def set_consecutive_matches(self):
        consecutive_matches_allow = self.ui.checkBox_consecutive_matches_allow.isChecked()
        consecutive_matches_probability = self.ui.spinBox_consecutive_matches_probability.value()
        self.MatchPlan.set_settings_consecutive_matches(consecutive_matches_allow, consecutive_matches_probability)

    def set_shuffle_matches(self):
        shuffle_matches_allow = self.ui.checkBox_shuffle_matches_allow.isChecked()
        shuffle_matches_part = self.ui.doubleSpinBox_shuffle_matches_shuffle_part.value()
        self.MatchPlan.set_settings_shuffle_matches(shuffle_matches_allow, shuffle_matches_part)

    def set_weight(self):
        amount_consecutive_matches = self.ui.spinBox_weight_amount_consecutive_matches.value()
        distribution_game_days = self.ui.spinBox_weight_distribution_game_days.value()
        amount_please_dont_play_dates = self.ui.spinBox_weight_amount_please_dont_play_dates.value()
        distribution_home_away_matches = self.ui.spinBox_weight_distribution_home_away_matches.value()
        self.MatchPlan.set_settings_weight(amount_consecutive_matches, distribution_game_days,
                                           amount_please_dont_play_dates, distribution_home_away_matches)

    # TAB 04 - "Spielplan Erstellen"
    def generate_match_plan(self):
        if os.path.exists(self.path_to_matchplan_csv):
            logging.info(f"Match plan already exists: {self.path_to_matchplan_csv}")
            button = QMessageBox.question(self, "Löschen bestätigen", "Bisherigen Spielplan löschen und Neuen generieren?",
                                     buttons=QMessageBox.Yes | QMessageBox.No)
            if button == QMessageBox.Yes:
                try:
                    os.remove(self.path_to_matchplan_csv)
                    logging.info(f"Deleting old match plan: {self.path_to_matchplan_csv}")
                except OSError as e:
                    logging.error("Error deleting old match plan file: %s - %s." % (e.filename, e.strerror))
            else:
                return
        self.ui.textEdit_matchmaker_core_output.clear()
        self.ui.pushButton_download_matchplan.setEnabled(False)
        self.ui.tableWidget_match_plan.setRowCount(0)
        self.MatchPlan.remove_settings_file(self.path_to_settings_json)  # remove old file
        self.MatchPlan.save_settings_file(self.path_to_settings_json)
        logging.info('Starting process: generate matchplan')
        self.process.start(self.path_to_matchmaker_core)

    def append_matchmaker_core_text(self, text):
        cursor = self.ui.textEdit_matchmaker_core_output.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        # self.output.ensureCursorVisible()

    def matchmaker_core_process_started(self):
        self.ui.progressBar_matchplan_generation.show()
        self.ui.progressBar_matchplan_generation.setValue(0)
        self.ui.pushButton_generate_matchplan.setEnabled(False)
        self.append_matchmaker_core_text('Starte Spielplan Generierung' + '\n')

    def matchmaker_core_process_finished(self):
        self.ui.pushButton_generate_matchplan.setEnabled(True)
        self.append_matchmaker_core_text('Spielplan Generierung beendet' + '\n')
        self.ui.progressBar_matchplan_generation.setValue(100)
        logging.info("Process finished: generate matchplan")
        if os.path.exists(self.path_to_matchplan_csv):
            self.ui.pushButton_download_matchplan.setEnabled(True)
            self.ui.tableWidget_match_plan.setEnabled(True)
            self.show_generated_matchplan()
            logging.info(f"New match plan available: {self.path_to_matchplan_csv}")
        else:
            self.ui.pushButton_download_matchplan.setEnabled(False)
            self.ui.tableWidget_match_plan.setEnabled(False)
            logging.warning(f"No match plan seems to be created: {self.path_to_matchplan_csv}")

    def stdout_ready(self):
        text = str(self.process.readAllStandardOutput())
        text_clean = return_clean_stdout_text(text)
        for entry in text_clean:
            logging.info(f"matchmaker_core stdout: {entry}")
            if "RUN" in entry:
                try:
                    self.ui.progressBar_matchplan_generation.setValue(int(entry[4:]))  # Remove "RUN:"
                except Exception:
                    pass
            else:
                self.append_matchmaker_core_text(entry + '\n')

    def save_match_plan(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Spielplan speichern", "", "(*.csv)")
        if file_path and self.path_to_matchplan_csv:
            file_name = os.path.normpath(file_path)
            try:
                shutil.copyfile(self.path_to_matchplan_csv, file_name)
                logging.info(f"Match plan saved to: {file_name}")
                QMessageBox.information(
                    self, "Einstellungen gespeichert", "Der Spielplan wurden erfolgreich gespeichert",
                    buttons=QMessageBox.Ok)
            except IOError as e:
                logging.error(f"Error while saving match plan: {e}")
                QMessageBox.critical(
                    self, "Fehler", "Der Spielplan konnten nicht gespeichert werden.",
                    buttons=QMessageBox.Ok)

    def show_generated_matchplan(self):
        df = pd.read_csv(self.path_to_matchplan_csv, sep=";")
        count_row = df.shape[0]
        list_of_column_names = list(df.columns)
        relevant_columns = [list_of_column_names[1], list_of_column_names[2], list_of_column_names[6]]
        self.ui.tableWidget_match_plan.setRowCount(count_row)
        self.ui.tableWidget_match_plan.setColumnCount(3)
        self.ui.tableWidget_match_plan.setHorizontalHeaderLabels(relevant_columns)
        for index, row in df.iterrows():
            self.ui.tableWidget_match_plan.setItem(index, 0, QTableWidgetItem(row["Datum"]))
            self.ui.tableWidget_match_plan.setItem(index, 1, QTableWidgetItem(row["Heimmannschaft"]))
            self.ui.tableWidget_match_plan.setItem(index, 2, QTableWidgetItem(row["Gastmannschaft"]))
            # Table will fit the screen horizontally
        self.ui.tableWidget_match_plan.horizontalHeader().setStretchLastSection(True)
        self.ui.tableWidget_match_plan.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


def run_app():
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(filename='logfile.log', filemode='w', level=logging.INFO, format=FORMAT)
    logging.getLogger().addHandler(logging.StreamHandler())
    print("Matchmaker Gui")
    print("===== V0.2 =====")
    print("Maintainer: Bjarne Andersen - b-andersen@arkaris.de")
    print("")
    logging.info('Start Application')
    logging.info("===== V0.2 =====")
    logging.info("Maintainer: Bjarne Andersen - b-andersen@arkaris.de")
    run_app()

