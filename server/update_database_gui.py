# -*- coding: utf-8 -*-

import datetime
from os import read
import os.path
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets
from server import ServerProgram
import copy

PIC_PATH = os.path.join(Path(__file__).parent.absolute(),"pic")

WEATHER_SET = [
    "",
    "Sunny",
    "Cloudy",
    "Sunny + Cloudy",
    "Rainy",
    "Stormy",
    "Lightning"
]

def ConvertWeatherToInt(string):
    try:
        return WEATHER_SET.index(string)
    except:
        return 0

class UpdateWindow(QtWidgets.QWidget):
    def __init__(self, serverProgram:ServerProgram):
        super().__init__()
        self.serverProgram = serverProgram
        self.modifier = self.serverProgram.EnterEditMode()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        msgBox = QtWidgets.QMessageBox(self)
        msgBox.setWindowTitle("Thoát")
        msgBox.setText(("Dữ liệu có sự thay đổi. " if self.serverProgram.IsWeatherDataChangedSinceLoaded() else "") + "Bạn có muốn lưu dữ liệu?")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Save)

        saveButton = msgBox.button(QtWidgets.QMessageBox.Save)
        saveButton.setText("Lưu")
        disButton = msgBox.button(QtWidgets.QMessageBox.Discard)
        disButton.setText("Không lưu")
        canButton = msgBox.button(QtWidgets.QMessageBox.Cancel)
        canButton.setText("Hủy")

        msgBox.exec_()

        if msgBox.clickedButton() == saveButton:
            event.accept()
            self.serverProgram.ExitEditModeAndReload(True)
            self.modifier = None
        elif msgBox.clickedButton() == disButton:
            event.accept()
            self.serverProgram.ExitEditModeAndReload(False)
            self.modifier = None
        elif msgBox.clickedButton() == canButton:
            event.ignore()

