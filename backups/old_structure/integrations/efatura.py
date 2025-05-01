# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
import requests
import json

class EFaturaIntegration:
    def __init__(self):
        self.api_key = settings.EFATURA_API_KEY
        self.base_url = settings.EFATURA_BASE_URL
        
    def create_invoice(self, data):
        """
        E-Fatura olu≈üturma
        """
        try:
            response = requests.post(
                f"{self.base_url}/invoice/create",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=data
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
            
    def get_invoice_status(self, invoice_id):
        """
        E-Fatura durumu sorgulama
        """
        try:
            response = requests.get(
                f"{self.base_url}/invoice/status/{invoice_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
            
    def cancel_invoice(self, invoice_id):
        """
        E-Fatura iptal etme
        """
        try:
            response = requests.post(
                f"{self.base_url}/invoice/cancel/{invoice_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)} 