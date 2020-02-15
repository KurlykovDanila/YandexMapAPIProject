import os
import sys
import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt


# Hello there


class Map(QMainWindow):
    def __init__(self):
        super().__init__()
        self.coordinates = ['82.920430', '55.030199']
        self.scale = 10
        self.step = 360 / (2 ** self.scale)
        self.map_type = "map"
        self.map_file = None
        self.point = None
        self.init_ui()

    def get_address(self):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": self.lineAddress.text(),
            "format": "json"}
        response = requests.get(geocoder_api_server, params=geocoder_params)
        if response:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"].split()
            self.coordinates = toponym_coodrinates[:]
            self.point = toponym_coodrinates[:]
            self.scale = self.sbScale.value()
            self.change_map()

    def get_image(self):
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        map_params = {
            "ll": ",".join(self.coordinates),
            "z": str(self.scale),
            "l": self.map_type,
            "size": "450,450"
        }
        if self.point is not None:
            map_params['pt'] = ",".join(self.point) + ',pm2rdm'
        response = requests.get(map_api_server, params=map_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(response.url)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            return
        if self.map_file is not None:
            os.remove(self.map_file)
        if "sat" in self.map_type:
            self.map_file = "map.jpg"
        else:
            self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def change_map(self):
        self.get_image()
        self.mapImg.setPixmap(QPixmap(self.map_file))

    def init_ui(self):
        uic.loadUi('window.ui', self)
        self.change_map()
        self.pbShow.clicked.connect(self.get_coordinates)
        self.pbFind.clicked.connect(self.get_address)
        self.sbScale.setMaximum(20)
        self.sbScale.setMinimum(0)
        self.sbScale.setValue(self.scale)
        self.pbAnnul.clicked.connect(self.cancel)
        self.lineGetX.setText(self.coordinates[0])
        self.lineGetY.setText(self.coordinates[1])
        self.radioLayout.itemAt(0).widget().toggle()
        self.radioLayout.itemAt(0).widget().toggled.connect(
            lambda: self.type_of_map("map" * int(self.radioLayout.itemAt(0).widget().isChecked())))
        self.radioLayout.itemAt(1).widget().toggled.connect(
            lambda: self.type_of_map("sat" * int(self.radioLayout.itemAt(1).widget().isChecked())))
        self.radioLayout.itemAt(2).widget().toggled.connect(
            lambda: self.type_of_map("map,trf,skl" * int(self.radioLayout.itemAt(2).widget().isChecked())))

    def type_of_map(self, text):
        if text != '':
            self.map_type = text
            self.change_map()

    def get_coordinates(self):
        x = self.lineGetX.text().strip()
        try:
            float(x)
        except ValueError:
            return
        y = self.lineGetY.text().strip()
        try:
            float(y)
        except ValueError:
            return
        self.scale = self.sbScale.value()
        self.coordinates = [x, y]
        self.change_map()

    def keyPressEvent(self, button):
        if button.key() == Qt.Key_PageUp:
            self.scale = min(self.scale + 1, 19)
        elif button.key() == Qt.Key_PageDown:
            self.scale = max(self.scale - 1, 0)
        elif button.key() == Qt.Key_Right:
            self.coordinates[0] = str(float(self.coordinates[0]) + self.step)
        elif button.key() == Qt.Key_Left:
            self.coordinates[0] = str(float(self.coordinates[0]) - self.step)
        elif button.key() == Qt.Key_Up:
            self.coordinates[1] = str(float(self.coordinates[1]) + self.step)
        elif button.key() == Qt.Key_Down:
            self.coordinates[1] = str(float(self.coordinates[1]) - self.step)
        else:
            return
        self.lineGetX.setText(self.coordinates[0])
        self.lineGetY.setText(self.coordinates[ 1])
        self.sbScale.setValue(self.scale)
        self.step = 360 / (2 ** (self.scale))
        self.change_map()

    def cancel(self):
        self.labelForInfo.setText("")
        self.lineAddress.setText("")

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.exit(app.exec())