class UpdateDatabase(object):
    def __init__(self, svPro:ServerProgram):
        self.MainWindow = UpdateWindow(svPro)
        self.modifier = self.MainWindow.modifier
        

    def SetUpMainWindow(self):
        self.label.show()
        self.WELCOME_label.show()
        self.function_label.setText("Chọn chức năng")
        self.function_label.show()
        self.insert_database_button.show()
        self.delete_city_button.show()
        self.delete_date_button.show()

        self.return_button.hide()
        self.return_choose_function_button.hide()
        self.check_city_id_button.hide()
        self.city_id_label.hide()
        self.city_id_box.hide()
        self.add_city_button.hide()
        self.city_name_label.hide()
        self.city_name_box.hide()
        self.weather_label.hide()
        self.weather_box.hide()
        self.temperature_label.hide()
        self.temperature_box.hide()
        self.humid_label.hide()
        self.humid_box.hide()
        self.wind_label.hide()
        self.wind_box.hide()
        self.update_database_button.hide()
        self.date_label.hide()
        self.date_box.hide()
        self.insert_one_day_button.hide()
        self.insert_seven_days_button.hide()
        self.weather_table.hide()
        self.add_date_button.hide()

    def chooseFunctionWindow(self):
        self.label.show()
        self.WELCOME_label.show()
        self.function_label.show()

        self.insert_database_button.hide()
        self.delete_city_button.hide()
        self.delete_date_button.hide()
        self.return_choose_function_button.hide()
        self.check_city_id_button.show()
        self.add_city_button.hide()
        self.weather_label.hide()
        self.weather_box.hide()
        self.temperature_label.hide()
        self.temperature_box.hide()
        self.humid_label.hide()
        self.humid_box.hide()
        self.wind_label.hide()
        self.wind_box.hide()
        self.update_database_button.hide()
        self.date_label.hide()
        self.date_box.hide()
        self.weather_table.hide()
        self.add_date_button.hide()
        
        self.city_name_label.show()
        self.city_name_box.show()
        self.return_button.show()
        self.city_id_label.show()
        self.city_id_box.show()
        self.insert_one_day_button.show()
        self.insert_seven_days_button.show()

    def onInsertDatabase(self):
        self.insert_database_button.hide()
        self.delete_city_button.hide()
        self.delete_date_button.hide()
        
        self.function_label.setText("Thêm/Sửa database")
        self.check_city_id_button.show()
        self.return_button.show()
        self.city_id_label.setGeometry(QtCore.QRect(80, 150, 71, 31))
        self.city_id_label.show()
        self.city_id_box.setGeometry(QtCore.QRect(155, 150, 70, 31))
        self.city_id_box.show()
        
    def onCheckID(self):
        id = int(self.city_id_box.text())
        if self.modifier:
            state, city = self.modifier.FetchForcastsByCity(city_id = id, fromDate=None, count=0)
        if self.modifier and state == False:
            self.update_database_button.setText("Thêm/Sửa")
            self.update_database_button.hide()
            self.return_choose_function_button.hide()

            self.add_city_button.show()
            self.city_name_label.show()
            self.city_name_box.show()

            self.date_label.hide()
            self.date_box.hide()
            self.weather_label.hide()
            self.weather_box.hide()
            self.temperature_label.hide()
            self.temperature_box.hide()
            self.humid_label.hide()
            self.humid_box.hide()
            self.wind_label.hide()
            self.wind_box.hide()

        else:
            self.add_city_button.hide()
            self.city_name_label.show()
            self.city_name_box.setText(city[0])
            self.city_name_box.show()
            self.return_choose_function_button.hide()

            self.chooseFunction()

    def addCityName(self):
        city_name = self.city_name_box.text()
        if self.modifier:
            state, city_id = self.modifier.AddCity(city_name=city_name)

        if not self.modifier or state == False:
            QtWidgets.QMessageBox.about(self.MainWindow, "", "Lỗi hệ thống")
        else:
            self.city_id_box.setText(str(city_id))
            self.add_city_button.hide()
            self.return_choose_function_button.hide()
            self.chooseFunction()

    def chooseFunction(self):
        # self.return_choose_function_button.show()
        self.insert_one_day_button.show()
        self.insert_seven_days_button.show()

    def on_insert_one_day(self):
        self.update_database_button.setText("Thêm/Sửa")
        self.update_database_button.clicked.disconnect()
        self.update_database_button.clicked.connect(lambda:self.insert_one_day())
        self.update_database_button.show()
        self.date_label.setGeometry(QtCore.QRect(256, 150, 245, 31))
        self.date_label.show()
        self.date_box.setGeometry(QtCore.QRect(470, 150, 151, 31))
        self.date_box.show()
        self.weather_label.show()
        self.weather_box.show()
        self.temperature_label.show()
        self.temperature_box.show()
        self.humid_label.show()
        self.humid_box.show()
        self.wind_label.show()
        self.wind_box.show()
        self.return_choose_function_button.show()

        self.add_city_button.hide()
        self.city_name_label.hide()
        self.city_name_box.hide()
        self.insert_one_day_button.hide()
        self.insert_seven_days_button.hide()
        
    def on_insert_seven_days(self):
        self.update_database_button.setText("Thêm/Sửa")
        self.update_database_button.clicked.disconnect()
        self.update_database_button.clicked.connect(lambda:self.insert_seven_days())
        self.add_date_button.show()
        self.date_label.setGeometry(QtCore.QRect(256, 150, 245, 31))
        self.date_label.show()
        self.date_box.setGeometry(QtCore.QRect(470, 150, 151, 31))
        ######
        self.date_box.show()
        self.return_choose_function_button.show()

        self.update_database_button.hide()
        self.add_city_button.hide()
        self.city_name_label.hide()
        self.city_name_box.hide()
        self.insert_one_day_button.hide()
        self.insert_seven_days_button.hide()

    def insert_one_day(self):
        city_id = int(self.city_id_box.text())
        date = self.date_box.text()
        if date == 'today':
            date = datetime.date.today()
        else:
            date = datetime.datetime.strptime(date, '%Y/%m/%d').date()
        weather = str(self.weather_box.currentText())
        temperature = float(self.temperature_box.text())
        humidity = float(self.humid_box.text())
        windspeed = float(self.wind_box.text())
        weatherInforTuple = (weather, temperature, humidity, windspeed)

        if self.modifier:
            state = self.modifier.AddForecastByValues(cityid= city_id, date= date, weatherInfoTuple= weatherInforTuple)
        if self.modifier and state:
            QtWidgets.QMessageBox.about(self.MainWindow,"","Thêm/Sửa thành công")
        elif not state:
            QtWidgets.QMessageBox.about(self.MainWindow,"","Thêm/Sửa thất bại")
        else:
            QtWidgets.QMessageBox.about(self.MainWindow,"","Lỗi hệ thống")

    def addDatetoTable(self):
        #self.add_date_button.hide()

        self.weather_table.show()
        self.update_database_button.show()
        date = self.date_box.text()
        if date == 'today':
            date = datetime.date.today()
        else:
            date = datetime.datetime.strptime(date, '%Y/%m/%d')

        try:
            city_id = int(self.city_id_box.text())
            state, readyWeathers = self.modifier.FetchForcastsByCity(city_id, fromDate= (date - datetime.timedelta(days=1)).date())
            print(readyWeathers)
            readyWeathers = readyWeathers[1]
            assert state
        except Exception as e:
            readyWeathers = dict()
            for i in range(7):
                readyWeathers[(date + datetime.timedelta(days=i)).strftime("%Y/%m/%d")] = [None, None, None, None]
            print(readyWeathers)
        
        font = QtGui.QFont()
        font.setFamily("Helvetica")

        for i, adate in enumerate(sorted(readyWeathers)):
            
            item = QtWidgets.QTableWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFont(font)
            item.setText(adate)
            self.weather_table.setItem(i+1, 0, item)
            
            box = self.weatherBoxes[i]
            box.setCurrentIndex(ConvertWeatherToInt(readyWeathers[adate][0]))
            temp = readyWeathers[adate][1]
            humid = readyWeathers[adate][2]
            wind = readyWeathers[adate][3]
            
            j = 2
            for toWrite in (temp, humid, wind):
                item = QtWidgets.QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                item.setFont(font)
                if toWrite:
                    item.setText(str(toWrite))
                self.weather_table.setItem(i+1, j, item)
                j += 1

    def insert_seven_days(self):
        successes = 0
        infoStrings = []
        for i in range(7):
            try:
                city_id = int(self.city_id_box.text())
                date_text = self.weather_table.item(i+1, 0).text()
                date = datetime.datetime.strptime(date_text, '%Y/%m/%d').date()
                weather = str(self.weather_table.cellWidget(i+1, 1).currentText())
                temperature = float(self.weather_table.item(i+1, 2).text())
                humidity = float(self.weather_table.item(i+1, 3).text())
                windspeed = float(self.weather_table.item(i+1, 4).text())
                
                weatherInforTuple = (weather, temperature, humidity, windspeed)
                if self.modifier:
                    state = self.modifier.AddForecastByValues(cityid= city_id, date= date, weatherInfoTuple= weatherInforTuple)
                if self.modifier and state:
                    infoStrings.append(f"Ngày thứ {i + 1}: Thêm thành công ngày {date_text}")
                    successes += 1
                elif not state:
                    infoStrings.append(f"Ngày thứ {i + 1}: Lỗi: Không thể thêm/sửa dữ liệu ngày {date_text}")
                else:
                    infoStrings.append(f"Ngày thứ {i + 1}: Lỗi hệ thống")
            except:
                infoStrings.append(f"Ngày thứ {i + 1}: Lỗi: Dữ liệu không hợp lệ.")
                continue

        QtWidgets.QMessageBox.about(self.MainWindow, f"Thành công: {successes}/7",'\n'.join(infoStrings))
        
    def onDeleteCity(self):
        self.function_label.setText("Xóa database")
        self.insert_database_button.hide()
        self.delete_city_button.hide()
        self.delete_date_button.hide()
        
        self.check_city_id_button.hide()
        self.return_button.hide()
        self.city_name_label.hide()
        self.city_name_box.hide()
        self.weather_label.hide()
        self.weather_box.hide()
        self.temperature_label.hide()
        self.temperature_box.hide()
        self.humid_label.hide()
        self.humid_box.hide()
        self.wind_label.hide()
        self.wind_box.hide()
        self.date_label.hide()
        self.date_box.hide()

        self.city_id_label.setGeometry(QtCore.QRect(290, 190, 71, 31))
        self.city_id_label.show()
        self.city_id_box.setGeometry(QtCore.QRect(370, 190, 61, 31))
        self.city_id_box.show()
        self.update_database_button.setText("Xóa")
        self.update_database_button.clicked.disconnect()
        self.update_database_button.clicked.connect(lambda:self.deleteCity())
        self.update_database_button.show()
        self.return_button.show()
        
    def deleteCity(self):
        city_id = int(self.city_id_box.text())
        if self.modifier:
            state = self.modifier.RemoveCity(cityid=city_id)

        if self.modifier and state:
            QtWidgets.QMessageBox.about(self.MainWindow, "", "Xóa thành công")
        elif not state:
            QtWidgets.QMessageBox.about(self.MainWindow, "", "Xóa thất bại")
        else:
            QtWidgets.QMessageBox.about(self.MainWindow,"","Lỗi hệ thống")

    def onDeleteDate(self):
        self.function_label.setText("Xóa database")
        self.insert_database_button.hide()
        self.delete_city_button.hide()
        self.delete_date_button.hide()
        
        self.check_city_id_button.hide()
        self.return_button.hide()
        self.city_name_label.hide()
        self.city_name_box.hide()
        self.weather_label.hide()
        self.weather_box.hide()
        self.temperature_label.hide()
        self.temperature_box.hide()
        self.humid_label.hide()
        self.humid_box.hide()
        self.wind_label.hide()
        self.wind_box.hide()

        self.date_label.setGeometry(QtCore.QRect(160, 230, 211, 31))
        self.date_label.show()
        self.date_box.setGeometry(QtCore.QRect(370, 230, 131, 31))
        self.date_box.show()
        self.city_id_label.setGeometry(QtCore.QRect(290, 190, 71, 31))
        self.city_id_label.show()
        self.city_id_box.setGeometry(QtCore.QRect(370, 190, 61, 31))
        self.city_id_box.show()
        self.update_database_button.setText("Xóa")
        self.update_database_button.clicked.disconnect()
        self.update_database_button.clicked.connect(lambda:self.deleteDate())
        self.update_database_button.show()
        self.return_button.show()
        
    def deleteDate(self):
        city_id = int(self.city_id_box.text())
        date = self.date_box.text()
        if date == 'today':
            date = datetime.date.today()
        else:
            date = datetime.datetime.strptime(date, '%Y/%m/%d')
        
        if self.modifier:
            state = self.modifier.RemoveCity(cityid=city_id)

        if self.modifier and state:
            QtWidgets.QMessageBox.about(self.MainWindow, "", "Xóa thành công")
        elif not state:
            QtWidgets.QMessageBox.about(self.MainWindow, "", "Xóa thất bại")
        else:
            QtWidgets.QMessageBox.about(self.MainWindow,"","Lỗi hệ thống")


    def setupUI(self):
        self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.resize(670, 350)

        self.label = QtWidgets.QLabel(self.MainWindow)
        self.label.setGeometry(QtCore.QRect(0, 0, 671, 351))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(os.path.join(PIC_PATH, "sv.png")))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")

        self.WELCOME_label = QtWidgets.QLabel(self.MainWindow)
        self.WELCOME_label.setGeometry(QtCore.QRect(130, 40, 421, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.WELCOME_label.setFont(font)
        self.WELCOME_label.setStyleSheet("color: rgb(255, 127, 41);")
        self.WELCOME_label.setAlignment(QtCore.Qt.AlignCenter)
        self.WELCOME_label.setObjectName("WELCOME_label")

        self.function_label = QtWidgets.QLabel(self.MainWindow)
        self.function_label.setGeometry(QtCore.QRect(130, 90, 421, 41))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.function_label.setFont(font)
        self.function_label.setStyleSheet("color: rgb(255, 207, 152)")
        self.function_label.setAlignment(QtCore.Qt.AlignCenter)
        self.function_label.setObjectName("function_label")

        self.insert_database_button = QtWidgets.QPushButton(self.MainWindow, clicked = lambda:self.onInsertDatabase())
        self.insert_database_button.setGeometry(QtCore.QRect(90, 150, 131, 141))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.insert_database_button.setFont(font)
        self.insert_database_button.setObjectName("insert_database_button")

        self.delete_city_button = QtWidgets.QPushButton(self.MainWindow, clicked = lambda:self.onDeleteCity())
        self.delete_city_button.setGeometry(QtCore.QRect(270, 150, 131, 141))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.delete_city_button.setFont(font)
        self.delete_city_button.setObjectName("delete_city_button")

        self.delete_date_button = QtWidgets.QPushButton(self.MainWindow, clicked = lambda:self.onDeleteDate())
        self.delete_date_button.setGeometry(QtCore.QRect(450, 150, 131, 141))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(12)
        self.delete_date_button.setFont(font)
        self.delete_date_button.setObjectName("delete_date_button")

        self.update_database_button = QtWidgets.QPushButton(self.MainWindow)
        self.update_database_button.setGeometry(QtCore.QRect(290, 305, 93, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.update_database_button.setFont(font)
        self.update_database_button.setStyleSheet("")
        self.update_database_button.setObjectName("update_database_button")
        self.update_database_button.clicked.connect(lambda:self.insert_one_day())
        self.update_database_button.clicked.connect(lambda:self.deleteCity())
        self.update_database_button.clicked.connect(lambda:self.deleteDate())

        self.return_button = QtWidgets.QPushButton(self.MainWindow, clicked = lambda:self.SetUpMainWindow())
        self.return_button.setGeometry(QtCore.QRect(592, 110, 71, 28))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.return_button.setFont(font)
        self.return_button.setStyleSheet("color: rgb(183, 255, 189);")
        self.return_button.setFlat(True)
        self.return_button.setObjectName("return_button")

        self.return_choose_function_button = QtWidgets.QPushButton(self.MainWindow, clicked = lambda:self.chooseFunctionWindow())
        self.return_choose_function_button.setGeometry(QtCore.QRect(592, 110, 71, 28))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.return_choose_function_button.setFont(font)
        self.return_choose_function_button.setStyleSheet("color: rgb(183, 255, 189);")
        self.return_choose_function_button.setFlat(True)
        self.return_choose_function_button.setObjectName("return_choose_function_button")

        self.check_city_id_button = QtWidgets.QPushButton(self.MainWindow, clicked = lambda:self.onCheckID())
        self.check_city_id_button.setGeometry(QtCore.QRect(10, 150, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setItalic(True)
        font.setPointSize(10)
        self.check_city_id_button.setFont(font)
        self.check_city_id_button.setStyleSheet("color: rgb(183, 255, 189);")
        self.check_city_id_button.setFlat(True)
        self.check_city_id_button.setObjectName("check_city_id_button")

        self.city_id_label = QtWidgets.QLabel(self.MainWindow)
        self.city_id_label.setGeometry(QtCore.QRect(80, 150, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.city_id_label.setFont(font)
        self.city_id_label.setStyleSheet("color:rgb(85, 255, 0)")
        self.city_id_label.setObjectName("city_id_label")

        self.add_city_button = QtWidgets.QPushButton(self.MainWindow, clicked = lambda:self.addCityName())
        self.add_city_button.setGeometry(QtCore.QRect(10, 190, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setItalic(True)
        font.setPointSize(10)
        self.add_city_button.setFont(font)
        self.add_city_button.setStyleSheet("color: rgb(183, 255, 189);")
        self.add_city_button.setFlat(True)
        self.add_city_button.setObjectName("add_city_button")

        self.city_name_label = QtWidgets.QLabel(self.MainWindow)
        self.city_name_label.setGeometry(QtCore.QRect(80, 190, 245, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.city_name_label.setFont(font)
        self.city_name_label.setStyleSheet("color:rgb(85, 255, 0)")
        self.city_name_label.setObjectName("city_name_label")
        
        self.weather_label = QtWidgets.QLabel(self.MainWindow)
        self.weather_label.setGeometry(QtCore.QRect(80, 190, 111, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.weather_label.setFont(font)
        self.weather_label.setStyleSheet("color:rgb(85, 255, 0)")
        self.weather_label.setObjectName("weather_label")

        self.temperature_label = QtWidgets.QLabel(self.MainWindow)
        self.temperature_label.setGeometry(QtCore.QRect(80, 230, 111, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.temperature_label.setFont(font)
        self.temperature_label.setStyleSheet("color:rgb(85, 255, 0)")
        self.temperature_label.setObjectName("temperature_label")

        self.humid_label = QtWidgets.QLabel(self.MainWindow)
        self.humid_label.setGeometry(QtCore.QRect(260, 230, 101, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.humid_label.setFont(font)
        self.humid_label.setStyleSheet("color:rgb(85, 255, 0)")
        self.humid_label.setObjectName("humid_label")

        self.wind_label = QtWidgets.QLabel(self.MainWindow)
        self.wind_label.setGeometry(QtCore.QRect(425, 230, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.wind_label.setFont(font)
        self.wind_label.setStyleSheet("color:rgb(85, 255, 0)")
        self.wind_label.setObjectName("wind_label")

        self.city_id_box = QtWidgets.QLineEdit(self.MainWindow)
        self.city_id_box.setGeometry(QtCore.QRect(160, 150, 70, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.city_id_box.setFont(font)
        self.city_id_box.setAlignment(QtCore.Qt.AlignCenter)
        self.city_id_box.setObjectName("city_id_box")

        self.city_name_box = QtWidgets.QLineEdit(self.MainWindow)
        self.city_name_box.setGeometry(QtCore.QRect(335, 190, 135, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.city_name_box.setFont(font)
        self.city_name_box.setAlignment(QtCore.Qt.AlignCenter)
        self.city_name_box.setObjectName("city_name_box")

        self.weather_box = QtWidgets.QComboBox(self.MainWindow)
        self.weather_box.setGeometry(QtCore.QRect(200, 190, 161, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.weather_box.setFont(font)
        self.weather_box.setMaxVisibleItems(7)
        self.weather_box.setObjectName("weather_box")
        self.weather_box.addItem("")
        self.weather_box.addItem("")
        self.weather_box.addItem("")
        self.weather_box.addItem("")
        self.weather_box.addItem("")
        self.weather_box.addItem("")
        self.weather_box.addItem("")
        self.weather_box.setCurrentIndex(0)

        self.temperature_box = QtWidgets.QLineEdit(self.MainWindow)
        self.temperature_box.setGeometry(QtCore.QRect(195, 230, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.temperature_box.setFont(font)
        self.temperature_box.setAlignment(QtCore.Qt.AlignCenter)
        self.temperature_box.setObjectName("temperature_box")

        self.humid_box = QtWidgets.QLineEdit(self.MainWindow)
        self.humid_box.setGeometry(QtCore.QRect(362, 230, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.humid_box.setFont(font)
        self.humid_box.setAlignment(QtCore.Qt.AlignCenter)
        self.humid_box.setObjectName("humid_box")

        self.wind_box = QtWidgets.QLineEdit(self.MainWindow)
        self.wind_box.setGeometry(QtCore.QRect(550, 230, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.wind_box.setFont(font)
        self.wind_box.setAlignment(QtCore.Qt.AlignCenter)
        self.wind_box.setObjectName("wind_box")

        self.date_label = QtWidgets.QLabel(self.MainWindow)
        self.date_label.setGeometry(QtCore.QRect(160, 230, 211, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.date_label.setFont(font)
        self.date_label.setStyleSheet("color:rgb(85, 255, 0)")
        self.date_label.setObjectName("date_label")

        self.date_box = QtWidgets.QLineEdit(self.MainWindow)
        self.date_box.setGeometry(QtCore.QRect(370, 230, 131, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.date_box.setFont(font)
        self.date_box.setAlignment(QtCore.Qt.AlignCenter)
        self.date_box.setObjectName("date_box")

        self.add_date_button = QtWidgets.QPushButton(self.MainWindow, clicked = lambda:self.addDatetoTable())
        self.add_date_button.setGeometry(QtCore.QRect(550, 190, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setItalic(True)
        font.setPointSize(10)
        self.add_date_button.setFont(font)
        self.add_date_button.setStyleSheet("color: rgb(183, 255, 189);")
        self.add_date_button.setFlat(True)
        self.add_date_button.setObjectName("add_date_button")

        _translate = QtCore.QCoreApplication.translate
        self.MainWindow.setWindowTitle(_translate("MainWindow", "Update Database"))
        self.WELCOME_label.setText(_translate("MainWindow", "WELCOME ADMIN"))
        self.function_label.setText(_translate("MainWindow", "Chọn chức năng"))
        self.insert_database_button.setText(_translate("MainWindow", "Thêm/Sửa\nDatabase"))
        self.delete_city_button.setText(_translate("MainWindow", "Xóa thông tin\ncủa\nthành phố"))
        self.delete_date_button.setText(_translate("MainWindow", "Xóa thông tin\nmột ngày của\nthành phố"))
        self.update_database_button.setText(_translate("MainWindow", "Thêm/Xóa"))
        self.return_button.setText(_translate("MainWindow", "Return"))
        self.return_choose_function_button.setText(_translate("MainWindow", "Return"))
        self.check_city_id_button.setText(_translate("Main Window", "Check"))
        self.city_id_label.setText(_translate("MainWindow", "ID:"))
        self.add_city_button.setText(_translate("Main Window", "Thêm"))
        self.city_name_label.setText(_translate("MainWindow", "Tên thành phố (không dấu):"))
        self.weather_label.setText(_translate("MainWindow", "Chọn thời tiết:"))
        self.temperature_label.setText(_translate("MainWindow", "Nhập nhiệt độ:"))
        self.humid_label.setText(_translate("MainWindow", "Nhập độ ẩm:"))
        self.wind_label.setText(_translate("MainWindow", "Nhập tốc độ gió:"))
        self.city_id_box.setText(_translate("MainWindow", "12345"))
        self.city_name_box.setText(_translate("MainWindow", ""))

        for i in range(len(WEATHER_SET)):
            self.weather_box.setItemText(i, _translate("MainWindow", WEATHER_SET[i]))

        self.temperature_box.setText(_translate("MainWindow", "30"))
        self.humid_box.setText(_translate("MainWindow", "0.7"))
        self.wind_box.setText(_translate("MainWindow", "99.5"))
        self.date_label.setText(_translate("MainWindow", "Nhập ngày (yyyy/mm/dd):"))
        self.date_box.setText(_translate("MainWindow", datetime.date.today().strftime('%Y/%m/%d')))
        self.add_date_button.setText(_translate("MainWindow", "Thêm"))

        self.insert_one_day_button = QtWidgets.QPushButton(self.MainWindow, clicked = lambda:self.on_insert_one_day())
        self.insert_one_day_button.setGeometry(QtCore.QRect(80, 230, 220, 100))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.insert_one_day_button.setFont(font)
        self.insert_one_day_button.setObjectName("insert_one_day_button")
        self.insert_one_day_button.setText("Thêm/Sửa thông tin\ncủa một ngày")

        self.insert_seven_days_button = QtWidgets.QPushButton(self.MainWindow, clicked = lambda:self.on_insert_seven_days())
        self.insert_seven_days_button.setGeometry(QtCore.QRect(370, 230, 220, 100))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.insert_seven_days_button.setFont(font)
        self.insert_seven_days_button.setObjectName("insert_seven_days_button")
        self.insert_seven_days_button.setText("Thêm/Sửa thông tin\nbảy ngày liên tiếp")

        self.weather_table = QtWidgets.QTableWidget(self.MainWindow)
        self.weather_table.setGeometry(QtCore.QRect(40, 186, 590, 116))
        self.weather_table.setMinimumSize(QtCore.QSize(590, 0))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(9)
        self.weather_table.setFont(font)
        self.weather_table.setRowCount(8)
        self.weather_table.setColumnCount(5)
        self.weather_table.setObjectName("weather_table")
        
        for i in range(8):
            for j in range(5):
                item = QtWidgets.QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                font = QtGui.QFont()
                font.setFamily("Helvetica")
                font.setPointSize(9)
                item.setFont(font)
                self.weather_table.setItem(i, j, item)
        self.weatherBoxes = []
        for i in range(7):
            weatherBox = QtWidgets.QComboBox(self.weather_table)
            weatherBox.setFont(font)
            weatherBox.setMaxVisibleItems(7)
            weatherBox.setObjectName("weather_box")
            weatherBox.addItems(WEATHER_SET)
            weatherBox.setCurrentIndex(0)
            weatherBox.setStyleSheet("background-color: rgb(255, 255, 255);")
            self.weather_table.setCellWidget(i+1, 1, weatherBox)
            self.weatherBoxes.append(weatherBox)

        self.weather_table.horizontalHeader().setVisible(False)
        self.weather_table.horizontalHeader().setCascadingSectionResizes(True)
        self.weather_table.horizontalHeader().setHighlightSections(False)
        self.weather_table.horizontalHeader().setStretchLastSection(True)
        self.weather_table.verticalHeader().setVisible(False)
        self.weather_table.verticalHeader().setCascadingSectionResizes(False)
        self.weather_table.verticalHeader().setHighlightSections(True)
        self.weather_table.verticalHeader().setMinimumSectionSize(10)
        self.weather_table.verticalHeader().setSortIndicatorShown(False)
        self.weather_table.verticalHeader().setStretchLastSection(False)
        self.weather_table.setColumnWidth(0, 100)
        self.weather_table.setColumnWidth(1, 120)
        self.weather_table.setColumnWidth(2, 130)
        self.weather_table.setColumnWidth(3, 90)
        self.weather_table.setColumnWidth(4, 90)
        for i in range(8):
            self.weather_table.setRowHeight(i, 10)
        __sortingEnabled = self.weather_table.isSortingEnabled()
        self.weather_table.setSortingEnabled(False)
        item = self.weather_table.item(0, 0)
        item.setText(_translate("MainWindow", "Date"))
        item = self.weather_table.item(0, 1)
        item.setText(_translate("MainWindow", "Weather"))
        item = self.weather_table.item(0, 2)
        item.setText(_translate("MainWindow", "Temperature"))
        item = self.weather_table.item(0, 3)
        item.setText(_translate("MainWindow", "Humidity"))
        item = self.weather_table.item(0, 4)
        item.setText(_translate("MainWindow", "Wind Speed"))
        self.weather_table.setSortingEnabled(__sortingEnabled)
        self.weather_table.resizeRowsToContents()

        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)
        self.SetUpMainWindow()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = UpdateDatabase()
    ui.setupUI()
    sys.exit(app.exec_())