# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.conf import settings
from ..base import BaseAPIIntegration
from ..services import IntegrationService, APIService

class PaymentService(APIService):
    """Ödeme entegrasyonu servisi"""
    
    def __init__(self):
        config = IntegrationService.get_integration_config('payment')
        super().__init__(
            base_url=config.get('base_url'),
            headers={
                'Authorization': f"Bearer {config.get('api_key')}",
                'Content-Type': 'application/json'
            }
        )
    
    def create_payment(
        self,
        amount: float,
        currency: str,
        payment_method: str,
        customer_id: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ödeme oluştur"""
        endpoint = "/payments"
        data = {
            'amount': amount,
            'currency': currency,
            'payment_method': payment_method,
            'customer_id': customer_id,
            'description': description
        }
        if metadata:
            data['metadata'] = metadata
        if success_url:
            data['success_url'] = success_url
        if cancel_url:
            data['cancel_url'] = cancel_url
        return self.post(endpoint, json=data)
    
    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """Ödeme detaylarını al"""
        endpoint = f"/payments/{payment_id}"
        return self.get(endpoint)
    
    def cancel_payment(
        self,
        payment_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ödeme iptal et"""
        endpoint = f"/payments/{payment_id}/cancel"
        data = {}
        if reason:
            data['reason'] = reason
        return self.post(endpoint, json=data)
    
    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ödeme iadesi yap"""
        endpoint = f"/payments/{payment_id}/refund"
        data = {}
        if amount:
            data['amount'] = amount
        if reason:
            data['reason'] = reason
        return self.post(endpoint, json=data)
    
    def list_payments(
        self,
        page: int = 1,
        per_page: int = 50,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ödemeleri listele"""
        endpoint = "/payments"
        params = {
            'page': page,
            'per_page': per_page
        }
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        if status:
            params['status'] = status
        if customer_id:
            params['customer_id'] = customer_id
        return self.get(endpoint, params=params)
    
    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        payment_method: str,
        start_date: Optional[datetime] = None,
        trial_period_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Abonelik oluştur"""
        endpoint = "/subscriptions"
        data = {
            'customer_id': customer_id,
            'plan_id': plan_id,
            'payment_method': payment_method
        }
        if start_date:
            data['start_date'] = start_date.isoformat()
        if trial_period_days:
            data['trial_period_days'] = trial_period_days
        if metadata:
            data['metadata'] = metadata
        return self.post(endpoint, json=data)
    
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Abonelik detaylarını al"""
        endpoint = f"/subscriptions/{subscription_id}"
        return self.get(endpoint)
    
    def update_subscription(
        self,
        subscription_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Abonelik güncelle"""
        endpoint = f"/subscriptions/{subscription_id}"
        return self.put(endpoint, json=data)
    
    def cancel_subscription(
        self,
        subscription_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Abonelik iptal et"""
        endpoint = f"/subscriptions/{subscription_id}/cancel"
        data = {}
        if reason:
            data['reason'] = reason
        return self.post(endpoint, json=data)
    
    def list_subscriptions(
        self,
        page: int = 1,
        per_page: int = 50,
        customer_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Abonelikleri listele"""
        endpoint = "/subscriptions"
        params = {
            'page': page,
            'per_page': per_page
        }
        if customer_id:
            params['customer_id'] = customer_id
        if status:
            params['status'] = status
        return self.get(endpoint, params=params)
    
    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Müşteri oluştur"""
        endpoint = "/customers"
        data = {'email': email}
        if name:
            data['name'] = name
        if phone:
            data['phone'] = phone
        if metadata:
            data['metadata'] = metadata
        return self.post(endpoint, json=data)
    
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Müşteri detaylarını al"""
        endpoint = f"/customers/{customer_id}"
        return self.get(endpoint)
    
    def update_customer(
        self,
        customer_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Müşteri güncelle"""
        endpoint = f"/customers/{customer_id}"
        return self.put(endpoint, json=data)
    
    def delete_customer(self, customer_id: str) -> Dict[str, Any]:
        """Müşteri sil"""
        endpoint = f"/customers/{customer_id}"
        return self.delete(endpoint)
    
    def list_customers(
        self,
        page: int = 1,
        per_page: int = 50,
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Müşterileri listele"""
        endpoint = "/customers"
        params = {
            'page': page,
            'per_page': per_page
        }
        if email:
            params['email'] = email
        return self.get(endpoint, params=params)
    
    def create_payment_method(
        self,
        customer_id: str,
        type: str,
        card_details: Optional[Dict[str, Any]] = None,
        bank_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ödeme yöntemi ekle"""
        endpoint = "/payment-methods"
        data = {
            'customer_id': customer_id,
            'type': type
        }
        if card_details:
            data['card_details'] = card_details
        if bank_details:
            data['bank_details'] = bank_details
        return self.post(endpoint, json=data)
    
    def get_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
        """Ödeme yöntemi detaylarını al"""
        endpoint = f"/payment-methods/{payment_method_id}"
        return self.get(endpoint)
    
    def update_payment_method(
        self,
        payment_method_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ödeme yöntemi güncelle"""
        endpoint = f"/payment-methods/{payment_method_id}"
        return self.put(endpoint, json=data)
    
    def delete_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
        """Ödeme yöntemi sil"""
        endpoint = f"/payment-methods/{payment_method_id}"
        return self.delete(endpoint)
    
    def list_payment_methods(
        self,
        customer_id: str,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Ödeme yöntemlerini listele"""
        endpoint = "/payment-methods"
        params = {
            'customer_id': customer_id,
            'page': page,
            'per_page': per_page
        }
        return self.get(endpoint, params=params)
    
    def create_invoice(
        self,
        customer_id: str,
        amount: float,
        currency: str,
        description: str,
        due_date: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Fatura oluştur"""
        endpoint = "/invoices"
        data = {
            'customer_id': customer_id,
            'amount': amount,
            'currency': currency,
            'description': description
        }
        if due_date:
            data['due_date'] = due_date.isoformat()
        if metadata:
            data['metadata'] = metadata
        return self.post(endpoint, json=data)
    
    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Fatura detaylarını al"""
        endpoint = f"/invoices/{invoice_id}"
        return self.get(endpoint)
    
    def list_invoices(
        self,
        customer_id: str,
        page: int = 1,
        per_page: int = 50,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Faturaları listele"""
        endpoint = "/invoices"
        params = {
            'customer_id': customer_id,
            'page': page,
            'per_page': per_page
        }
        if status:
            params['status'] = status
        return self.get(endpoint, params=params)
    
    def get_payment_intent(
        self,
        amount: float,
        currency: str,
        payment_method_types: List[str],
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ödeme niyeti oluştur"""
        endpoint = "/payment-intents"
        data = {
            'amount': amount,
            'currency': currency,
            'payment_method_types': payment_method_types
        }
        if customer_id:
            data['customer_id'] = customer_id
        if metadata:
            data['metadata'] = metadata
        return self.post(endpoint, json=data)
    
    def confirm_payment_intent(
        self,
        payment_intent_id: str,
        payment_method_id: str
    ) -> Dict[str, Any]:
        """Ödeme niyetini onayla"""
        endpoint = f"/payment-intents/{payment_intent_id}/confirm"
        data = {'payment_method_id': payment_method_id}
        return self.post(endpoint, json=data)
    
    def get_payment_intent_status(self, payment_intent_id: str) -> Dict[str, Any]:
        """Ödeme niyeti durumunu kontrol et"""
        endpoint = f"/payment-intents/{payment_intent_id}/status"
        return self.get(endpoint)
    
    def get_payment_statistics(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: str = 'day'
    ) -> Dict[str, Any]:
        """Ödeme istatistiklerini al"""
        endpoint = "/statistics/payments"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'group_by': group_by
        }
        return self.get(endpoint, params=params)
    
    def get_subscription_statistics(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: str = 'day'
    ) -> Dict[str, Any]:
        """Abonelik istatistiklerini al"""
        endpoint = "/statistics/subscriptions"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'group_by': group_by
        }
        return self.get(endpoint, params=params)
    
    def get_customer_statistics(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: str = 'day'
    ) -> Dict[str, Any]:
        """Müşteri istatistiklerini al"""
        endpoint = "/statistics/customers"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'group_by': group_by
        }
        return self.get(endpoint, params=params)
    
    def get_payment_reports(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str
    ) -> Dict[str, Any]:
        """Ödeme raporlarını al"""
        endpoint = "/reports/payments"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'type': report_type
        }
        return self.get(endpoint, params=params)
    
    def get_subscription_reports(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str
    ) -> Dict[str, Any]:
        """Abonelik raporlarını al"""
        endpoint = "/reports/subscriptions"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'type': report_type
        }
        return self.get(endpoint, params=params)
    
    def get_customer_reports(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str
    ) -> Dict[str, Any]:
        """Müşteri raporlarını al"""
        endpoint = "/reports/customers"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'type': report_type
        }
        return self.get(endpoint, params=params)
    
    def get_system_settings(self) -> Dict[str, Any]:
        """Sistem ayarlarını al"""
        endpoint = "/settings"
        return self.get(endpoint)
    
    def update_system_settings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sistem ayarlarını güncelle"""
        endpoint = "/settings"
        return self.put(endpoint, json=data)
    
    def get_audit_logs(
        self,
        start_date: datetime,
        end_date: datetime,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Denetim loglarını al"""
        endpoint = "/audit-logs"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'page': page,
            'per_page': per_page
        }
        return self.get(endpoint, params=params)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Sistem durumunu kontrol et"""
        endpoint = "/status"
        return self.get(endpoint)
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Entegrasyon durumunu kontrol et"""
        endpoint = "/integration/status"
        return self.get(endpoint)
    
    def sync_data(self, data_type: str) -> Dict[str, Any]:
        """Veri senkronizasyonu başlat"""
        endpoint = "/sync"
        data = {'data_type': data_type}
        return self.post(endpoint, json=data)
    
    def get_sync_status(self, sync_id: str) -> Dict[str, Any]:
        """Senkronizasyon durumunu kontrol et"""
        endpoint = f"/sync/{sync_id}/status"
        return self.get(endpoint) 