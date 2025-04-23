"""
Pytest yapılandırma dosyası.
"""
import pytest
from django.test import Client
from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings

@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default']['TEST'] = {
        'NAME': 'test_db',
        'CHARSET': 'UTF8',
        'COLLATION': 'utf8_general_ci',
    }

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )

@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()

@pytest.fixture
def authenticated_client(client, user):
    client.login(username='testuser', password='testpass123')
    return client 