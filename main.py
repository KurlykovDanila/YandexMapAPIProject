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
        self.init_ui()

    def get_image(self):
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        map_params = {
            "ll": ",".join(self.coordinates),
            "z": str(self.scale),
            "l": "map"
        }
        response = requests.get(map_api_server, params=map_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(response.url)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            return

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def change_map(self):
        self.get_image()
        self.pixmap = QPixmap(self.map_file)
        self.mapImg.setPixmap(self.pixmap)

    def init_ui(self):
        uic.loadUi('window.ui', self)
        self.change_map()
        self.pbShow.clicked.connect(self.get_coordinates)

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
        self.coordinates = [x, y]
        self.change_map()

    def keyPressEvent(self, button):
        if button.key() == Qt.Key_PageUp:
            self.scale = min(self.scale + 1, 20)
        elif button.key() == Qt.Key_PageDown:
            self.scale = max(self.scale - 1, 0)
        else:
            return
        self.change_map()

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.exit(app.exec())
