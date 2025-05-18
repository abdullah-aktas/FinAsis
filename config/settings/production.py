# -*- coding: utf-8 -*-
"""
Canlı ortam için Django ayarları
Bu dosya, canlı ortamda (production) kullanılacak özel ayarları içerir.
"""
import os
from datetime import timedelta
from core.settings import *
from config.settings.base import BASE_DIR, TIME_ZONE

# Güvenlik Ayarları
DEBUG = False
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')

# Statik ve Media URL'leri
STATIC_URL = os.getenv('STATIC_URL', '/static/')
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')

# PostgreSQL Veritabanı ayarları
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', 600)),
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',
        },
    }
}

# Redis Cache Ayarları
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            },
            'MAX_CONNECTIONS': 1000,
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'finasis'
    }
}

# Email ayarları
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Güvenlik ayarları
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 yıl
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Statik dosya toplama
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Celery Ayarları
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_WORKER_CONCURRENCY = int(os.getenv('CELERY_WORKER_CONCURRENCY', 4))
CELERY_WORKER_MAX_TASKS_PER_CHILD = int(os.getenv('CELERY_WORKER_MAX_TASKS_PER_CHILD', 1000))
CELERY_WORKER_MAX_MEMORY_PER_CHILD = int(os.getenv('CELERY_WORKER_MAX_MEMORY_PER_CHILD', 200000))  # KB
CELERY_WORKER_PREFETCH_MULTIPLIER = int(os.getenv('CELERY_WORKER_PREFETCH_MULTIPLIER', 1))
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_TIME_LIMIT = int(os.getenv('CELERY_TASK_TIME_LIMIT', 5 * 60))  # 5 dakika
CELERY_TASK_SOFT_TIME_LIMIT = int(os.getenv('CELERY_TASK_SOFT_TIME_LIMIT', 4 * 60))  # 4 dakika

# Günlük dosyaları yapılandırması
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'debug.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'celery': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'celery.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['celery', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'finasis': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# Sentry yapılandırması (opsiyonel hata izleme)
if os.getenv('SENTRY_DSN'):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration()
        ],
        # Örnekleme oranı: 1.0 tüm olayları gönderir
        traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', 0.1)),
        # İşlem başlangıçlarını performans izleme için gönderir
        send_default_pii=True,
        environment=os.getenv('SENTRY_ENVIRONMENT', 'production'),
    )

# Ek üretim ortamı ayarları
VERSION = os.getenv('VERSION', '1.0.0')

# INSTALLED_APPS += [
#     'django_otp',
#     'two_factor',
# ] 