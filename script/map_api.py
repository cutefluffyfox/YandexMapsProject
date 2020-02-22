from io import BytesIO
import requests


class MapAPI:
    geocode_server = "http://geocode-maps.yandex.ru/1.x/"
    geocode_token = "40d1649f-0493-4b70-98ba-98533de7710b"
    maps_api_server = "http://static-maps.yandex.ru/1.x/"

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
        self.__update_image()

    def set_map_size(self, map_size: str):
        self.map_size = map_size

    def __get_json(self, address: str):
        params = {
            "apikey": self.geocode_token,
            "geocode": address,
            "format": "json"
        }
        return requests.get(self.geocode_server, params).json()

    @staticmethod
    def __get_object_json(json: dict):
        return json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']

    @staticmethod
    def __get_cords(object_json: dict) -> str:
        return object_json['Point']['pos'].replace(" ", ",")

    def __update_image(self):
        params = {
            "ll": self.__cords,
            "l": self.__style,
            "pt": "~".join(self.__pin),
            "z": self.__zoom,
            "size": "650,450",
        }
        response = requests.get(self.maps_api_server, params=params)
        if response.status_code == 200:
            self.__image = BytesIO(response.content)

    def add_pin(self, address: str, pin_style="pm2rdm"):
        self.__pin.append(self.__get_cords(self.__get_object_json(self.__get_json(address))) + "," + pin_style)

    def get_image(self) -> BytesIO:
        return self.__image

    def __auto_spn(self) -> str:
        lower = self.__str_to_list(self.__object_json['boundedBy']['Envelope']['lowerCorner'].replace(" ", ","))
        upper = self.__str_to_list(self.__object_json['boundedBy']['Envelope']['upperCorner'].replace(" ", ","))
        return f"{abs(upper[0] - lower[0])},{abs(upper[1] - lower[1])}"

    def zoom_in(self, delta: int):
        self.set_zoom(int(self.__zoom) + delta)

    def set_zoom(self, new_zoom: int):
        if 2 <= new_zoom <= 18:
            self.__zoom = new_zoom
            self.__update_image()

    def __auto_change(self) -> float:
        return 0.0006 * pow(2, 18 - self.__zoom)

    def __move(self, x=0, y=0):
        new_cords = self.__str_to_list(self.__cords)
        new_cords = self.__list_to_str([new_cords[0] + x, new_cords[1] + y])
        if self.__is_ok(cords=new_cords, zoom=self.__zoom, pin=self.__pin):
            self.__cords = new_cords
            self.__update_image()

    def move_up(self, y=None):
        self.__move(0, self.__auto_change() if y is None else -y)

    def move_down(self, y=None):
        self.__move(0, self.__auto_change() if y is None else y)

    def move_right(self, x=None):
        self.__move(self.__auto_change() if x is None else x, 0)

    def move_left(self, x=None):
        self.__move(self.__auto_change() if x is None else -x, 0)

    def set_style(self, style: str):
        if self.__is_ok(style=style):
            self.__style = style
            self.__update_image()

    def __is_ok(self, cords=None, zoom=None, style="map", pin=None):
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

    @staticmethod
    def easy_pin(color: str) -> str:
        return ",pm2" + color + "m"

    @staticmethod
    def __str_to_list(data: str) -> [float, float]:
        return list(map(float, data.split(",")))

    @staticmethod
    def __list_to_str(data: [float, float]) -> str:
        return f"{data[0]},{data[1]}"
