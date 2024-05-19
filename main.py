import os.path

from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QFileDialog
from main_window import Ui_MainWindow
from datetime import datetime
from utils import convert_qt_date_to_datetime, convert_date_string_to_datetime, return_clean_stdout_text, get_script_folder
import sys
import logging
from pprint import pprint
from teamsParser import Teams

logger = logging.getLogger(__name__)
EXPERT_SETTINGS_TAB = 2


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.today = datetime.today()
        script_path = get_script_folder()
        self.path_to_settings_json = os.path.join(script_path, "tools", "teams.json")
        self.path_to_ligaman_pro = os.path.join(script_path, "tools", "ligaman_pro.exe")
        print(f"Path to settings JSON file: {self.path_to_settings_json}")
        print(f"Path to Ligaman Pro: {self.path_to_ligaman_pro}")
        self.MatchPlan = Teams()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.display_date_format = '%d.%m.%Y'
        self.current_selection_team = None

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

        # TAB 04 - "Spielplan Erstellen"
        # Connection to create match plan
        self.ui.pushButton_download_matchplan.setEnabled(False)
        self.ui.pushButton_generate_matchplan.clicked.connect(self.generate_match_plan)
        self.ui.pushButton_download_matchplan.clicked.connect(self.save_match_plan)

        # Connection to ligaman_pro process
        self.process = QtCore.QProcess(self)
        self.process.readyRead.connect(self.stdout_ready)  # alternative to use print('',flush=True) instead of stdout
        self.process.started.connect(self.ligaman_process_started)
        self.process.finished.connect(self.ligaman_process_finished)

        self.ui.progressBar_matchplan_generation.hide()

        self.refresh_tab_global_settings()
        self.refresh_all_tabs()

    def refresh_all_tabs(self):
        self.refresh_tab_teams()

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
        print(f"Start Date first round set to: {self.MatchPlan.start_date_first_round}")

    def set_end_date_first_round(self):
        if self.ui.checkBox_end_date_first_round_activate.isChecked():
            self.ui.dateEdit_end_date_first_round.setEnabled(True)
            selected_date = convert_qt_date_to_datetime(self.ui.dateEdit_end_date_first_round.date().getDate())
            self.MatchPlan.set_end_date_first_round(selected_date)
        else:
            self.ui.dateEdit_end_date_first_round.setEnabled(False)
            self.MatchPlan.set_end_date_first_round(None)
        print(f"End Date first round set to: {self.MatchPlan.end_date_first_round}")

    def set_start_date_second_round(self):
        if self.ui.checkBox_start_date_second_round_activate.isChecked():
            self.ui.dateEdit_start_date_second_round.setEnabled(True)
            selected_date = convert_qt_date_to_datetime(self.ui.dateEdit_start_date_second_round.date().getDate())
            self.MatchPlan.set_start_date_second_round(selected_date)
        else:
            self.ui.dateEdit_start_date_second_round.setEnabled(False)
            self.MatchPlan.set_start_date_second_round(None)
        print(f"Start Date second round set to: {self.MatchPlan.start_date_second_round}")

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

    # TAB 04 - "Spielplan Erstellen"
    def generate_match_plan(self):
        self.ui.textEdit_ligaman_pro_output.clear()
        self.ui.pushButton_download_matchplan.setEnabled(False)
        self.MatchPlan.remove_settings_file(self.path_to_settings_json)
        self.MatchPlan.save_settings_file(self.path_to_settings_json)
        print('Starting process')
        self.process.start(self.path_to_ligaman_pro)

    def append_ligaman_pro_text(self, text):
        cursor = self.ui.textEdit_ligaman_pro_output.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        # self.output.ensureCursorVisible()

    def ligaman_process_started(self):
        self.ui.progressBar_matchplan_generation.show()
        self.ui.progressBar_matchplan_generation.setValue(0)
        self.ui.pushButton_generate_matchplan.setEnabled(False)
        self.append_ligaman_pro_text('Starte Spielplan Generierung' + '\n')

    def ligaman_process_finished(self):
        self.ui.pushButton_generate_matchplan.setEnabled(True)
        self.append_ligaman_pro_text('Spielplan Generierung beendet' + '\n')
        self.ui.progressBar_matchplan_generation.setValue(100)
        if self.MatchPlan.check_for_settings_file(self.path_to_settings_json):
            self.ui.pushButton_download_matchplan.setEnabled(True)
        else:
            self.ui.pushButton_download_matchplan.setEnabled(False)

    def stdout_ready(self):
        text = str(self.process.readAllStandardOutput())
        text_clean = return_clean_stdout_text(text)
        for entry in text_clean:
            if "RUN" in entry:
                try:
                    self.ui.progressBar_matchplan_generation.setValue(int(entry[4:]))  # Remove "RUN:"
                except Exception:
                    pass
            else:
                self.append_ligaman_pro_text(entry + '\n')

    def save_match_plan(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)

    def open_match_plan(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)


def run_app():
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    logging.basicConfig(filename='systemlog.log', level=logging.INFO)
    print("Ligaman Gui")
    print("===== V0.2 =====")
    print("Maintainer: Bjarne Andersen - b-andersen@arkaris.de")
    print("")
    logger.info('Start Application')
    run_app()

