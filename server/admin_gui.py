# -*- coding: utf-8 -*-

from PySide2 import QtCore, QtGui, QtWidgets
import json
from server import ServerProgram
from update_database_gui import UpdateDatabase
from user_data_handler import UserDataHandler
from weather_data_handler import WeatherDataHandler

class AdminProgram():
    def showWidgets(self):
        self.WELCOME_label.show()
        self.username_box.show()
        self.password_box.show()
        self.login_button.show()

    def Login(self, MainWindow, serverProgram:ServerProgram):
        username = self.username_box.text()
        password = self.password_box.text()

        if not serverProgram.userDataHandler.VerifyAdmin(username, password):
            QtWidgets.QMessageBox.about(MainWindow, "Đăng nhập thất bại" , "username/password: admin/admin")
        else:
            updateDatabase = UpdateDatabase(serverProgram)
            updateDatabase.setupUI()
            updateDatabase.MainWindow.show()
            # Create a window allow admin update weather data

    def setupUI(self, MainWindow, serverProgram):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(362, 261)

        self.WELCOME_label = QtWidgets.QLabel(MainWindow)
        self.WELCOME_label.setGeometry(QtCore.QRect(50, 10, 261, 51))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(22)
        self.WELCOME_label.setFont(font)
        self.WELCOME_label.setAlignment(QtCore.Qt.AlignCenter)
        self.WELCOME_label.setObjectName("WELCOME_label")

        self.username_box = QtWidgets.QLineEdit(MainWindow)
        self.username_box.setGeometry(QtCore.QRect(50, 80, 261, 41))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(14)
        self.username_box.setFont(font)
        self.username_box.setDragEnabled(True)
        self.username_box.setClearButtonEnabled(True)
        self.username_box.setObjectName("username_box")

        self.password_box = QtWidgets.QLineEdit(MainWindow)
        self.password_box.setGeometry(QtCore.QRect(50, 130, 261, 41))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(14)
        self.password_box.setFont(font)
        self.password_box.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_box.setDragEnabled(True)
        self.password_box.setClearButtonEnabled(True)
        self.password_box.setObjectName("password_box")

        self.login_button = QtWidgets.QPushButton(MainWindow, clicked = lambda:self.Login(MainWindow, serverProgram))
        self.login_button.setGeometry(QtCore.QRect(120, 190, 121, 41))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(16)
        self.login_button.setFont(font)
        self.login_button.setObjectName("login_button")

        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.WELCOME_label.setText(_translate("MainWindow", "Welcome Admin"))
        self.username_box.setText(_translate("MainWindow", "Username"))
        self.password_box.setText(_translate("MainWindow", "Password"))
        self.login_button.setText(_translate("MainWindow", "Login"))

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.showWidgets()

if __name__ == "__main__":
    import sys
    from os import environ

    def suppress_qt_warnings():
        environ["QT_DEVICE_PIXEL_RATIO"] = "0"
        environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        environ["QT_SCREEN_SCALE_FACTORS"] = "1"
        environ["QT_SCALE_FACTOR"] = "1"

    suppress_qt_warnings()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QWidget()
    ui = AdminProgram()
    serverProgram = ServerProgram()
    ui.setupUI(MainWindow, serverProgram)
    MainWindow.show()
    sys.exit(app.exec_())