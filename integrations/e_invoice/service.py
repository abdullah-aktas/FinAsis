# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.conf import settings
from ..base import BaseAPIIntegration
from ..services import IntegrationService, APIService

class EInvoiceService(APIService):
    """E-fatura entegrasyonu servisi"""
    
    def __init__(self):
        config = IntegrationService.get_integration_config('e_invoice')
        super().__init__(
            base_url=config.get('base_url'),
            headers={
                'Authorization': f"Bearer {config.get('api_key')}",
                'Content-Type': 'application/json'
            }
        )
    
    def create_invoice(
        self,
        customer_id: str,
        items: List[Dict[str, Any]],
        invoice_date: datetime,
        due_date: datetime,
        currency: str = 'TRY',
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """E-fatura oluştur"""
        endpoint = "/invoices"
        data = {
            'customer_id': customer_id,
            'items': items,
            'invoice_date': invoice_date.isoformat(),
            'due_date': due_date.isoformat(),
            'currency': currency
        }
        if notes:
            data['notes'] = notes
        return self.post(endpoint, json=data)
    
    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """E-fatura detaylarını al"""
        endpoint = f"/invoices/{invoice_id}"
        return self.get(endpoint)
    
    def update_invoice(
        self,
        invoice_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """E-fatura güncelle"""
        endpoint = f"/invoices/{invoice_id}"
        return self.put(endpoint, json=data)
    
    def cancel_invoice(
        self,
        invoice_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """E-fatura iptal et"""
        endpoint = f"/invoices/{invoice_id}/cancel"
        data = {'reason': reason}
        return self.post(endpoint, json=data)
    
    def send_invoice(
        self,
        invoice_id: str,
        send_method: str = 'email'
    ) -> Dict[str, Any]:
        """E-fatura gönder"""
        endpoint = f"/invoices/{invoice_id}/send"
        data = {'send_method': send_method}
        return self.post(endpoint, json=data)
    
    def get_invoice_status(self, invoice_id: str) -> Dict[str, Any]:
        """E-fatura durumunu kontrol et"""
        endpoint = f"/invoices/{invoice_id}/status"
        return self.get(endpoint)
    
    def list_invoices(
        self,
        page: int = 1,
        per_page: int = 50,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """E-faturaları listele"""
        endpoint = "/invoices"
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
        return self.get(endpoint, params=params)
    
    def get_invoice_pdf(self, invoice_id: str) -> Dict[str, Any]:
        """E-fatura PDF'ini al"""
        endpoint = f"/invoices/{invoice_id}/pdf"
        return self.get(endpoint)
    
    def get_invoice_xml(self, invoice_id: str) -> Dict[str, Any]:
        """E-fatura XML'ini al"""
        endpoint = f"/invoices/{invoice_id}/xml"
        return self.get(endpoint)
    
    def create_credit_note(
        self,
        invoice_id: str,
        items: List[Dict[str, Any]],
        reason: str
    ) -> Dict[str, Any]:
        """E-irsaliye oluştur"""
        endpoint = f"/invoices/{invoice_id}/credit-note"
        data = {
            'items': items,
            'reason': reason
        }
        return self.post(endpoint, json=data)
    
    def get_credit_note(self, credit_note_id: str) -> Dict[str, Any]:
        """E-irsaliye detaylarını al"""
        endpoint = f"/credit-notes/{credit_note_id}"
        return self.get(endpoint)
    
    def list_credit_notes(
        self,
        page: int = 1,
        per_page: int = 50,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """E-irsaliyeleri listele"""
        endpoint = "/credit-notes"
        params = {
            'page': page,
            'per_page': per_page
        }
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        return self.get(endpoint, params=params)
    
    def get_invoice_statistics(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: str = 'day'
    ) -> Dict[str, Any]:
        """E-fatura istatistiklerini al"""
        endpoint = "/invoices/statistics"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'group_by': group_by
        }
        return self.get(endpoint, params=params)
    
    def validate_invoice_data(
        self,
        invoice_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """E-fatura verilerini doğrula"""
        endpoint = "/invoices/validate"
        return self.post(endpoint, json=invoice_data)
    
    def get_invoice_template(self, template_id: str) -> Dict[str, Any]:
        """E-fatura şablonunu al"""
        endpoint = f"/templates/{template_id}"
        return self.get(endpoint)
    
    def create_invoice_template(
        self,
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """E-fatura şablonu oluştur"""
        endpoint = "/templates"
        return self.post(endpoint, json=template_data)
    
    def update_invoice_template(
        self,
        template_id: str,
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """E-fatura şablonunu güncelle"""
        endpoint = f"/templates/{template_id}"
        return self.put(endpoint, json=template_data)
    
    def delete_invoice_template(self, template_id: str) -> Dict[str, Any]:
        """E-fatura şablonunu sil"""
        endpoint = f"/templates/{template_id}"
        return self.delete(endpoint)
    
    def list_invoice_templates(
        self,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """E-fatura şablonlarını listele"""
        endpoint = "/templates"
        params = {
            'page': page,
            'per_page': per_page
        }
        return self.get(endpoint, params=params)
    
    def get_invoice_settings(self) -> Dict[str, Any]:
        """E-fatura ayarlarını al"""
        endpoint = "/settings"
        return self.get(endpoint)
    
    def update_invoice_settings(
        self,
        settings_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """E-fatura ayarlarını güncelle"""
        endpoint = "/settings"
        return self.put(endpoint, json=settings_data)
    
    def get_invoice_logs(
        self,
        invoice_id: str,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """E-fatura loglarını al"""
        endpoint = f"/invoices/{invoice_id}/logs"
        params = {
            'page': page,
            'per_page': per_page
        }
        return self.get(endpoint, params=params)
    
    def get_invoice_archive(
        self,
        start_date: datetime,
        end_date: datetime,
        format: str = 'zip'
    ) -> Dict[str, Any]:
        """E-fatura arşivini al"""
        endpoint = "/invoices/archive"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'format': format
        }
        return self.get(endpoint, params=params)
    
    def get_invoice_reports(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str
    ) -> Dict[str, Any]:
        """E-fatura raporlarını al"""
        endpoint = "/reports"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'type': report_type
        }
        return self.get(endpoint, params=params) 