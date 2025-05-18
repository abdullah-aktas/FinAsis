# -*- coding: utf-8 -*-
"""
Düzenli çalışan finansal görevler için test dosyası.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))
import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

class InvoiceReminderTaskTests(TestCase):
    """Fatura hatırlatma görevleri için testler."""
    
    def setUp(self):
        # İlgili modelleri import et
        from finance.accounting.models import Invoice, Customer
        
        # Test müşterisi oluştur
        self.customer = Customer.objects.create(
            name="Test Müşteri",
            tax_id="1234567890",
            address="Test Adres",
            email="musteri@example.com"
        )
        
        # Vadesi geçmiş fatura oluştur
        self.overdue_invoice = Invoice.objects.create(
            customer=self.customer,
            invoice_number="INV-2023-001",
            issue_date=timezone.now().date() - timedelta(days=40),
            due_date=timezone.now().date() - timedelta(days=10),
            total_amount=Decimal("1180.00"),
            status="APPROVED"
        )
        
        # Vadesi yaklaşan fatura oluştur
        self.due_soon_invoice = Invoice.objects.create(
            customer=self.customer,
            invoice_number="INV-2023-002",
            issue_date=timezone.now().date() - timedelta(days=5),
            due_date=timezone.now().date() + timedelta(days=2),
            total_amount=Decimal("2360.00"),
            status="APPROVED"
        )
    
    @patch('finance.tasks.email_service.send_email')
    def test_send_overdue_invoice_reminders(self, mock_send_email):
        """Vadesi geçmiş fatura hatırlatması gönderme testi."""
        # Hatırlatma görevini içe aktar
        from finance.tasks.invoice_tasks import send_overdue_invoice_reminders
        
        # Görevi çalıştır
        result = send_overdue_invoice_reminders()
        
        # E-posta gönderildiğini doğrula
        mock_send_email.assert_called_with(
            to_email="musteri@example.com",
            subject="Vadesi Geçmiş Fatura Hatırlatması: INV-2023-001",
            template="overdue_invoice_reminder",
            context={
                'invoice': self.overdue_invoice,
                'customer': self.customer
            }
        )
        self.assertEqual(result['sent_count'], 1)
    
    @patch('finance.tasks.email_service.send_email')
    def test_send_due_soon_invoice_reminders(self, mock_send_email):
        """Vadesi yaklaşan fatura hatırlatması gönderme testi."""
        # Hatırlatma görevini içe aktar
        from finance.tasks.invoice_tasks import send_due_soon_invoice_reminders
        
        # Görevi çalıştır
        result = send_due_soon_invoice_reminders()
        
        # E-posta gönderildiğini doğrula
        mock_send_email.assert_called_with(
            to_email="musteri@example.com",
            subject="Fatura Ödeme Hatırlatması: INV-2023-002",
            template="due_soon_invoice_reminder",
            context={
                'invoice': self.due_soon_invoice,
                'customer': self.customer
            }
        )
        self.assertEqual(result['sent_count'], 1)


class BankStatementSyncTaskTests(TestCase):
    """Banka hesap ekstresi senkronizasyon görevleri testleri."""
    
    def setUp(self):
        # İlgili modelleri import et
        from integrations.bank_integration.models import IntegratedBankAccount, BankTransaction
        
        # Test banka hesabı oluştur
        self.bank_account = IntegratedBankAccount.objects.create(
            name="Test Hesabı",
            account_number="TR123456789012345678901234",
            currency="TRY"
        )
    
    @patch('integrations.bank_integration.services.BankAPIClient')
    def test_sync_bank_statements(self, mock_api_client):
        """Banka hesap ekstrelerini senkronize etme testi."""
        # Mock API yanıtı oluştur
        mock_instance = MagicMock()
        mock_instance.get_transactions.return_value = [
            {
                'id': '12345',
                'date': '2023-06-01',
                'description': 'Müşteri Ödemesi',
                'amount': 1000.00,
                'type': 'CREDIT'
            },
            {
                'id': '12346',
                'date': '2023-06-02',
                'description': 'Tedarikçi Ödemesi',
                'amount': -500.00,
                'type': 'DEBIT'
            }
        ]
        mock_api_client.return_value = mock_instance
        
        # Senkronizasyon görevini içe aktar
        from integrations.bank_integration.tasks import sync_bank_statements
        
        # Görevi çalıştır
        result = sync_bank_statements()
        
        # Senkronizasyon sonucunu kontrol et
        self.assertEqual(result['accounts_processed'], 1)
        self.assertEqual(result['transactions_created'], 2)
        
        # İşlemlerin veritabanına eklendiğini doğrula
        from integrations.bank_integration.models import BankTransaction
        transactions = BankTransaction.objects.filter(account=self.bank_account)
        self.assertEqual(transactions.count(), 2)


class MonthlyFinancialReportTaskTests(TestCase):
    """Aylık finansal rapor görevleri testleri."""
    
    def setUp(self):
        # İlgili modelleri import et
        from finance.accounting.models import FinancialTransaction, Account
        
        # Test hesapları oluştur
        self.income_account = Account.objects.create(
            name="Gelir Hesabı",
            code="601",
            type="INCOME",
            balance=Decimal("0.00")
        )
        
        self.expense_account = Account.objects.create(
            name="Gider Hesabı",
            code="701",
            type="EXPENSE",
            balance=Decimal("0.00")
        )
        
        # Geçen ay için test işlemleri oluştur
        last_month = timezone.now().replace(day=1) - timedelta(days=1)
        last_month_start = last_month.replace(day=1)
        
        # Gelir işlemi
        FinancialTransaction.objects.create(
            account=self.income_account,
            amount=Decimal("5000.00"),
            transaction_type="INCOME",
            description="Aylık Gelir",
            transaction_date=last_month_start + timedelta(days=5)
        )
        
        # Gider işlemi
        FinancialTransaction.objects.create(
            account=self.expense_account,
            amount=Decimal("2000.00"),
            transaction_type="EXPENSE",
            description="Aylık Gider",
            transaction_date=last_month_start + timedelta(days=15)
        )
    
    @patch('finance.tasks.report_service.generate_pdf_report')
    @patch('finance.tasks.email_service.send_email_with_attachment')
    def test_generate_and_send_monthly_report(self, mock_send_email, mock_generate_report):
        """Aylık rapor oluşturma ve gönderme testi."""
        # PDF raporu için mock dönüş
        mock_generate_report.return_value = {
            'file_path': '/tmp/monthly_report.pdf',
            'report_data': {
                'total_income': Decimal("5000.00"),
                'total_expense': Decimal("2000.00"),
                'net_profit': Decimal("3000.00")
            }
        }
        
        # Rapor görevini içe aktar
        from finance.tasks.report_tasks import generate_and_send_monthly_financial_report
        
        # Görevi çalıştır
        result = generate_and_send_monthly_financial_report()
        
        # Raporun oluşturulduğunu doğrula
        self.assertTrue(mock_generate_report.called)
        
        # E-postanın gönderildiğini doğrula
        mock_send_email.assert_called_once()
        
        # Rapor içeriğini kontrol et
        report_data = result['report_data']
        self.assertEqual(report_data['total_income'], Decimal("5000.00"))
        self.assertEqual(report_data['total_expense'], Decimal("2000.00"))
        self.assertEqual(report_data['net_profit'], Decimal("3000.00")) 