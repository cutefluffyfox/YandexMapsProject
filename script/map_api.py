from io import BytesIO
import requests
from pprint import pprint


class MapAPI:
    geocode_server = "http://geocode-maps.yandex.ru/1.x/"
    geocode_token = "40d1649f-0493-4b70-98ba-98533de7710b"
    maps_api_server = "http://static-maps.yandex.ru/1.x/"
    search_api_server = "https://search-maps.yandex.ru/v1/"
    search_api_token = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    def __init__(self, address: str, map_size="650,450"):
        self.address = ""
        self.map_size = map_size
        self.__json = dir()
        self.__object_json = dict()
        self.__cords = ""
        self.__zoom = 2
        self.__style = "map"
        self.__pin = []
        self.__image = None
        self.set_address(address)

    def set_address(self, address: str):
        self.address = address
        self.__json = self.__get_json(self.address)
        self.__object_json = self.__get_object_json(self.__json)
        self.__cords = self.__get_cords(self.__object_json)
        self.__zoom = 2
        self.__pin = []
        self.__image = None
        self.__image = self.get_image()

    def set_map_size(self, map_size: str):
        self.map_size = map_size

    def add_pin(self, address: str, pin_style="pm2rdm"):
        self.__pin.append(self.__get_cords(self.__get_object_json(self.__get_json(address))) + "," + pin_style)

    def clear_pin(self):
        self.__pin.clear()

    def get_image(self) -> BytesIO:
        params = {
            "ll": self.__cords,
            "l": self.__style,
            "pt": "~".join(self.__pin),
            "z": self.__zoom,
            "size": self.map_size,
        }
        response = requests.get(self.maps_api_server, params=params)
        if response.status_code == 200:
            self.__image = BytesIO(response.content)
        return self.__image

    def zoom_in(self, delta: int):
        self.set_zoom(int(self.__zoom) + delta)

    def set_zoom(self, new_zoom: int):
        if 2 <= new_zoom <= 18:
            self.__zoom = new_zoom

    def move_up(self, y=None):
        self.__move(0, self.__auto_change() if y is None else y)

    def move_down(self, y=None):
        self.__move(0, -self.__auto_change() if y is None else -y)

    def move_right(self, x=None):
        self.__move(self.__auto_change() if x is None else x, 0)

    def move_left(self, x=None):
        self.__move(-self.__auto_change() if x is None else -x, 0)

    def set_style(self, style: str):
        if self.__is_ok(style=style):
            self.__style = style

    @staticmethod
    def easy_pin(color: str) -> str:
        return ",pm2" + color + "m"

    def get_full_data(self) -> dict:
        object_json = self.__get_object_json(self.__get_json(self.__cords))
        return {
            "address": object_json['metaDataProperty']['GeocoderMetaData']['Address']['formatted'],
            "postal_code": object_json['metaDataProperty']['GeocoderMetaData']['Address']['postal_code'],
        }

    def __get_json(self, address: str) -> dict:
        params = {
            "apikey": self.geocode_token,
            "geocode": address,
            "format": "json"
        }
        return requests.get(self.geocode_server, params).json()

    @staticmethod
    def __get_object_json(json: dict) -> dict:
        return json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']

    @staticmethod
    def __get_cords(object_json: dict) -> str:
        return object_json['Point']['pos'].replace(" ", ",")

    def __move(self, x=0, y=0):
        new_cords = self.__str_to_list(self.__cords)
        new_cords = self.__list_to_str([new_cords[0] + x, new_cords[1] + y])
        if self.__is_ok(cords=new_cords, zoom=self.__zoom, pin=self.__pin):
            self.__cords = new_cords

    def __is_ok(self, cords=None, zoom=None, style="map", pin=None) -> bool:
        if cords is None:
            cords = self.__cords
        params = {
            "ll": cords,
            "l": style,
            "pt": pin,
            "z": zoom,
        }
        response = requests.get(self.maps_api_server, params=params)
        return response.status_code == 200

    def __auto_change(self) -> float:
        return 0.0006 * pow(2, 18 - self.__zoom)

    @staticmethod
    def __str_to_list(data: str) -> [float, float]:
        return list(map(float, data.split(",")))

    @staticmethod
    def __list_to_str(data: [float, float]) -> str:
        return f"{data[0]},{data[1]}"

    def __auto_spn(self) -> str:
        lower = self.__str_to_list(self.__object_json['boundedBy']['Envelope']['lowerCorner'].replace(" ", ","))
        upper = self.__str_to_list(self.__object_json['boundedBy']['Envelope']['upperCorner'].replace(" ", ","))
        return f"{abs(upper[0] - lower[0])},{abs(upper[1] - lower[1])}"


def debug():
    from PIL import Image
    # нацеливаемся на адресс
    map_api = MapAPI("Океанский просп., 17, Владивосток")
    map_api.set_zoom(18)
    Image.open(map_api.get_image()).show()

    # чуть сдвигаем, меняем на спутник, добавляем 2 точки и отдаляемся
    map_api.move_up()
    map_api.move_right()
    map_api.set_style("sat")
    map_api.zoom_in(-1)
    map_api.add_pin("некрасовская 50")
    map_api.add_pin("некрасовская 48А")
    Image.open(map_api.get_image()).show()

    # убираем точки и меняем на карту
    map_api.clear_pin()
    map_api.set_style("map")
    Image.open(map_api.get_image()).show()

    # получение информации об объекте
    pprint(map_api.get_full_data())


if __name__ == '__main__':
    debug()
