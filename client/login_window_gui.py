# -*- coding: utf-8 -*-

import os.path
from pathlib import Path
from logging import error
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QMessageBox, QWidget
from client import ClientProgram
from weather_forecast_gui import WeatherWindow

PIC_PATH = os.path.join(Path(__file__).parent.absolute(),"pic")

class LoginWindow(object):

    def setupUI(self, MainWindow, clientProgram):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 502)
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Login"))

        self.background_image = QtWidgets.QLabel(MainWindow)
        self.background_image.setGeometry(QtCore.QRect(0, 0, 901, 501))
        self.background_image.setAutoFillBackground(False)
        self.background_image.setText("")
        self.background_image.setPixmap(QtGui.QPixmap(os.path.join(PIC_PATH, "background-login.jpg")))
        self.background_image.setScaledContents(True)
        self.background_image.setObjectName("label")
        self.background_image.raise_()
    
        self.login_window_image = QtWidgets.QLabel(MainWindow)
        self.login_window_image.setGeometry(QtCore.QRect(260, 50, 381, 401))
        self.login_window_image.setMouseTracking(False)
        self.login_window_image.setTabletTracking(False)
        self.login_window_image.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.login_window_image.setAutoFillBackground(False)
        self.login_window_image.setText("")
        self.login_window_image.setPixmap(QtGui.QPixmap(os.path.join(PIC_PATH, "background_login_box.jpg")))
        self.login_window_image.setScaledContents(True)
        self.login_window_image.setObjectName("login_window_label")
        self.login_window_image.raise_()

        self.WELCOME_label = QtWidgets.QLabel(MainWindow)
        self.WELCOME_label.setGeometry(QtCore.QRect(350, 90, 211, 41))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.WELCOME_label.setFont(font)
        self.WELCOME_label.setAutoFillBackground(False)
        self.WELCOME_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.WELCOME_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.WELCOME_label.setScaledContents(False)
        self.WELCOME_label.setAlignment(QtCore.Qt.AlignCenter)
        self.WELCOME_label.setObjectName("WELCOME_label")
        self.WELCOME_label.raise_()
        self.WELCOME_label.setText(_translate("MainWindow", "WELCOME"))       

        self.username_box = QtWidgets.QLineEdit(MainWindow)
        self.username_box.setGeometry(QtCore.QRect(290, 150, 321, 41))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.username_box.setFont(font)
        self.username_box.setDragEnabled(True)
        self.username_box.setClearButtonEnabled(True)
        self.username_box.setObjectName("username_box")
        self.username_box.raise_()
        self.username_box.setText(_translate("MainWindow", "Username"))       

        self.password_box = QtWidgets.QLineEdit(MainWindow)
        self.password_box.setGeometry(QtCore.QRect(290, 210, 321, 41))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        font.setStrikeOut(False)
        font.setStyleStrategy(QtGui.QFont.NoAntialias)
        self.password_box.setFont(font)
        self.password_box.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_box.setDragEnabled(True)
        self.password_box.setClearButtonEnabled(True)
        self.password_box.setObjectName("password_box")
        self.password_box.raise_()
        self.password_box.setText(_translate("MainWindow", "Password"))

        self.login_button = QtWidgets.QPushButton(MainWindow, clicked = lambda:self.onLogin(MainWindow, clientProgram))
        self.login_button.setGeometry(QtCore.QRect(410, 280, 91, 41))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.login_button.setFont(font)
        self.login_button.setObjectName("login_button")
        self.login_button.raise_()
        self.login_button.setText(_translate("MainWindow", "Login"))

        self.findpassword_label = QtWidgets.QLabel(MainWindow)
        self.findpassword_label.setGeometry(QtCore.QRect(300, 350, 131, 21))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.findpassword_label.setFont(font)
        self.findpassword_label.setAutoFillBackground(False)
        self.findpassword_label.setScaledContents(False)
        self.findpassword_label.setAlignment(QtCore.Qt.AlignCenter)
        self.findpassword_label.setObjectName("findpassword_label")
        self.findpassword_label.raise_()
        self.findpassword_label.setText(_translate("MainWindow", "Forgot password?"))
        self.findpassword_label.hide()   

        self.findpassword_button = QtWidgets.QPushButton(MainWindow, clicked = lambda:self.onFindpassword())
        self.findpassword_button.setGeometry(QtCore.QRect(300, 370, 121, 28))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        self.findpassword_button.setFont(font)
        self.findpassword_button.setFlat(True)
        self.findpassword_button.setObjectName("findpassword_button")
        self.findpassword_button.raise_()
        self.findpassword_button.setText(_translate("MainWindow", "Click here"))     
        self.findpassword_button.hide()

        self.signup_label = QtWidgets.QLabel(MainWindow)
        self.signup_label.setGeometry(QtCore.QRect(490, 350, 121, 21))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.signup_label.setFont(font)
        self.signup_label.setAutoFillBackground(False)
        self.signup_label.setScaledContents(False)
        self.signup_label.setAlignment(QtCore.Qt.AlignCenter)
        self.signup_label.setObjectName("signup_label")
        self.signup_label.raise_()
        self.signup_label.setText(_translate("MainWindow", "New user?"))

        self.signup_button = QtWidgets.QPushButton(MainWindow, clicked = lambda:self.signup_layout())
        self.signup_button.setGeometry(QtCore.QRect(490, 370, 121, 28))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        self.signup_button.setFont(font)
        self.signup_button.setFlat(True)
        self.signup_button.setObjectName("signup_button")
        self.signup_button.raise_()
        self.signup_button.setText(_translate("MainWindow", "Click here"))

        self.findpassword_button_2 = QtWidgets.QPushButton(MainWindow, clicked = lambda:self.returnPassword(MainWindow, clientProgram))
        self.findpassword_button_2.setGeometry(QtCore.QRect(385, 280, 141, 41))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.findpassword_button_2.setFont(font)
        self.findpassword_button_2.setObjectName("findpassword_button_2")
        self.findpassword_button_2.raise_()
        self.findpassword_button_2.setText(_translate("MainWindow", "Find password"))
        self.findpassword_button_2.hide()

        self.label_2 = QtWidgets.QLabel(MainWindow)
        self.label_2.setGeometry(QtCore.QRect(294, 215, 321, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_2.raise_()
        self.label_2.setText(_translate("MainWindow", "Your password: "))
        self.label_2.hide()

        self.signup_button_2 = QtWidgets.QPushButton(MainWindow, clicked = lambda:self.onRegister(MainWindow, clientProgram))
        self.signup_button_2.setGeometry(QtCore.QRect(410, 280, 91, 41))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.signup_button_2.setFont(font)
        self.signup_button_2.setDefault(False)
        self.signup_button_2.setFlat(False)
        self.signup_button_2.setObjectName("signup_button_2")
        self.signup_button_2.raise_()
        self.signup_button_2.setText(_translate("MainWindow", "Register"))
        self.signup_button_2.hide()

        self.return_button = QtWidgets.QPushButton(MainWindow, clicked = lambda:self.Window())
        self.return_button.setGeometry(QtCore.QRect(490, 370, 121, 28))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        self.return_button.setFont(font)
        self.return_button.setFlat(True)
        self.return_button.setObjectName("return_button")
        self.return_button.raise_()
        self.return_button.setText(_translate("MainWindow", "Return"))
        self.return_button.hide()

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def Window(self):
        self.WELCOME_label.show()
        self.username_box.show()
        self.password_box.show()
        self.login_button.show()
        self.findpassword_label.hide()
        self.findpassword_button.hide()
        self.signup_label.show()
        self.signup_button.show()
        self.findpassword_button_2.hide()
        self.label_2.hide()
        self.signup_button_2.hide()
        self.return_button.hide()
        pass

    def onLogin(self, MainWindow, clientProgram:ClientProgram):
        username = self.username_box.text()
        password = self.password_box.text()
        state, error = clientProgram.Login(username, password)

        if state == ClientProgram.State.SUCCEEDED:
            QMessageBox.about(MainWindow, "", "Đăng nhập thành công")
            weatherWindow = WeatherWindow()
            weatherWindow.setupUI(MainWindow, clientProgram)
        elif state == ClientProgram.State.FAILED:
            QMessageBox.about(MainWindow, "Đăng nhập thất bại. Lỗi:", error)
        else:
            QMessageBox.about(MainWindow, "","Lỗi kết nối đến server")

        pass

    def onFindpassword(self):
        self.password_box.hide()
        self.login_button.hide()
        self.findpassword_label.hide()
        self.findpassword_button.hide()
        self.signup_label.hide()
        self.signup_button.hide()
        self.signup_button_2.hide()
        self.label_2.hide()

        self.findpassword_button_2.show()
        self.return_button.show()

        pass

    def signup_layout(self):
        self.login_button.hide()
        self.findpassword_label.hide()
        self.findpassword_button.hide()
        self.signup_label.hide()
        self.signup_button.hide()
        self.findpassword_button_2.hide()
        self.label_2.hide()

        self.password_box.show()
        self.signup_button_2.show()
        self.return_button.show()

        pass

    def onRegister(self, MainWindow, clientProgram):
        username = self.username_box.text()
        password = self.password_box.text()
        state, _ = clientProgram.Register(username, password)

        if state == ClientProgram.State.SUCCEEDED:
            QMessageBox.about(MainWindow, "", "Đăng ký thành công")
        elif state == ClientProgram.State.FAILED:
            QMessageBox.about(MainWindow, "", "Username đã tồn tại!")
        else:
            QMessageBox.about(MainWindow, "","Lỗi kết nối đến server")

    def returnPassword(self, MainWindow, clientProgram):
        
        self.label_2.show()
        pass

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QWidget()
    ui = LoginWindow()
    clientProgram = ClientProgram()
    ui.setupUI(MainWindow, clientProgram)
    MainWindow.show()
    sys.exit(app.exec_())