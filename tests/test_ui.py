"""
Finans modülü için UI testleri.
"""
import pytest
from django.test import LiveServerTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from decimal import Decimal
from datetime import datetime, timedelta
from selenium.common.exceptions import TimeoutException

User = get_user_model()

@pytest.fixture(scope='session')
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

class TestUI:
    def test_home_page_loads(self, browser, live_server):
        browser.get(live_server.url)
        assert "FinAsis" in browser.title

    def test_login_form(self, browser, live_server):
        browser.get(f"{live_server.url}/login")
        
        username = browser.find_element(By.NAME, "username")
        password = browser.find_element(By.NAME, "password")
        submit = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        username.send_keys("testuser")
        password.send_keys("testpass123")
        submit.click()
        
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
            )
            assert True
        except TimeoutException:
            assert False, "Login başarısız"

    def test_responsive_design(self, browser, live_server):
        browser.get(live_server.url)
        
        # Mobil görünüm
        browser.set_window_size(375, 812)  # iPhone X
        assert browser.find_element(By.CSS_SELECTOR, ".navbar-toggler").is_displayed()
        
        # Tablet görünüm
        browser.set_window_size(768, 1024)  # iPad
        assert not browser.find_element(By.CSS_SELECTOR, ".navbar-toggler").is_displayed()
        
        # Masaüstü görünüm
        browser.set_window_size(1920, 1080)
        assert not browser.find_element(By.CSS_SELECTOR, ".navbar-toggler").is_displayed()

    def test_form_validation(self, browser, live_server):
        browser.get(f"{live_server.url}/register")
        
        submit = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit.click()
        
        error_messages = browser.find_elements(By.CSS_SELECTOR, ".invalid-feedback")
        assert len(error_messages) > 0

    def test_ajax_loading(self, browser, live_server):
        browser.get(live_server.url)
        
        # AJAX tetikleyici buton
        button = browser.find_element(By.CSS_SELECTOR, ".load-data")
        button.click()
        
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".loading-spinner"))
            )
            WebDriverWait(browser, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-spinner"))
            )
            assert True
        except TimeoutException:
            assert False, "AJAX yükleme başarısız"

    def test_error_pages(self, browser, live_server):
        # 404 sayfası
        browser.get(f"{live_server.url}/non-existent-page")
        assert "404" in browser.page_source
        
        # 500 sayfası
        browser.get(f"{live_server.url}/error-test")
        assert "500" in browser.page_source

