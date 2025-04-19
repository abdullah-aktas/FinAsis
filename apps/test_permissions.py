"""
İzin sistemi için test dosyası.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from apps.permissions.models import Role, Permission, UserRole
from apps.permissions.utils import check_user_role, check_module_permission
from apps.permissions import ROLE_PERMISSIONS_MAP

User = get_user_model()

@pytest.fixture
def admin_user():
    """Admin rolünde bir kullanıcı oluşturur."""
    return User.objects.create_user(
        username='admin_user',
        email='admin@example.com',
        password='password123',
        role='admin',
        is_staff=True,
    )

@pytest.fixture
def finance_user():
    """Finans sorumlusu rolünde bir kullanıcı oluşturur."""
    return User.objects.create_user(
        username='finance_user',
        email='finance@example.com',
        password='password123',
        role='finance_manager',
    )

@pytest.fixture
def stock_user():
    """Depo yetkilisi rolünde bir kullanıcı oluşturur."""
    return User.objects.create_user(
        username='stock_user',
        email='stock@example.com',
        password='password123',
        role='stock_operator',
    )

@pytest.fixture
def regular_user():
    """Normal bir kullanıcı oluşturur."""
    return User.objects.create_user(
        username='regular_user',
        email='user@example.com',
        password='password123',
        role='guest',
    )

@pytest.fixture
def api_client():
    """Test için API client oluşturur."""
    return APIClient()


class TestRoleBasedPermissions:
    """Rol tabanlı izin sistemi testleri."""
    
    def test_check_user_role(self, admin_user, finance_user, regular_user):
        """check_user_role fonksiyonunu test eder."""
        # Admin kullanıcı her role sahip olabilir
        assert check_user_role(admin_user, 'admin') is True
        assert check_user_role(admin_user, 'finance_manager') is True
        assert check_user_role(admin_user, 'stock_operator') is True
        
        # Finans kullanıcısı sadece kendi rolüne sahip
        assert check_user_role(finance_user, 'finance_manager') is True
        assert check_user_role(finance_user, 'admin') is False
        assert check_user_role(finance_user, 'stock_operator') is False
        
        # Normal kullanıcı sadece misafir rolüne sahip
        assert check_user_role(regular_user, 'guest') is True
        assert check_user_role(regular_user, 'admin') is False
        
        # Liste olarak rol kontrolü
        assert check_user_role(finance_user, ['finance_manager', 'admin']) is True
        assert check_user_role(regular_user, ['finance_manager', 'admin']) is False
    
    def test_check_module_permission(self, admin_user, finance_user, stock_user, regular_user):
        """check_module_permission fonksiyonunu test eder."""
        # Admin kullanıcı tüm modüllere tam erişime sahip
        assert check_module_permission(admin_user, 'finance', 'create') is True
        assert check_module_permission(admin_user, 'stock', 'update') is True
        assert check_module_permission(admin_user, 'accounting', 'delete') is True
        
        # Finans kullanıcısı finans modülüne tam erişime sahip
        assert check_module_permission(finance_user, 'finance', 'create') is True
        assert check_module_permission(finance_user, 'finance', 'update') is True
        assert check_module_permission(finance_user, 'finance', 'delete') is True
        
        # Finans kullanıcısı muhasebe modülüne sınırlı erişime sahip
        assert check_module_permission(finance_user, 'accounting', 'view') is True
        assert check_module_permission(finance_user, 'accounting', 'update') is True
        assert check_module_permission(finance_user, 'accounting', 'delete') is False
        
        # Stok kullanıcısı stok modülüne tam erişime sahip
        assert check_module_permission(stock_user, 'stock', 'create') is True
        assert check_module_permission(stock_user, 'stock', 'delete') is True
        
        # Stok kullanıcısı muhasebe modülüne sınırlı erişime sahip
        assert check_module_permission(stock_user, 'accounting', 'view') is True
        assert check_module_permission(stock_user, 'accounting', 'update') is False
        
        # Normal kullanıcı sadece raporları görüntüleyebilir
        assert check_module_permission(regular_user, 'reports', 'view') is True
        assert check_module_permission(regular_user, 'finance', 'view') is False
    
    def test_api_access(self, admin_user, finance_user, stock_user, regular_user, api_client):
        """API erişim kontrolleri test eder."""
        # Token alma işlemi (normalde JWT kullanılır)
        api_client.force_authenticate(user=admin_user)
        
        # Admin kullanıcı tüm endpointlere erişebilir
        response = api_client.get(reverse('api:finance'))
        assert response.status_code == status.HTTP_200_OK
        
        response = api_client.get(reverse('api:stock'))
        assert response.status_code == status.HTTP_200_OK
        
        response = api_client.get(reverse('api:accounting'))
        assert response.status_code == status.HTTP_200_OK
        
        # Stok kullanıcısı sadece stok endpointine erişebilir
        api_client.force_authenticate(user=stock_user)
        
        response = api_client.get(reverse('api:stock'))
        assert response.status_code == status.HTTP_200_OK
        
        response = api_client.get(reverse('api:finance'))
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Finans kullanıcısı sadece finans endpointine erişebilir
        api_client.force_authenticate(user=finance_user)
        
        response = api_client.get(reverse('api:finance'))
        assert response.status_code == status.HTTP_200_OK
        
        response = api_client.get(reverse('api:stock'))
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Normal kullanıcı hiçbir endpointe erişemez
        api_client.force_authenticate(user=regular_user)
        
        response = api_client.get(reverse('api:finance'))
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        response = api_client.get(reverse('api:stock'))
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_model_permission(self, admin_user, finance_user, stock_user, api_client):
        """ModulePermission sınıfını test eder."""
        # Admin kullanıcı her modüle erişebilir ve her işlemi yapabilir
        api_client.force_authenticate(user=admin_user)
        
        response = api_client.get(reverse('api:products'))
        assert response.status_code == status.HTTP_200_OK
        
        response = api_client.post(reverse('api:products'), {})
        assert response.status_code == status.HTTP_201_CREATED
        
        response = api_client.get(reverse('api:invoices'))
        assert response.status_code == status.HTTP_200_OK
        
        # Stok kullanıcısı ürünlere erişebilir ve oluşturabilir
        api_client.force_authenticate(user=stock_user)
        
        response = api_client.get(reverse('api:products'))
        assert response.status_code == status.HTTP_200_OK
        
        response = api_client.post(reverse('api:products'), {})
        assert response.status_code == status.HTTP_201_CREATED
        
        # Ama faturalara erişemez
        response = api_client.get(reverse('api:invoices'))
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Finans kullanıcısı faturalara erişebilir ve oluşturabilir
        api_client.force_authenticate(user=finance_user)
        
        response = api_client.get(reverse('api:invoices'))
        assert response.status_code == status.HTTP_200_OK
        
        response = api_client.post(reverse('api:invoices'), {})
        assert response.status_code == status.HTTP_201_CREATED 