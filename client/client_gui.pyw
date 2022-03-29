# -*- coding: utf-8 -*-

import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QMessageBox, QWidget

from client import ClientProgram
from login_window_gui import LoginWindow

class ClientWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.clientProgram = ClientProgram()
    
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        close = QtWidgets.QMessageBox.question(self,
                                     "Thoát",
                                     ("Kết nối vẫn còn hiệu lực. " if self.clientProgram.connected else "") + "Bạn chắc chắn muốn thoát?",
                                      QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QtWidgets.QMessageBox.Yes:
            event.accept()
            if self.clientProgram.connected:
                self.clientProgram.Disconnect()
        else:
            event.ignore()

class ClientUI(object):
    def __init__(self):
        self.MainWindow = ClientWindow()
        
    def Connect(self):
        ip = self.IP_box.text()
        port = int(self.port_box.text())
        
        state = self.MainWindow.clientProgram.Connect(ip, port)
        if state:
            QMessageBox.about(self.MainWindow, "", "Kết nối thành công")
            self.connect_button.hide()
            self.disconnect_button.show()

            login_window_ui = LoginWindow()
            self.loginWindow = QWidget()
            login_window_ui.setupUI(self.loginWindow, self.MainWindow.clientProgram)
            self.loginWindow.show()
        else:
            QMessageBox.about(self.MainWindow, "", "Kết nối thất bại")
    
    def Disconnect(self):
        self.MainWindow.clientProgram.Disconnect()
        self.disconnect_button.hide()
        self.connect_button.show()

    def setupUI(self):
        self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.resize(282, 214)
        _translate = QtCore.QCoreApplication.translate
        self.MainWindow.setWindowTitle(_translate("MainWindow", "Client"))

        self.background_image = QtWidgets.QLabel(self.MainWindow)
        self.background_image.setGeometry(QtCore.QRect(0, 0, 281, 211))
        self.background_image.setStyleSheet("background-color: rgb(238, 255, 238);")
        self.background_image.setText("")
        self.background_image.setScaledContents(True)
        self.background_image.setObjectName("background_image")

        self.IP_box = QtWidgets.QLineEdit(self.MainWindow)
        self.IP_box.setGeometry(QtCore.QRect(40, 90, 201, 41))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.IP_box.setFont(font)
        self.IP_box.setStyleSheet("background-color: rgb(246, 252, 255);")
        self.IP_box.setObjectName("IP_box")
        self.IP_box.setText(_translate("MainWindow", "Nhập IP"))

        self.port_box = QtWidgets.QLineEdit(self.MainWindow)
        self.port_box.setGeometry(QtCore.QRect(40, 150, 101, 41))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.port_box.setFont(font)
        self.port_box.setStyleSheet("background-color: rgb(246, 252, 255);")
        self.port_box.setObjectName("port_box")
        self.port_box.setText(_translate("MainWindow", "Nhập port"))

        self.connect_button = QtWidgets.QPushButton(self.MainWindow, clicked = lambda:self.Connect())
        self.connect_button.setGeometry(QtCore.QRect(160, 150, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.connect_button.setFont(font)
        self.connect_button.setStyleSheet("background-color: rgb(224, 237, 255)")
        self.connect_button.setCheckable(False)
        self.connect_button.setChecked(False)
        self.connect_button.setObjectName("connect_button")
        self.connect_button.setText(_translate("MainWindow", "Kết nối"))

        self.disconnect_button = QtWidgets.QPushButton(self.MainWindow, clicked = lambda:self.Disconnect())
        self.disconnect_button.setGeometry(QtCore.QRect(160, 150, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.disconnect_button.setFont(font)
        self.disconnect_button.setStyleSheet("background-color: rgb(224, 237, 255)")
        self.disconnect_button.setCheckable(False)
        self.disconnect_button.setChecked(False)
        self.disconnect_button.setObjectName("connect_button")
        self.disconnect_button.setText(_translate("MainWindow", "Ngắt"))
        self.disconnect_button.hide()

        self.WELCOME_label = QtWidgets.QLabel(self.MainWindow)
        self.WELCOME_label.setGeometry(QtCore.QRect(40, 20, 201, 51))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.WELCOME_label.setFont(font)
        self.WELCOME_label.setStyleSheet("color: rgb(255, 24, 128);")
        self.WELCOME_label.setAlignment(QtCore.Qt.AlignCenter)
        self.WELCOME_label.setObjectName("WELCOME_label")
        self.WELCOME_label.setText(_translate("MainWindow", "WELCOME"))
        
        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)


if __name__ == "__main__":
    from os import environ

    def suppress_qt_warnings():
        environ["QT_DEVICE_PIXEL_RATIO"] = "0"
        environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        environ["QT_SCREEN_SCALE_FACTORS"] = "1"
        environ["QT_SCALE_FACTOR"] = "1"

    suppress_qt_warnings()

    app = QtWidgets.QApplication(sys.argv)
    ui = ClientUI()
    ui.setupUI()
    ui.MainWindow.show()
    sys.exit(app.exec_())