@pytest.mark.webtest
class InvoiceUITests(LiveServerTestCase):
    """Fatura UI testleri."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Headless Chrome ayarları
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
    def setUp(self):
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # İlgili modelleri import et
        from finance.accounting.models import Invoice, Customer
        
        # Test müşterisi oluştur
        self.customer = Customer.objects.create(
            name="Test Müşteri",
            tax_id="1234567890",
            address="Test Adres"
        )
        
        # Test faturası oluştur
        self.invoice = Invoice.objects.create(
            customer=self.customer,
            invoice_number="INV-2023-001",
            issue_date=datetime.now().date(),
            due_date=datetime.now().date() + timedelta(days=30),
            total_amount=Decimal("1180.00"),
            status="DRAFT"
        )
    
    def test_invoice_list_page(self):
        """Fatura listesi sayfası testi."""
        # Giriş yap
        self.selenium.get(f"{self.live_server_url}/login/")
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys("testuser")
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys("testpassword")
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Fatura listesi sayfasına git
        self.selenium.get(f"{self.live_server_url}/finance/invoices/")
        
        # Sayfanın yüklendiğini doğrula
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "invoice-list"))
        )
        
        # Faturanın listede göründüğünü doğrula
        invoice_element = self.selenium.find_element(By.XPATH, f"//tr[contains(., '{self.invoice.invoice_number}')]")
        self.assertIsNotNone(invoice_element)
        
        # Müşteri adının göründüğünü doğrula
        customer_name = invoice_element.find_element(By.XPATH, "./td[contains(@class, 'customer-name')]").text
        self.assertEqual(customer_name, self.customer.name)
        
        # Fatura tutarının göründüğünü doğrula
        amount = invoice_element.find_element(By.XPATH, "./td[contains(@class, 'amount')]").text
        self.assertIn("1.180,00", amount)
    
    def test_invoice_create_page(self):
        """Fatura oluşturma sayfası testi."""
        # Giriş yap
        self.selenium.get(f"{self.live_server_url}/login/")
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys("testuser")
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys("testpassword")
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Fatura oluşturma sayfasına git
        self.selenium.get(f"{self.live_server_url}/finance/invoices/create/")
        
        # Sayfanın yüklendiğini doğrula
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "invoice-form"))
        )
        
        # Fatura formunu doldur
        # Müşteri seç
        customer_select = self.selenium.find_element(By.ID, "id_customer")
        customer_option = customer_select.find_element(By.XPATH, f"//option[contains(text(), '{self.customer.name}')]")
        customer_option.click()
        
        # Fatura numarası gir
        invoice_number_input = self.selenium.find_element(By.ID, "id_invoice_number")
        invoice_number_input.send_keys("INV-2023-002")
        
        # Fatura tutarı gir
        amount_input = self.selenium.find_element(By.ID, "id_total_amount")
        amount_input.send_keys("2360.00")
        
        # Formu gönder
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Fatura listesi sayfasına yönlendirildiğini doğrula
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains("/finance/invoices/")
        )
        
        # Yeni faturanın listede göründüğünü doğrula
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, "//tr[contains(., 'INV-2023-002')]"))
        )


@pytest.mark.webtest
class FinancialDashboardUITests(LiveServerTestCase):
    """Finansal gösterge paneli UI testleri."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Headless Chrome ayarları
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
    def setUp(self):
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # İlgili modelleri import et
        from finance.accounting.models import FinancialTransaction, Account
        
        # Test hesapları oluştur
        self.income_account = Account.objects.create(
            name="Gelir Hesabı",
            code="601",
            type="INCOME",
            balance=Decimal("5000.00")
        )
        
        self.expense_account = Account.objects.create(
            name="Gider Hesabı",
            code="701",
            type="EXPENSE",
            balance=Decimal("2000.00")
        )
        
        # Test işlemleri oluştur
        FinancialTransaction.objects.create(
            account=self.income_account,
            amount=Decimal("5000.00"),
            transaction_type="INCOME",
            description="Satış Geliri",
            transaction_date=datetime.now().date() - timedelta(days=5)
        )
        
        FinancialTransaction.objects.create(
            account=self.expense_account,
            amount=Decimal("2000.00"),
            transaction_type="EXPENSE",
            description="Kira Gideri",
            transaction_date=datetime.now().date() - timedelta(days=2)
        )
    
    def test_dashboard_page(self):
        """Gösterge paneli sayfası testi."""
        # Giriş yap
        self.selenium.get(f"{self.live_server_url}/login/")
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys("testuser")
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys("testpassword")
        self.selenium.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Gösterge paneli sayfasına git
        self.selenium.get(f"{self.live_server_url}/finance/dashboard/")
        
        # Sayfanın yüklendiğini doğrula
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "financial-dashboard"))
        )
        
        # Toplam gelir kutucuğunu kontrol et
        income_element = self.selenium.find_element(By.ID, "total-income")
        self.assertIn("5.000,00", income_element.text)
        
        # Toplam gider kutucuğunu kontrol et
        expense_element = self.selenium.find_element(By.ID, "total-expense")
        self.assertIn("2.000,00", expense_element.text)
        
        # Net kâr kutucuğunu kontrol et
        profit_element = self.selenium.find_element(By.ID, "net-profit")
        self.assertIn("3.000,00", profit_element.text)
        
        # Grafiklerin yüklendiğini doğrula
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "income-expense-chart"))
        )
        
        # İşlem tablosunun yüklendiğini doğrula
        transactions_table = self.selenium.find_element(By.ID, "recent-transactions")
        transaction_rows = transactions_table.find_elements(By.TAG_NAME, "tr")
        # Başlık satırı hariç en az 2 işlem satırı olmalı
        self.assertGreaterEqual(len(transaction_rows) - 1, 2) 