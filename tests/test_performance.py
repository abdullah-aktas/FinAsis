"""
Kritik finansal işlemler için performans testleri.
"""
import pytest
import time
import json
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import connection, reset_queries
import random
import string
from locust import HttpUser, task, between
from random import choice, randint

User = get_user_model()

def random_string(length=10):
    """Belirtilen uzunlukta rastgele string oluşturur."""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

@pytest.mark.slow
class FinancialTransactionPerformanceTests(TransactionTestCase):
    """Finansal işlem performans testleri."""
    
    def setUp(self):
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # İlgili modelleri import et
        from finance.accounting.models import Account
        
        # Test hesabı oluştur
        self.account = Account.objects.create(
            name="Test Hesabı",
            code="101",
            type="ASSET",
            balance=Decimal("10000.00")
        )
    
    def test_bulk_transaction_creation_performance(self):
        """Toplu işlem oluşturma performans testi."""
        from finance.accounting.models import FinancialTransaction
        
        num_transactions = 100
        start_time = time.time()
        
        reset_queries()  # SQL sorgularını sıfırla
        
        # Toplu işlem oluştur
        transactions = []
        for i in range(num_transactions):
            transaction = FinancialTransaction(
                account=self.account,
                amount=Decimal(random.uniform(10.0, 1000.0)).quantize(Decimal('0.01')),
                transaction_type="EXPENSE" if i % 2 == 0 else "INCOME",
                description=f"Test İşlem {i}",
                transaction_date=datetime.now().date() - timedelta(days=random.randint(0, 30))
            )
            transactions.append(transaction)
        
        # Bulk create ile veritabanına ekle
        FinancialTransaction.objects.bulk_create(transactions)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Sorgu sayısını doğrula (bulk create 1 sorgu kullanmalı)
        self.assertLessEqual(len(connection.queries), 5)
        
        # Oluşturma süresini doğrula (100 işlem için 1 saniyeden az olmalı)
        self.assertLess(execution_time, 1.0)
        
        # İşlemlerin oluşturulduğunu doğrula
        self.assertEqual(FinancialTransaction.objects.count(), num_transactions)
        
        print(f"\nToplu işlem oluşturma süresi: {execution_time:.4f} saniye")
        print(f"İşlem başına ortalama süre: {(execution_time / num_transactions):.6f} saniye")
        print(f"Kullanılan sorgu sayısı: {len(connection.queries)}")


@pytest.mark.slow
class InvoiceAPIPerformanceTests(TestCase):
    """Fatura API performans testleri."""
    
    def setUp(self):
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # API istemcisi oluştur
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # İlgili modelleri import et
        from finance.accounting.models import Customer
        
        # Test müşterileri oluştur
        for i in range(20):
            Customer.objects.create(
                name=f"Test Müşteri {i}",
                tax_id=f"123456789{i}",
                address=f"Test Adres {i}"
            )
    
    def test_invoice_list_api_performance(self):
        """Fatura listesi API performans testi."""
        from finance.accounting.models import Invoice, Customer
        
        # Test faturaları oluştur (100 fatura)
        customers = Customer.objects.all()
        for i in range(100):
            customer = random.choice(customers)
            Invoice.objects.create(
                customer=customer,
                invoice_number=f"INV-2023-{i+1:03d}",
                issue_date=datetime.now().date() - timedelta(days=random.randint(0, 30)),
                due_date=datetime.now().date() + timedelta(days=random.randint(0, 30)),
                total_amount=Decimal(random.uniform(100.0, 10000.0)).quantize(Decimal('0.01')),
                status=random.choice(["DRAFT", "APPROVED", "PAID"])
            )
        
        reset_queries()  # SQL sorgularını sıfırla
        
        # API isteği gönder ve süreyi ölç
        start_time = time.time()
        response = self.client.get(reverse('invoice-list'))
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Başarı durumunu kontrol et
        self.assertEqual(response.status_code, 200)
        
        # Veri sayısını kontrol et
        self.assertEqual(len(response.data), 100)
        
        # Sorgu sayısını doğrula (N+1 sorununu kontrol et)
        query_count = len(connection.queries)
        self.assertLessEqual(query_count, 5)  # select_related ve prefetch_related ile sorgu sayısı az olmalı
        
        # Yanıt süresini kontrol et
        self.assertLess(execution_time, 0.5)  # 500ms'den az olmalı
        
        print(f"\nFatura listesi API yanıt süresi: {execution_time:.4f} saniye")
        print(f"Kullanılan sorgu sayısı: {query_count}")


