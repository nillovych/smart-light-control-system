import requests


class Controller:
    def __init__(self, domain, token):
        self.TOKEN = token.encode('utf-8').decode('latin-1')
        self.BASE_URL = 'https://' + domain + '/api'
        self.HEADERS = {
            'Authorization': f'Bearer {self.TOKEN}',
            'Content-Type': 'application/json',
        }

    def verify_connection(self):
        url = f'{self.BASE_URL}/states'

        try:
            response = requests.get(url, headers=self.HEADERS)
            response.raise_for_status()

            try:
                response.json()
            except ValueError:
                return f"Відповідь сервера не є дійсною."

            return "Підключення успішне!"

        except requests.exceptions.HTTPError as http_err:
            return f"Введено неіснуючий токен..."
        except requests.exceptions.RequestException as req_err:
            return f"Введений домен не існує, або не відповідає."

    def get_light_entities(self):
        response = requests.get(f'{self.BASE_URL}/states', headers=self.HEADERS)
        entities = response.json()
        return [entity for entity in entities if entity['entity_id'].startswith('light.')]
