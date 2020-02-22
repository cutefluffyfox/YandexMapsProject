from io import BytesIO

import requests


class MapAPI:
    geocode_server = "http://geocode-maps.yandex.ru/1.x/"
    geocode_token = "40d1649f-0493-4b70-98ba-98533de7710b"
    maps_api_server = "http://static-maps.yandex.ru/1.x/"

    def __init__(self, address: str):
        self.address = address  # адрес, без него никак
        self.json = self.get_json()  # все данные там, так что один раз читаем ради ускорения
        self.object_json = self.get_object_json()  # важные данные там, так что один раз находим ради ускорения
        self.cords = self.get_cords()  # они везде используются, б
        self.zoom = "0"
        self.spn = self.auto_spn()
        self.style = "map"
        self.pin = ""
        self.image = None
        self.update_image()

    def get_json(self):
        params = {
            "apikey": self.geocode_token,
            "geocode": self.address,
            "format": "json"
        }
        return requests.get(self.geocode_server, params).json()

    def get_object_json(self):
        return self.json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']

    def get_cords(self) -> str:
        return self.object_json['Point']['pos'].replace(" ", ",")

    def update_image(self):
        params = {
            "ll": self.cords,
            "l": self.style,
            "pt": self.pin,
            "z": self.zoom,
        }
        response = requests.get(self.maps_api_server, params=params)
        if response.status_code == 200:
            self.image = BytesIO(response.content)

    def get_image(self) -> BytesIO:
        return self.image

    def auto_spn(self) -> str:
        lower = self.str_to_list(self.object_json['boundedBy']['Envelope']['lowerCorner'].replace(" ", ","))
        upper = self.str_to_list(self.object_json['boundedBy']['Envelope']['upperCorner'].replace(" ", ","))
        return f"{abs(upper[0] - lower[0])},{abs(upper[1] - lower[1])}"

    def zoom_in(self, delta: int):
        new_zoom = int(self.zoom) + delta
        if 1 <= new_zoom <= 20:
            self.zoom = str(new_zoom)
            self.update_image()

    def set_zoom(self, new_zoom: int):
        if 1 <= new_zoom <= 20:
            self.zoom = str(new_zoom)
            self.update_image()

    def is_ok(self, spn=None, zoom=None, style="map", pins=None):
        params = {
            "ll": self.cords,
            "l": style,
            "pt": pins,
            "z": zoom,
            "spn": spn,
        }
        response = requests.get(self.maps_api_server, params=params)
        return response.status_code == 200

    @staticmethod
    def easy_pin(color: str) -> str:
        return ",pm2" + color + "m"

    @staticmethod
    def str_to_list(data: str) -> [float, float]:
        return list(map(float, data.split(",")))

    @staticmethod
    def list_to_str(data: [float, float]) -> str:
        return f"{data[0]},{data[1]}"


def debug():
    from PIL import Image
    map_api = MapAPI("некрасовская 50")
    map_api.set_zoom(15)
    Image.open(map_api.get_image()).show()
    map_api.set_zoom(18)
    Image.open(map_api.get_image()).show()


if __name__ == "__main__":
    debug()
