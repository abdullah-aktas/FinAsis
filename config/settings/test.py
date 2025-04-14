"""
Test ortamı ayarları
"""
from .base import *

# Test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Password hashers
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# Disable celery tasks during tests
CELERY_ALWAYS_EAGER = True 