@pytest.mark.slow
class BankAPIPerformanceTests(TestCase):
    """Banka API performans testleri."""
    
    def setUp(self):
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # API istemcisi oluştur
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # İlgili modelleri import et
        from integrations.bank_integration.models import BankAccount, BankTransaction
        
        # Test banka hesabı oluştur
        self.bank_account = BankAccount.objects.create(
            name="Test Hesabı",
            account_number="TR123456789012345678901234",
            currency="TRY"
        )
        
        # Çok sayıda banka işlemi oluştur
        transactions = []
        for i in range(1000):
            transaction = BankTransaction(
                account=self.bank_account,
                transaction_id=f"TRX{i+1:06d}",
                amount=Decimal(random.uniform(-5000.0, 5000.0)).quantize(Decimal('0.01')),
                description=f"Test İşlem {i}",
                transaction_date=datetime.now().date() - timedelta(days=random.randint(0, 90))
            )
            transactions.append(transaction)
        
        BankTransaction.objects.bulk_create(transactions)
    
    def test_bank_statement_query_performance(self):
        """Banka hesap ekstresi sorgulama performans testi."""
        from django.db.models import Sum
        from integrations.bank_integration.models import BankTransaction
        
        # Tarih aralığı belirle
        start_date = datetime.now().date() - timedelta(days=60)
        end_date = datetime.now().date()
        
        reset_queries()  # SQL sorgularını sıfırla
        
        # Sorguyu ölç
        start_time = time.time()
        
        # Tarih aralığındaki işlemleri getir
        transactions = BankTransaction.objects.filter(
            account=self.bank_account,
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        ).order_by('-transaction_date')
        
        # Toplam işlem hacmini hesapla
        total_credit = transactions.filter(amount__gt=0).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_debit = transactions.filter(amount__lt=0).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # İşlemleri sayfalandır (ilk 100 işlem)
        paginated_transactions = transactions[:100]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Sorgu sayısını kontrol et
        query_count = len(connection.queries)
        
        # Sorgu süresini kontrol et
        self.assertLess(execution_time, 0.3)  # 300ms'den az olmalı
        
        print(f"\nBanka ekstresi sorgulama süresi: {execution_time:.4f} saniye")
        print(f"Kullanılan sorgu sayısı: {query_count}")
        print(f"İşlem sayısı: {transactions.count()}")
        print(f"Toplam Alacak: {total_credit}")
        print(f"Toplam Borç: {total_debit}")

class FinAsisUser(HttpUser):
    wait_time = between(1, 3)  # Her istek arasında 1-3 saniye bekleme
    
    def on_start(self):
        # Kullanıcı girişi
        self.client.post("/api/auth/login/", {
            "email": f"test_user_{randint(1,1000)}@finasis.com",
            "password": "test1234"
        })
    
    @task(3)
    def view_dashboard(self):
        self.client.get("/api/dashboard/")
    
    @task(2)
    def view_transactions(self):
        self.client.get("/api/transactions/")
        
    @task(2)
    def create_invoice(self):
        self.client.post("/api/invoices/", {
            "customer": choice(["ABC Ltd.", "XYZ A.Ş.", "123 Ltd. Şti."]),
            "amount": randint(100, 10000),
            "description": f"Test fatura {randint(1,1000)}"
        })
    
    @task(1)
    def play_game(self):
        self.client.get("/api/games/ticaretin-izinde/")
        self.client.post("/api/games/ticaretin-izinde/score/", {
            "score": randint(100, 1000),
            "time_spent": randint(60, 300)
        })
    
    @task(1)
    def generate_report(self):
        self.client.get("/api/reports/monthly/")
    
    @task(1)
    def search_transactions(self):
        self.client.get(f"/api/transactions/search/?q=test_{randint(1,100)}")

class WebsiteUser(HttpUser):
    wait_time = between(2, 5)
    
    @task(3)
    def view_homepage(self):
        self.client.get("/")
    
    @task(2)
    def view_about(self):
        self.client.get("/about/")
    
    @task(1)
    def view_pricing(self):
        self.client.get("/pricing/")
    
    @task(1)
    def view_contact(self):
        self.client.get("/contact/") 