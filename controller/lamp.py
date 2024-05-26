import requests

class Lamp:
    def __init__(self, entity, base_url, headers):
        self.entity = entity
        self.entity_id = entity['entity_id']

        self.features = entity['attributes']

        self.BASE_URL = base_url
        self.HEADERS = headers

    # Функції контролю стану лампочки
    def change_state(self, state: bool):
        url = f'{self.BASE_URL}/services/light/turn_{"on" if state == True else "off"}'
        data = {'entity_id': self.entity_id}
        response = requests.post(url, headers=self.HEADERS, json=data)
        return response.json()

    def change_color(self, rgb_color: list):
        url = f'{self.BASE_URL}/services/light/turn_on'
        data = {
            'entity_id': self.entity_id,
            'rgb_color': rgb_color
        }
        response = requests.post(url, headers=self.HEADERS, json=data)
        return response.json()

    def change_brightness(self, brightness: int):
        url = f'{self.BASE_URL}/services/light/turn_on'
        data = {
            'entity_id': self.entity_id,
            'brightness': brightness
        }
        response = requests.post(url, headers=self.HEADERS, json=data)
        return response.json()