from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QLineEdit
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
        uic.loadUi(join(UI, "map_output_extra5.ui"), self)

        self.find_b.clicked.connect(self.find_place)
        self.find_b.setAutoDefault(True)
        self.place_input.returnPressed.connect(self.find_b.click)

        self.index_b.clicked.connect(self.ch_ind)

        self.clear_b.clicked.connect(self.cancel)
        self.index_b.clicked.connect(self.index)
        self.hybrid_rb.toggled.connect(self.hybrid)
        self.satellite_rb.toggled.connect(self.satellite)
        self.scheme_rb.toggled.connect(self.scheme)
        self.X_LINE = 10
        self.Y_LINE = 220
        self.sc = False
        self.hyb = False
        self.sat = False

        self.chc = 1

    def find_place(self):
        res = listdir((RESULTS))
        if len(res) > 1:
            path = os.path.join(RESULTS, res[1])
            os.remove(path)
        self.place = self.place_input.text()
        if self.place == "":
            return
        self.form_map()
        if self.sc:
            self.map_api.set_style("map")
        elif self.sat:
            self.map_api.set_style("sat")
        elif self.hyb:
            self.map_api.set_style("sat,trf")
        else:
            self.map_api.set_style("map")

        self.index()
        self.update2()

    def index(self):
        print(self.chc, "показатель передан")
        if self.chc % 2 == 0:
            ad = " ".join(list(map(str, self.map_api.get_full_data().values())))
            self.index_b.setText("Скрыть индекс")
        else:
            ad = " ".join(list(map(str, self.map_api.get_full_data().values()))[:-1])
            self.index_b.setText("Показать индекс")
        self.adress_d.setText(ad)

    def ch_ind(self):
        self.chc += 1
        print(self.chc, "показатель изменён")
        self.index()

    def form_map(self):
        self.map_api = MapAPI(self.place)
        self.map_api.set_zoom(10)
        self.name = f"map_{str(len(listdir(RESULTS)) + 1)}.png"
        place = self.place
        self.map_api.add_pin(place)

    def update2(self):
        img = Image.open(self.map_api.get_image())
        img.save(join(split(getcwd())[0], f"results/{self.name}"))

        label_pixmap = QPixmap(join(split(getcwd())[0], f"results/{self.name}"))
        self.map_d.setPixmap(label_pixmap)

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

    def mousePressEvent(self, event):
        self.place_input.clearFocus()
        # if event.buttons() == QtCore.Qt.RightButton:
        #     print(self.map_api.add_pin_by_right_click(event.pos().x() - self.X_LINE, event.pos().y() - self.Y_LINE))
        #     self.map_api.clear_pin()
        #     self.map_api.add_pin_by_right_click(event.pos().x() - self.X_LINE, event.pos().y() - self.Y_LINE)
        #     adr = list((self.map_api.add_pin_by_right_click(event.pos().x() - self.X_LINE, event.pos().y() - self.Y_LINE)).values())
        #     self.adress_d.setText(" ".join(adr))
        #     self.place_input.clear()
        #     self.update2()

        if event.buttons() == QtCore.Qt.LeftButton:
            print(self.map_api.add_pin_by_left_click(event.pos().x() - self.X_LINE, event.pos().y() - self.Y_LINE))
            self.map_api.clear_pin()
            self.map_api.add_pin_by_left_click(event.pos().x() - self.X_LINE, event.pos().y() - self.Y_LINE)
            adr = list((self.map_api.add_pin_by_left_click(event.pos().x() - self.X_LINE, event.pos().y() - self.Y_LINE)).values())
            self.adress_d.setText(" ".join(adr))
            self.place_input.clear()
            self.update2()

    def scheme(self):
        self.sat = False
        self.hyb = False
        self.sc = True

    def satellite(self):
        self.hyb = False
        self.sc = False
        self.sat = True

    def hybrid(self):
        self.sat = False
        self.sc = False
        self.hyb = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MapDisplay()
    ex.show()
    sys.exit(app.exec_())
