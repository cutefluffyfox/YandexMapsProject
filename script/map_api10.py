from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene
import sys
import os
from os import getcwd, listdir
from os.path import join, split
from PyQt5.QtGui import QPixmap
UI = join(split(getcwd())[0], "ui")
from script.map_api import MapAPI
from PIL import Image

RESULTS = join(split(getcwd())[0], "results")


class MapDisplay(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(join(UI, "map_output_extra4.ui"), self)
        self.find_b.clicked.connect(self.find_place)
        self.clear_b.clicked.connect(self.cancel)
        self.index_b.clicked.connect(self.index)
        self.hybrid_rb.toggled.connect(self.hybrid)
        self.satellite_rb.toggled.connect(self.satellite)
        self.scheme_rb.toggled.connect(self.scheme)

        self.chc = 1

    def find_place(self):
        res = listdir((RESULTS))
        print(res, "до")
        if len(res) > 1:
            path = os.path.join(RESULTS, res[1])
            os.remove(path)
        print(res, "после")
        self.place = self.place_input.text()
        if self.place == "":
            return
        self.form_map()
        self.update2()
        self.index()

    def index(self):
        self.chc += 1
        if self.chc % 2 == 0:
            ad = " ".join(list(map(str, self.map_api.get_full_data().values())))
            self.index_b.setText("Скрыть индекс")
        else:
            ad = " ".join(list(map(str, self.map_api.get_full_data().values()))[:-1])
            self.index_b.setText("Показать индекс")

        self.adress_d.setText(ad)

    def paintEvent(self, QPaintEvent):
        self.update()

    def form_map(self):
        self.map_api = MapAPI(self.place)
        self.map_api.set_zoom(10)
        self.name = f"map_{str(len(listdir(RESULTS)) + 1)}.png"
        place = self.place
        self.map_api.add_pin(place)

    def update2(self):
        img = Image.open(self.map_api.get_image())
        img.save(join(split(getcwd())[0], f"results/{self.name}"))
        self.scene = QGraphicsScene()
        self.scene.addPixmap(QPixmap(join(split(getcwd())[0], f"results/{self.name}")))
        self.display.setScene(self.scene)

    def cancel(self):
        self.place_input.clear()
        self.map_api.clear_pin()
        self.place = ''
        self.adress_d.setText("                                                                  ")
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:  # вверх
            self.map_api.move_up()
            self.update2()

        if event.key() == Qt.Key_S:  # вниз
            self.map_api.move_down()
            self.update2()

        if event.key() == Qt.Key_A:  # влево
            self.map_api.move_left()
            self.update2()

        if event.key() == Qt.Key_D:  # вправо
            self.map_api.move_right()
            self.update2()

        if event.key() == Qt.Key_R:  # приближение
            self.map_api.zoom_in(1)
            self.update2()

        if event.key() == Qt.Key_F:  # отдаление
            self.map_api.zoom_in(-1)
            self.update2()

    def scheme(self):
        self.find_place()
        if self.place == "":
            return
        self.map_api.set_style("map")
        self.update2()

    def satellite(self):
        self.find_place()
        if self.place == "":
            return
        self.map_api.set_style("sat")
        self.update2()

    def hybrid(self):
        self.find_place()
        if self.place == "":
            return
        self.map_api.set_style("sat,trf")
        self.update2()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MapDisplay()
    ex.show()
    sys.exit(app.exec_())
