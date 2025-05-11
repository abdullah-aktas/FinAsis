# -*- coding: utf-8 -*-
"""
E-fatura entegrasyonları için test dosyası.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))
import pytest
from django.test import TestCase
from integrations.efatura.models import EInvoice, InvoiceItem
from datetime import datetime
from unittest.mock import patch, MagicMock
from decimal import Decimal

class EInvoiceModelTest(TestCase):
    """E-fatura modeli testleri."""
    
    def setUp(self):
        self.einvoice = EInvoice.objects.create(
            invoice_number="INV-2023-001",
            issue_date=datetime.now().date(),
            due_date=datetime.now().date(),
            total_amount=Decimal("1000.00"),
            tax_amount=Decimal("180.00"),
            customer_name="Test Müşteri",
            customer_tax_id="1234567890"
        )
        
        self.invoice_item = InvoiceItem.objects.create(
            invoice=self.einvoice,
            description="Test Ürün",
            quantity=2,
            unit_price=Decimal("500.00"),
            tax_rate=Decimal("18.00"),
            amount=Decimal("1000.00")
        )
    
    def test_einvoice_creation(self):
        """E-fatura oluşturma testi."""
        self.assertEqual(self.einvoice.invoice_number, "INV-2023-001")
        self.assertEqual(self.einvoice.total_amount, Decimal("1000.00"))
        self.assertEqual(self.einvoice.tax_amount, Decimal("180.00"))
        self.assertEqual(self.einvoice.customer_name, "Test Müşteri")
    
    def test_einvoice_item_creation(self):
        """E-fatura kalemi oluşturma testi."""
        self.assertEqual(self.invoice_item.invoice, self.einvoice)
        self.assertEqual(self.invoice_item.description, "Test Ürün")
        self.assertEqual(self.invoice_item.quantity, 2)
        self.assertEqual(self.invoice_item.unit_price, Decimal("500.00"))
        self.assertEqual(self.invoice_item.amount, Decimal("1000.00"))

@pytest.mark.integration
class EInvoiceIntegrationTest(TestCase):
    """E-fatura entegrasyon testleri."""
    
    @patch('integrations.efatura.services.EInvoiceProvider')
    def test_send_einvoice(self, mock_provider):
        """E-fatura gönderme testi."""
        mock_instance = MagicMock()
        mock_instance.send_invoice.return_value = {
            "status": "success", 
            "document_id": "12345678-1234-1234-1234-123456789012"
        }
        mock_provider.return_value = mock_instance
        
        # E-fatura oluştur
        einvoice = EInvoice.objects.create(
            invoice_number="INV-2023-002",
            issue_date=datetime.now().date(),
            due_date=datetime.now().date(),
            total_amount=Decimal("1000.00"),
            tax_amount=Decimal("180.00"),
            customer_name="Test Müşteri",
            customer_tax_id="1234567890"
        )
        
        # E-fatura servisini kullanarak test işlemi
        from integrations.efatura.services import send_einvoice
        result = send_einvoice(einvoice.id)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["document_id"], "12345678-1234-1234-1234-123456789012")
    
    @patch('integrations.efatura.services.EInvoiceProvider')
    def test_get_einvoice_status(self, mock_provider):
        """E-fatura durumu sorgulama testi."""
        mock_instance = MagicMock()
        mock_instance.get_invoice_status.return_value = {
            "status": "delivered", 
            "timestamp": "2023-06-15T14:30:00Z"
        }
        mock_provider.return_value = mock_instance
        
        # E-fatura servisini kullanarak test işlemi
        from integrations.efatura.services import get_einvoice_status
        status_info = get_einvoice_status("12345678-1234-1234-1234-123456789012")
        
        self.assertEqual(status_info["status"], "delivered")
        self.assertIn("timestamp", status_info) 