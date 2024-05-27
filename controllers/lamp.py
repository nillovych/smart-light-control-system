import requests


class Lamp:
    def __init__(self, entity_id, domain, token):
        self.entity_id = entity_id
        self.BASE_URL = 'https://' + domain + '/api'
        self.HEADERS = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        self.entity = self.get_entity(entity_id)

    def get_entity(self, entity_id):
        url = f'{self.BASE_URL}/states/{entity_id}'
        response = requests.get(url, headers=self.HEADERS)
        return response.json()

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
