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
        uic.loadUi(join(UI, "map_output.ui"), self)
        self.map_api = MapAPI("Океанский просп., 17, Владивосток")
        self.map_api.set_zoom(10)
        self.name = f"map_{str(len(listdir(RESULTS)) + 1)}.png"
        self.update()

    def update(self):
        img = Image.open(self.map_api.get_image())
        img.save(join(split(getcwd())[0], f"results/{self.name}"))
        scene = QGraphicsScene()
        scene.addPixmap(QPixmap(join(split(getcwd())[0], f"results/{self.name}")))
        self.display.setScene(scene)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W: #приближение
            self.map_api.zoom_in(1)
            self.update()

        if event.key() == Qt.Key_S: #отдаление
            self.map_api.zoom_in(-1)
            self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MapDisplay()
    ex.show()
    sys.exit(app.exec_())
