from PyQt5 import uic
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

        map_api = MapAPI("Океанский просп., 17, Владивосток")
        map_api.set_zoom(18)
        name = f"map_{str(len(listdir(RESULTS)) + 1)}.png"

        img = Image.open(map_api.get_image())
        img.save(join(split(getcwd())[0], f"results/{name}"))

        scene = QGraphicsScene()
        scene.addPixmap(QPixmap(join(split(getcwd())[0], f"results/{name}")))
        self.display.setScene(scene)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MapDisplay()
    ex.show()
    sys.exit(app.exec_())
