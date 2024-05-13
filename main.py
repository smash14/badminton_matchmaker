from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox
from main_window import Ui_MainWindow
from utils import convert_qt_date_to_datetime, convert_date_string_to_datetime

import sys

from pprint import pprint
from teamsParser import Teams


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.MatchPlan = Teams("teams.json")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.display_date_format = '%d.%m.%Y'
        self.current_selection_team = None
        self.current_selection_home_match_date = None
        self.current_selection_blocked_match_date = None
        self.current_selection_unwanted_match_date = None

        self.ui.listWidget_teams.itemSelectionChanged.connect(self.update_selected_team)

        self.ui.pushButton_add_team.clicked.connect(self.add_team)
        self.ui.pushButton_remove_team.clicked.connect(self.remove_team)

        self.ui.pushButton_add_home_match_date.clicked.connect(self.add_home_match_date)
        self.ui.pushButton_remove_home_match_date.clicked.connect(self.remove_home_match_date)
        self.ui.pushButton_add_blocked_match_date.clicked.connect(self.add_blocked_match_date)
        self.ui.pushButton_remove_blocked_match_date.clicked.connect(self.remove_blocked_match_date)
        self.ui.pushButton_add_unwanted_match_date.clicked.connect(self.add_unwanted_match_date)
        self.ui.pushButton_remove_unwanted_match_date.clicked.connect(self.remove_unwanted_match_date)

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


def app():
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

    app()

