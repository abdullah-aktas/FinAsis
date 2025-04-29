# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
import requests
import json
from datetime import datetime

class BankIntegration:
    def __init__(self, bank_name):
        self.bank_name = bank_name
        self.api_key = getattr(settings, f"{bank_name.upper()}_API_KEY")
        self.base_url = getattr(settings, f"{bank_name.upper()}_BASE_URL")
        
    def get_account_balance(self, account_number):
        """
        Hesap bakiyesi sorgulama
        """
        try:
            response = requests.get(
                f"{self.base_url}/accounts/{account_number}/balance",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
            
    def get_transactions(self, account_number, start_date, end_date):
        """
        Hesap hareketleri sorgulama
        """
        try:
            response = requests.get(
                f"{self.base_url}/accounts/{account_number}/transactions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"start_date": start_date, "end_date": end_date}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
            
    def reconcile_transactions(self, account_number, transactions):
        """
        Otomatik mutabakat
        """
        try:
            response = requests.post(
                f"{self.base_url}/accounts/{account_number}/reconcile",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"transactions": transactions}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
            
    def make_transfer(self, from_account, to_account, amount, description):
        """
        Para transferi
        """
        try:
            response = requests.post(
                f"{self.base_url}/transfer",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "from_account": from_account,
                    "to_account": to_account,
                    "amount": amount,
                    "description": description
                }
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)} 