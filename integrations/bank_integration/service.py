# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.conf import settings
from ..base import BaseAPIIntegration
from ..services import IntegrationService, APIService

class BankService(APIService):
    """Banka entegrasyonu servisi"""
    
    def __init__(self):
        config = IntegrationService.get_integration_config('bank')
        super().__init__(
            base_url=config.get('base_url'),
            headers={
                'Authorization': f"Bearer {config.get('api_key')}",
                'Content-Type': 'application/json'
            }
        )
    
    def get_account_balance(self, account_id: str) -> Dict[str, Any]:
        """Hesap bakiyesini al"""
        endpoint = f"/accounts/{account_id}/balance"
        return self.get(endpoint)
    
    def get_transactions(
        self,
        account_id: str,
        start_date: datetime,
        end_date: datetime,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Hesap hareketlerini al"""
        endpoint = f"/accounts/{account_id}/transactions"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'page': page,
            'per_page': per_page
        }
        return self.get(endpoint, params=params)
    
    def make_transfer(
        self,
        from_account: str,
        to_account: str,
        amount: float,
        currency: str,
        description: str
    ) -> Dict[str, Any]:
        """Para transferi yap"""
        endpoint = "/transfers"
        data = {
            'from_account': from_account,
            'to_account': to_account,
            'amount': amount,
            'currency': currency,
            'description': description
        }
        return self.post(endpoint, json=data)
    
    def get_transfer_status(self, transfer_id: str) -> Dict[str, Any]:
        """Transfer durumunu kontrol et"""
        endpoint = f"/transfers/{transfer_id}/status"
        return self.get(endpoint)
    
    def get_exchange_rates(
        self,
        base_currency: str,
        target_currencies: List[str]
    ) -> Dict[str, Any]:
        """Döviz kurlarını al"""
        endpoint = "/exchange-rates"
        params = {
            'base': base_currency,
            'symbols': ','.join(target_currencies)
        }
        return self.get(endpoint, params=params)
    
    def create_payment_order(
        self,
        account_id: str,
        amount: float,
        currency: str,
        recipient_name: str,
        recipient_iban: str,
        description: str
    ) -> Dict[str, Any]:
        """Ödeme emri oluştur"""
        endpoint = "/payment-orders"
        data = {
            'account_id': account_id,
            'amount': amount,
            'currency': currency,
            'recipient_name': recipient_name,
            'recipient_iban': recipient_iban,
            'description': description
        }
        return self.post(endpoint, json=data)
    
    def get_payment_order_status(self, order_id: str) -> Dict[str, Any]:
        """Ödeme emri durumunu kontrol et"""
        endpoint = f"/payment-orders/{order_id}/status"
        return self.get(endpoint)
    
    def cancel_payment_order(self, order_id: str) -> Dict[str, Any]:
        """Ödeme emrini iptal et"""
        endpoint = f"/payment-orders/{order_id}/cancel"
        return self.post(endpoint)
    
    def get_account_statements(
        self,
        account_id: str,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """Hesap ekstresi al"""
        endpoint = f"/accounts/{account_id}/statements"
        params = {
            'year': year,
            'month': month
        }
        return self.get(endpoint, params=params)
    
    def get_account_details(self, account_id: str) -> Dict[str, Any]:
        """Hesap detaylarını al"""
        endpoint = f"/accounts/{account_id}"
        return self.get(endpoint)
    
    def validate_iban(self, iban: str) -> Dict[str, Any]:
        """IBAN doğrulama"""
        endpoint = "/validate/iban"
        data = {'iban': iban}
        return self.post(endpoint, json=data)
    
    def get_bank_branches(
        self,
        city: Optional[str] = None,
        district: Optional[str] = None
    ) -> Dict[str, Any]:
        """Banka şubelerini listele"""
        endpoint = "/branches"
        params = {}
        if city:
            params['city'] = city
        if district:
            params['district'] = district
        return self.get(endpoint, params=params)
    
    def get_bank_holidays(self, year: int) -> Dict[str, Any]:
        """Banka tatil günlerini al"""
        endpoint = "/holidays"
        params = {'year': year}
        return self.get(endpoint, params=params)
    
    def get_currency_list(self) -> Dict[str, Any]:
        """Para birimlerini listele"""
        endpoint = "/currencies"
        return self.get(endpoint)
    
    def get_account_limits(self, account_id: str) -> Dict[str, Any]:
        """Hesap limitlerini al"""
        endpoint = f"/accounts/{account_id}/limits"
        return self.get(endpoint)
    
    def get_transaction_categories(self) -> Dict[str, Any]:
        """İşlem kategorilerini listele"""
        endpoint = "/transaction-categories"
        return self.get(endpoint)
    
    def get_transaction_reports(
        self,
        account_id: str,
        start_date: datetime,
        end_date: datetime,
        report_type: str
    ) -> Dict[str, Any]:
        """İşlem raporları al"""
        endpoint = f"/accounts/{account_id}/reports"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'type': report_type
        }
        return self.get(endpoint, params=params) 