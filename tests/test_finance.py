# -*- coding: utf-8 -*-
"""
Finans modülü için test dosyası.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))
import pytest
from django.test import TestCase
from decimal import Decimal
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

class FinancialTransactionTest(TestCase):
    """Finansal işlem testleri."""
    
    def setUp(self):
        # İlgili modelleri import et
        from finance.accounting.models import FinancialTransaction, Account
        
        self.account = Account.objects.create(
            name="Ana Kasa",
            code="101",
            type="ASSET",
            balance=Decimal("10000.00")
        )
        
        self.transaction = FinancialTransaction.objects.create(
            account=self.account,
            amount=Decimal("500.00"),
            transaction_type="EXPENSE",
            description="Test Harcama",
            transaction_date=datetime.now().date()
        )
    
    def test_transaction_creation(self):
        """Finansal işlem oluşturma testi."""
        from finance.accounting.models import FinancialTransaction
        
        transaction = FinancialTransaction.objects.get(id=self.transaction.id)
        self.assertEqual(transaction.amount, Decimal("500.00"))
        self.assertEqual(transaction.transaction_type, "EXPENSE")
        self.assertEqual(transaction.description, "Test Harcama")
    
    def test_account_balance_update(self):
        """Hesap bakiyesi güncelleme testi."""
        from finance.accounting.models import Account
        
        # İşlem sonrası hesap bakiyesini kontrol et
        account = Account.objects.get(id=self.account.id)
        self.assertEqual(account.balance, Decimal("9500.00"))

class InvoiceTest(TestCase):
    """Fatura testleri."""
    
    def setUp(self):
        # İlgili modelleri import et
        from finance.accounting.models import Invoice, InvoiceItem, Customer
        
        self.customer = Customer.objects.create(
            name="Test Müşteri",
            tax_id="1234567890",
            address="Test Adres"
        )
        
        self.invoice = Invoice.objects.create(
            customer=self.customer,
            invoice_number="INV-2023-001",
            issue_date=datetime.now().date(),
            due_date=datetime.now().date() + timedelta(days=30),
            total_amount=Decimal("1180.00"),
            status="DRAFT"
        )
        
        self.invoice_item = InvoiceItem.objects.create(
            invoice=self.invoice,
            description="Test Ürün",
            quantity=2,
            unit_price=Decimal("500.00"),
            tax_rate=Decimal("18.00"),
            line_total=Decimal("1000.00"),
            tax_amount=Decimal("180.00")
        )
    
    def test_invoice_creation(self):
        """Fatura oluşturma testi."""
        from finance.accounting.models import Invoice
        
        invoice = Invoice.objects.get(id=self.invoice.id)
        self.assertEqual(invoice.invoice_number, "INV-2023-001")
        self.assertEqual(invoice.total_amount, Decimal("1180.00"))
        self.assertEqual(invoice.status, "DRAFT")
    
    def test_invoice_approval(self):
        """Fatura onaylama testi."""
        from finance.accounting.models import Invoice
        
        # Faturayı onayla
        self.invoice.status = "APPROVED"
        self.invoice.save()
        
        # Onaylı durumu kontrol et
        invoice = Invoice.objects.get(id=self.invoice.id)
        self.assertEqual(invoice.status, "APPROVED")

@pytest.mark.integration
class PaymentTest(TestCase):
    """Ödeme işlemleri testleri."""
    
    def setUp(self):
        # İlgili modelleri import et
        from finance.accounting.models import Payment, Invoice, Customer
        
        self.customer = Customer.objects.create(
            name="Test Müşteri",
            tax_id="1234567890",
            address="Test Adres"
        )
        
        self.invoice = Invoice.objects.create(
            customer=self.customer,
            invoice_number="INV-2023-001",
            issue_date=datetime.now().date(),
            due_date=datetime.now().date() + timedelta(days=30),
            total_amount=Decimal("1180.00"),
            status="APPROVED"
        )
        
        self.payment = Payment.objects.create(
            invoice=self.invoice,
            amount=Decimal("1180.00"),
            payment_date=datetime.now().date(),
            payment_method="BANK_TRANSFER",
            status="COMPLETED"
        )
    
    def test_payment_creation(self):
        """Ödeme oluşturma testi."""
        from finance.accounting.models import Payment
        
        payment = Payment.objects.get(id=self.payment.id)
        self.assertEqual(payment.amount, Decimal("1180.00"))
        self.assertEqual(payment.payment_method, "BANK_TRANSFER")
        self.assertEqual(payment.status, "COMPLETED")
    
    @patch('finance.banking.services.BankService')
    def test_bank_payment_processing(self, mock_bank_service):
        """Banka ödemesi işleme testi."""
        mock_instance = MagicMock()
        mock_instance.process_payment.return_value = {
            "status": "success", 
            "transaction_id": "12345", 
            "timestamp": "2023-06-15T14:30:00Z"
        }
        mock_bank_service.return_value = mock_instance
        
        # Banka servisi ile ödeme işlemi
        from finance.banking.services import process_bank_payment
        result = process_bank_payment(
            invoice_id=self.invoice.id,
            amount=Decimal("1180.00"),
            account_number="TR123456789012345678901234"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["transaction_id"], "12345") 