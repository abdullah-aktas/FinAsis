from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Account, Transaction, Invoice
from decimal import Decimal

User = get_user_model()

class AccountingTests(TestCase):
    def setUp(self):
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Test hesapları oluştur
        self.asset_account = Account.objects.create(
            name='Test Varlık Hesabı',
            code='1000',
            type='asset',
            created_by=self.user
        )
        
        self.liability_account = Account.objects.create(
            name='Test Borç Hesabı',
            code='3000',
            type='liability',
            created_by=self.user
        )
        
        self.income_account = Account.objects.create(
            name='Test Gelir Hesabı',
            code='4000',
            type='income',
            created_by=self.user
        )

    def test_account_creation(self):
        """Hesap oluşturma testi"""
        self.assertEqual(self.asset_account.name, 'Test Varlık Hesabı')
        self.assertEqual(self.asset_account.code, '1000')
        self.assertEqual(self.asset_account.type, 'asset')
        self.assertEqual(self.asset_account.created_by, self.user)

    def test_transaction_creation(self):
        """İşlem oluşturma testi"""
        transaction = Transaction.objects.create(
            date='2024-01-01',
            description='Test İşlem',
            amount=Decimal('1000.00'),
            debit_account=self.asset_account,
            credit_account=self.liability_account,
            created_by=self.user
        )
        
        self.assertEqual(transaction.amount, Decimal('1000.00'))
        self.assertEqual(transaction.debit_account, self.asset_account)
        self.assertEqual(transaction.credit_account, self.liability_account)

    def test_invoice_creation(self):
        """Fatura oluşturma testi"""
        invoice = Invoice.objects.create(
            invoice_number='TEST-001',
            date='2024-01-01',
            due_date='2024-02-01',
            amount=Decimal('1000.00'),
            account=self.income_account,
            created_by=self.user
        )
        
        self.assertEqual(invoice.invoice_number, 'TEST-001')
        self.assertEqual(invoice.amount, Decimal('1000.00'))
        self.assertEqual(invoice.account, self.income_account)

    def test_account_balance(self):
        """Hesap bakiyesi hesaplama testi"""
        # Borç işlemi
        Transaction.objects.create(
            date='2024-01-01',
            description='Borç İşlemi',
            amount=Decimal('1000.00'),
            debit_account=self.asset_account,
            credit_account=self.liability_account,
            created_by=self.user
        )
        
        # Alacak işlemi
        Transaction.objects.create(
            date='2024-01-02',
            description='Alacak İşlemi',
            amount=Decimal('500.00'),
            debit_account=self.liability_account,
            credit_account=self.asset_account,
            created_by=self.user
        )
        
        # Varlık hesabı bakiyesi kontrolü
        self.assertEqual(self.asset_account.get_balance(), Decimal('500.00'))
        # Borç hesabı bakiyesi kontrolü
        self.assertEqual(self.liability_account.get_balance(), Decimal('500.00'))

    def test_invoice_payment(self):
        """Fatura ödeme testi"""
        # Fatura oluştur
        invoice = Invoice.objects.create(
            invoice_number='TEST-002',
            date='2024-01-01',
            due_date='2024-02-01',
            amount=Decimal('1000.00'),
            account=self.income_account,
            created_by=self.user
        )
        
        # Ödeme işlemi
        Transaction.objects.create(
            date='2024-01-15',
            description='Fatura Ödemesi',
            amount=Decimal('1000.00'),
            debit_account=self.liability_account,
            credit_account=self.asset_account,
            invoice=invoice,
            created_by=self.user
        )
        
        # Fatura durumu kontrolü
        self.assertEqual(invoice.status, 'paid')
        self.assertEqual(invoice.paid_amount, Decimal('1000.00'))
