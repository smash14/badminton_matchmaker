# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1043, 702)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.listWidget_teams = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget_teams.setGeometry(QtCore.QRect(70, 90, 256, 192))
        self.listWidget_teams.setObjectName("listWidget_teams")
        self.listWidget_home_match_dates = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget_home_match_dates.setGeometry(QtCore.QRect(330, 90, 151, 192))
        self.listWidget_home_match_dates.setObjectName("listWidget_home_match_dates")
        self.listWidget_blocked_match_dates = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget_blocked_match_dates.setGeometry(QtCore.QRect(490, 90, 151, 192))
        self.listWidget_blocked_match_dates.setObjectName("listWidget_blocked_match_dates")
        self.listWidget_unwanted_match_dates = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget_unwanted_match_dates.setGeometry(QtCore.QRect(650, 90, 151, 192))
        self.listWidget_unwanted_match_dates.setObjectName("listWidget_unwanted_match_dates")
        self.pushButton_add_team = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_add_team.setGeometry(QtCore.QRect(70, 290, 101, 23))
        self.pushButton_add_team.setObjectName("pushButton_add_team")
        self.pushButton_remove_team = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_remove_team.setGeometry(QtCore.QRect(180, 290, 101, 23))
        self.pushButton_remove_team.setObjectName("pushButton_remove_team")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1043, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_add_team.setText(_translate("MainWindow", "Verein hinzufügen"))
        self.pushButton_remove_team.setText(_translate("MainWindow", "Verein entfernen"))
