import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User
from integrations.models import BankIntegration
import os
from django.test import TestCase, Client
from .models import Profile

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.mark.django_db
class TestUserRegistration:
    def test_user_registration_success(self, api_client):
        url = reverse('accounts:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username='newuser').exists()

    def test_user_registration_invalid_data(self, api_client):
        url = reverse('accounts:register')
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'short',
            'password2': 'short'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestUserLogin:
    def test_user_login_success(self, api_client, test_user):
        url = reverse('accounts:login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data

    def test_user_login_invalid_credentials(self, api_client):
        url = reverse('accounts:login')
        data = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestUserProfile:
    def test_get_user_profile(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        url = reverse('accounts:profile')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == test_user.username
        assert response.data['email'] == test_user.email

    def test_update_user_profile(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        url = reverse('accounts:profile')
        data = {
            'first_name': 'Test',
            'last_name': 'hr_management.User'
        }
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        test_user.refresh_from_db()
        assert test_user.first_name == 'Test'
        assert test_user.last_name == 'hr_management.User'

# Örnek entegrasyon yapısı
class IntegrationManager:
    def __init__(self):
        self.integrations = {
            'bank': BankIntegration(),
            'e_invoice': EInvoiceIntegration(),
            'pos': POSIntegration(),
            'erp': ERPIntegration()
        }

# Gelişmiş raporlama modülü
class AdvancedReporting:
    def generate_financial_report(self, company, period):
        return {
            'balance_sheet': self.generate_balance_sheet(company, period),
            'income_statement': self.generate_income_statement(company, period),
            'cash_flow': self.generate_cash_flow(company, period),
            'financial_ratios': self.calculate_financial_ratios(company, period)
        }

# Üretim yönetimi modülü
class ProductionManagement:
    def __init__(self):
        self.bom_manager = BillOfMaterialsManager()
        self.inventory_manager = InventoryManager()
        self.quality_control = QualityControl()

# Dil yönetimi
class LanguageManager:
    def __init__(self):
        self.supported_languages = ['tr', 'en', 'de', 'fr']
        self.translations = self.load_translations()

# API yapılandırması
class APIManager:
    def __init__(self):
        self.version = 'v2'
        self.endpoints = {
            'accounting': AccountingAPI(),
            'inventory': InventoryAPI(),
            'production': ProductionAPI(),
            'reporting': ReportingAPI()
        }

# Önbellekleme yapılandırması
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            }
        }
    }
}

# Güvenlik ayarları
SECURITY_SETTINGS = {
    'SSL_REDIRECT': True,
    'SESSION_COOKIE_SECURE': True,
    'CSRF_COOKIE_SECURE': True,
    'SECURE_BROWSER_XSS_FILTER': True,
    'SECURE_CONTENT_TYPE_NOSNIFF': True,
    'X_FRAME_OPTIONS': 'DENY',
    'SECURE_HSTS_SECONDS': 31536000,
    'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
    'SECURE_HSTS_PRELOAD': True
}

# Entegrasyon sınıfları
class EInvoiceIntegration:
    def __init__(self):
        self.name = "E-Fatura Entegrasyonu"
        self.status = "active"

class POSIntegration:
    def __init__(self):
        self.name = "POS Entegrasyonu"
        self.status = "active"

class ERPIntegration:
    def __init__(self):
        self.name = "ERP Entegrasyonu"
        self.status = "active"

# Üretim yönetimi sınıfları
class BillOfMaterialsManager:
    def __init__(self):
        self.name = "BOM Yöneticisi"
        self.status = "active"

class InventoryManager:
    def __init__(self):
        self.name = "Envanter Yöneticisi"
        self.status = "active"

class QualityControl:
    def __init__(self):
        self.name = "Kalite Kontrol"
        self.status = "active"

# API sınıfları
class AccountingAPI:
    def __init__(self):
        self.name = "Muhasebe API"
        self.version = "v1"

class InventoryAPI:
    def __init__(self):
        self.name = "Envanter API"
        self.version = "v1"

class ProductionAPI:
    def __init__(self):
        self.name = "Üretim API"
        self.version = "v1"

class ReportingAPI:
    def __init__(self):
        self.name = "Raporlama API"
        self.version = "v1"

class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            phone_number='5551234567'
        )

    def test_login_view(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_register_view(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_profile_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home')) 