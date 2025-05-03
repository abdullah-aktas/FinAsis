# -*- coding: utf-8 -*-
from .base import *

DEBUG = False

SECRET_KEY = 'django-insecure-test-key-only-for-ci'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'finasisdb'),
        'USER': os.environ.get('POSTGRES_USER', 'finasisuser'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'testpassword'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Test için mail ayarları
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Test için cache ayarları
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Test için static dosya ayarları
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Test için media dosya ayarları
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Test için güvenlik ayarları
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['http://localhost']

# Test için logging ayarları
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
} 