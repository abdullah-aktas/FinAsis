# -*- coding: utf-8 -*-
import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from celery.schedules import crontab
from datetime import timedelta
import traceback
import sys
from dotenv import load_dotenv
import logging.config

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'test')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Database settings
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', ''),
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache session backend
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('tr', _('Türkçe')),
    ('en', _('English')),
    ('ku', _('Kurdî')),
    ('ar', _('العربية')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS settings
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = True

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Istanbul'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 3600
CELERY_TASK_SOFT_TIME_LIMIT = 3000
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_DEFAULT_RETRY_DELAY = 300
CELERY_TASK_MAX_RETRIES = 3
CELERY_RESULT_EXPIRES = 3600
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Celery Beat Ayarları
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BEAT_SCHEDULE = {
    'check-overdue-activities': {
        'task': 'crm.tasks.check_overdue_activities',
        'schedule': crontab(minute='*/15'),
    },
    'update-customer-credit-scores': {
        'task': 'crm.tasks.update_customer_credit_scores', 
        'schedule': crontab(hour='*/6'),
    },
    'process-seasonal-campaigns': {
        'task': 'crm.tasks.process_seasonal_campaigns',
        'schedule': crontab(hour='*/12'),
    },
    'send-opportunity-reminders': {
        'task': 'crm.tasks.send_opportunity_reminders',
        'schedule': crontab(hour='*/1'),
    },
    'check-expired-documents': {
        # 'task': 'edocument.tasks.check_expired_documents',  # KALDIRILDI veya yoruma alındı
        # 'schedule': crontab(hour=0, minute=0),  # Her gün gece yarısı çalışır
    },
}

# Logging ayarları
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
}

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@finasis.com')

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Custom settings
FINASIS = {
    'COMPANY_NAME': os.getenv('COMPANY_NAME', 'FinAsis'),
    'COMPANY_EMAIL': os.getenv('COMPANY_EMAIL', 'info@finasis.com'),
    'COMPANY_PHONE': os.getenv('COMPANY_PHONE', '+90 212 123 45 67'),
    'COMPANY_ADDRESS': os.getenv('COMPANY_ADDRESS', 'İstanbul, Türkiye'),
    'SUPPORT_EMAIL': os.getenv('SUPPORT_EMAIL', 'support@finasis.com'),
    'DOCUMENT_STORAGE_PATH': os.getenv('DOCUMENT_STORAGE_PATH', BASE_DIR / 'documents'),
    'MAX_DOCUMENT_SIZE': int(os.getenv('MAX_DOCUMENT_SIZE', 10 * 1024 * 1024)),  # 10 MB
    'ALLOWED_DOCUMENT_TYPES': os.getenv('ALLOWED_DOCUMENT_TYPES', 'pdf,doc,docx,xls,xlsx').split(','),
    'DEFAULT_CURRENCY': os.getenv('DEFAULT_CURRENCY', 'TRY'),
    'DATE_FORMAT': os.getenv('DATE_FORMAT', '%d.%m.%Y'),
    'DATETIME_FORMAT': os.getenv('DATETIME_FORMAT', '%d.%m.%Y %H:%M:%S'),
    'TIME_FORMAT': os.getenv('TIME_FORMAT', '%H:%M:%S'),
    'DECIMAL_SEPARATOR': os.getenv('DECIMAL_SEPARATOR', ','),
    'THOUSAND_SEPARATOR': os.getenv('THOUSAND_SEPARATOR', '.'),
}

# Channels Configuration
ASGI_APPLICATION = 'FinAsis.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# Rate Limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Cacheops Configuration
CACHEOPS_REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 1,
    'socket_timeout': 3,
}

CACHEOPS = {
    'auth.*': {'ops': 'all', 'timeout': 60*15},
    'games.*': {'ops': 'all', 'timeout': 60*15},
    '*.*': {'ops': (), 'timeout': 60*15},
}

# Ethereum Blockchain Ayarları
ETHEREUM_NODE_URL = 'https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'  # Testnet için: https://ropsten.infura.io/v3/YOUR_INFURA_PROJECT_ID
ETHEREUM_PRIVATE_KEY = 'YOUR_PRIVATE_KEY'  # Güvenli bir şekilde saklanmalı
ETHEREUM_CHAIN_ID = 1  # Mainnet için 1, Ropsten için 3
ETHEREUM_CONTRACT_ADDRESS = 'YOUR_CONTRACT_ADDRESS'
ETHEREUM_CONTRACT_ABI = [
    {
        "inputs": [
            {"name": "title", "type": "string"},
            {"name": "description", "type": "string"},
            {"name": "amount", "type": "uint256"},
            {"name": "parties", "type": "address[]"}
        ],
        "name": "createContract",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "title",
        "outputs": [{"name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "description",
        "outputs": [{"name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "amount",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "parties",
        "outputs": [{"name": "", "type": "address[]"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "status",
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "createdAt",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'FinAsis.urls'