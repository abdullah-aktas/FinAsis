import requests
import json
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform
import os

class APIService:
    def __init__(self):
        self.base_url = 'http://localhost:8000/api'
        self.store = JsonStore('finasis_data.json')
        self.setup_storage()

    def setup_storage(self):
        if not self.store.exists('auth'):
            self.store.put('auth', token=None)

    def get_token(self):
        return self.store.get('auth')['token']

    def set_token(self, token):
        self.store.put('auth', token=token)

    def clear_token(self):
        self.store.put('auth', token=None)

    def get_headers(self):
        headers = {
            'Content-Type': 'application/json'
        }
        token = self.get_token()
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers

    def login(self, username, password):
        try:
            response = requests.post(
                f'{self.base_url}/auth/login/',
                json={'username': username, 'password': password}
            )
            if response.status_code == 200:
                data = response.json()
                self.set_token(data.get('token'))
                return True, data
            return False, response.json()
        except Exception as e:
            return False, str(e)

    def logout(self):
        self.clear_token()

    def get_financial_summary(self):
        try:
            response = requests.get(
                f'{self.base_url}/financial/summary/',
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return True, response.json()
            return False, response.json()
        except Exception as e:
            return False, str(e)

    def get_accounting_data(self):
        try:
            response = requests.get(
                f'{self.base_url}/accounting/data/',
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return True, response.json()
            return False, response.json()
        except Exception as e:
            return False, str(e)

    def get_reports(self):
        try:
            response = requests.get(
                f'{self.base_url}/reports/',
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return True, response.json()
            return False, response.json()
        except Exception as e:
            return False, str(e)

    def get_crm_data(self):
        try:
            response = requests.get(
                f'{self.base_url}/crm/data/',
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return True, response.json()
            return False, response.json()
        except Exception as e:
            return False, str(e) 