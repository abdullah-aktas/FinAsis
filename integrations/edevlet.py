# -*- coding: utf-8 -*-
import requests
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from zeep import Client
from zeep.wsse.username import UsernameToken
import logging
from cryptography.fernet import Fernet
import base64
import json

logger = logging.getLogger(__name__)

class EDevletIntegration:
    def __init__(self):
        self.wsdl_url = settings.EDEVLET_WSDL_URL
        self.username = settings.EDEVLET_USERNAME
        self.password = settings.EDEVLET_PASSWORD
        self.client = None
        self.initialize_client()

    def initialize_client(self):
        """
        SOAP istemcisini başlat
        """
        try:
            wsse = UsernameToken(self.username, self.password)
            self.client = Client(self.wsdl_url, wsse=wsse)
            # Client'ın service özelliğini kontrol et
            if not hasattr(self.client, 'service'):
                raise Exception("EDevlet servisi başlatılamadı")
        except Exception as e:
            logger.error(f"EDevlet istemci başlatma hatası: {str(e)}")
            self.client = None
            raise

    def get_company_info(self, tax_number):
        """
        Vergi numarası ile firma bilgilerini sorgula
        """
        try:
            if not self.client:
                self.initialize_client()
                
            cache_key = f'company_info_{tax_number}'
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data

            response = self.client.service.GetCompanyInfo(tax_number)
            
            if response and response.Result:
                company_data = {
                    'tax_number': response.Result.TaxNumber,
                    'company_name': response.Result.CompanyName,
                    'address': response.Result.Address,
                    'phone': response.Result.Phone,
                    'email': response.Result.Email,
                    'registration_date': response.Result.RegistrationDate,
                    'status': response.Result.Status
                }
                
                cache.set(cache_key, company_data, 3600)  # 1 saat cache
                return company_data
            else:
                raise Exception("Firma bilgileri alınamadı")
        except Exception as e:
            logger.error(f"Firma bilgileri sorgulama hatası: {str(e)}")
            raise

    def verify_identity(self, identity_number, name, surname, birth_year):
        """
        TC Kimlik doğrulama
        """
        try:
            response = self.client.service.VerifyIdentity(
                identity_number=identity_number,
                name=name,
                surname=surname,
                birth_year=birth_year
            )
            
            return {
                'is_valid': response.Result,
                'verification_date': datetime.now()
            }
        except Exception as e:
            logger.error(f"Kimlik doğrulama hatası: {str(e)}")
            raise

    def get_tax_debts(self, tax_number):
        """
        Vergi borçlarını sorgula
        """
        try:
            cache_key = f'tax_debts_{tax_number}'
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data

            response = self.client.service.GetTaxDebts(tax_number)
            
            if response and response.Result:
                debts = []
                for debt in response.Result.Debts:
                    debts.append({
                        'debt_type': debt.DebtType,
                        'amount': debt.Amount,
                        'due_date': debt.DueDate,
                        'status': debt.Status
                    })
                
                cache.set(cache_key, debts, 1800)  # 30 dakika cache
                return debts
            else:
                raise Exception("Vergi borçları alınamadı")
        except Exception as e:
            logger.error(f"Vergi borçları sorgulama hatası: {str(e)}")
            raise

    def get_social_security_info(self, identity_number):
        """
        SGK bilgilerini sorgula
        """
        try:
            cache_key = f'sgk_info_{identity_number}'
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data

            response = self.client.service.GetSocialSecurityInfo(identity_number)
            
            if response and response.Result:
                sgk_data = {
                    'identity_number': response.Result.IdentityNumber,
                    'name': response.Result.Name,
                    'surname': response.Result.Surname,
                    'status': response.Result.Status,
                    'last_payment_date': response.Result.LastPaymentDate,
                    'insurance_type': response.Result.InsuranceType
                }
                
                cache.set(cache_key, sgk_data, 3600)  # 1 saat cache
                return sgk_data
            else:
                raise Exception("SGK bilgileri alınamadı")
        except Exception as e:
            logger.error(f"SGK bilgileri sorgulama hatası: {str(e)}")
            raise

class EInvoiceIntegration:
    def __init__(self):
        self.api_url = settings.EINVOICE_API_URL
        self.username = settings.EINVOICE_USERNAME
        self.password = settings.EINVOICE_PASSWORD
        self.token = None
        self.get_token()

    def get_token(self):
        """
        E-Fatura API token'ı al
        """
        try:
            response = requests.post(
                f"{self.api_url}/token",
                json={
                    'username': self.username,
                    'password': self.password
                }
            )
            
            if response.status_code == 200:
                self.token = response.json()['token']
            else:
                raise Exception("Token alınamadı")
        except Exception as e:
            logger.error(f"Token alma hatası: {str(e)}")
            raise

    def send_invoice(self, invoice_data):
        """
        E-Fatura gönder
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.api_url}/invoices",
                headers=headers,
                json=invoice_data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception("Fatura gönderilemedi")
        except Exception as e:
            logger.error(f"Fatura gönderme hatası: {str(e)}")
            raise

    def get_invoice_status(self, invoice_uuid):
        """
        E-Fatura durumunu sorgula
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.api_url}/invoices/{invoice_uuid}/status",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception("Fatura durumu alınamadı")
        except Exception as e:
            logger.error(f"Fatura durumu sorgulama hatası: {str(e)}")
            raise 