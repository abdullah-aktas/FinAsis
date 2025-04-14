"""
Pytest yapılandırma dosyası.
"""
import pytest
from django.conf import settings

@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient() 