import sqlite3

import requests


class Controller:
    def __init__(self, domain, token):
        self.TOKEN = token.encode('utf-8').decode('latin-1')
        self.BASE_URL = 'https://' + domain + '/api'
        self.HEADERS = {
            'Authorization': f'Bearer {self.TOKEN}',
            'Content-Type': 'application/json',
        }
        self.connection_is_verified = self.verify_connection()

    def verify_connection(self):
        url = f'{self.BASE_URL}/states'

        try:
            response = requests.get(url, headers=self.HEADERS)
            response.raise_for_status()

            try:
                response.json()
            except ValueError:
                print("Відповідь сервера не є JSON:", response.text)
                return False

            print("Токен і базовий URL вірні.")
            self.__save_auth_data()
            return True

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP помилка: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Помилка при перевірці токена та базового URL: {req_err}")

        return False

    def get_light_entities(self):
        response = requests.get(f'{self.BASE_URL}/states', headers=self.HEADERS)
        entities = response.json()
        return [entity for entity in entities if entity['entity_id'].startswith('light.')]

    # Операції з БД
    def __save_auth_data(self):
        Controller.delete_auth_data()

        with sqlite3.connect('db.sqlite3') as conn:
            conn.execute('INSERT INTO Users (token, url) VALUES (?, ?)',
                         (self.TOKEN, self.BASE_URL))
            conn.commit()

    @staticmethod
    def delete_auth_data():
        with sqlite3.connect('db.sqlite3') as conn:
            conn.execute('DELETE FROM Users')
            conn.commit()

    @staticmethod
    def get_user_record():
        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            return cursor.fetchone()
