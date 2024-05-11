from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox
from main_window import Ui_MainWindow

import sys

from pprint import pprint
from teamsParser import Teams


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.MatchPlan = Teams("teams.json")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show_teams()
        self.ui.listWidget_teams.itemSelectionChanged.connect(self.show_home_match_dates)
        self.ui.listWidget_teams.itemSelectionChanged.connect(self.show_blocked_match_dates)
        self.ui.listWidget_teams.itemSelectionChanged.connect(self.show_unwanted_match_dates)

    def show_teams(self):
        self.ui.listWidget_teams.addItems(self.MatchPlan.get_all_teams())
        self.ui.listWidget_teams.setCurrentRow(0)

    def show_home_match_dates(self):
        current_index = self.ui.listWidget_teams.currentRow()
        team = self.ui.listWidget_teams.item(current_index).text()
        if team is not None:
            self.ui.listWidget_home_match_dates.clear()
            self.ui.listWidget_home_match_dates.addItems(
                self.MatchPlan.show_all_home_match_dates(team, show_as_string=True))

    def show_blocked_match_dates(self):
        current_index = self.ui.listWidget_teams.currentRow()
        team = self.ui.listWidget_teams.item(current_index).text()
        if team is not None:
            self.ui.listWidget_blocked_match_dates.clear()
            self.ui.listWidget_blocked_match_dates.addItems(
                self.MatchPlan.show_all_blocked_match_dates(team, show_as_string=True))

    def show_unwanted_match_dates(self):
        current_index = self.ui.listWidget_teams.currentRow()
        team = self.ui.listWidget_teams.item(current_index).text()
        if team is not None:
            self.ui.listWidget_unwanted_match_dates.clear()
            self.ui.listWidget_unwanted_match_dates.addItems(
                self.MatchPlan.show_all_unwanted_match_dates(team, show_as_string=True))




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

