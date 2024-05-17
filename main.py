import os.path

from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QFileDialog
from main_window import Ui_MainWindow
from datetime import datetime
from utils import convert_qt_date_to_datetime, convert_date_string_to_datetime, return_clean_stdout_text, get_script_folder
import sys
from pprint import pprint
from teamsParser import Teams


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
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
        self.current_selection_home_match_date = None
        self.current_selection_blocked_match_date = None
        self.current_selection_unwanted_match_date = None

        # Set Date and Time to Date Edits
        self.today = datetime.today()
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

        self.show_teams()

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

    def update_selected_team(self):
        current_index = self.ui.listWidget_teams.currentRow()
        self.current_selection_team = self.ui.listWidget_teams.item(current_index).text()
        if self.current_selection_team is not None:
            self.show_home_match_dates()
            self.show_blocked_match_dates()
            self.show_unwanted_match_dates()

    def show_teams(self):
        self.ui.listWidget_teams.clear()
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
            self.MatchPlan.show_all_home_match_dates(self.current_selection_team, show_as_string=True,
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

    # TAB 3 - Generate Matchplan
    def generate_match_plan(self):
        self.ui.textEdit_ligaman_pro_output.clear()
        self.ui.pushButton_download_matchplan.setEnabled(False)
        self.MatchPlan.remove_settings_file(self.path_to_settings_json)
        self.MatchPlan.save_settings_file(self.path_to_settings_json)
        print('Starting process')
        self.process.start(self.path_to_ligaman_pro)

    def save_match_plan(self):
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
    print("Ligaman Gui")
    print("===== V0.2 =====")
    print("Maintainer: Bjarne Andersen - b-andersen@arkaris.de")
    print("")
    #MatchPlan = Teams("teams.json")
    #MatchPlan.add_team("Honkverein")

    run_app()

