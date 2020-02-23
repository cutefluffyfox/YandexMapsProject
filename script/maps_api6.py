from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene
import sys
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
        uic.loadUi(join(UI, "map_output_hw2.ui"), self)
        self.find_b.clicked.connect(self.find_place)

        self.hybrid_rb.toggled.connect(self.hybrid)
        self.satellite_rb.toggled.connect(self.satellite)
        self.scheme_rb.toggled.connect(self.scheme)

    def find_place(self):
        self.place = self.place_input.text()
        if self.place == "":
            return
        self.form_map()
        self.update()

    def form_map(self):
        self.map_api = MapAPI(self.place)
        self.map_api.set_zoom(10)
        self.name = f"map_{str(len(listdir(RESULTS)) + 1)}.png"
        place = self.place
        self.map_api.add_pin(place)

    def update(self):
        img = Image.open(self.map_api.get_image())
        img.save(join(split(getcwd())[0], f"results/{self.name}"))
        scene = QGraphicsScene()
        scene.addPixmap(QPixmap(join(split(getcwd())[0], f"results/{self.name}")))
        self.display.setScene(scene)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W: #вверх
            self.map_api.move_up()
            self.update()

        if event.key() == Qt.Key_S: #вниз
            self.map_api.move_down()
            self.update()

        if event.key() == Qt.Key_A: #влево
            self.map_api.move_left()
            self.update()

        if event.key() == Qt.Key_D: #вправо
            self.map_api.move_right()
            self.update()

        if event.key() == Qt.Key_R: #приближение
            self.map_api.zoom_in(1)
            self.update()

        if event.key() == Qt.Key_F: #отдаление
            self.map_api.zoom_in(-1)
            self.update()

    def scheme(self):
        self.map_api.set_style("map")
        self.update()

    def satellite(self):
        self.map_api.set_style("sat")
        self.update()

    def hybrid(self):
        self.map_api.set_style("sat,trf")
        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MapDisplay()
    ex.show()
    sys.exit(app.exec_())
