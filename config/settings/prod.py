# -*- coding: utf-8 -*-
"""
Üretim ortamı ayarları
"""
from .base import *
from typing import List
from datetime import timedelta
import os
import environ

# Create logs directory if it doesn't exist
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

env = environ.Env()

DEBUG = False

# Host settings
ALLOWED_HOSTS: List[str] = os.environ.get('ALLOWED_HOSTS', 'finasis.com.tr').split(',')

# Static/Media Settings
STATIC_ROOT = '/var/www/finasis/static'
STATIC_URL = '/static/'
MEDIA_ROOT = '/var/www/finasis/media'
MEDIA_URL = '/media/'

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 yıl
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'", "https://www.google-analytics.com", "https://cdn.jsdelivr.net")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com", "https://cdn.jsdelivr.net")
CSP_IMG_SRC = ("'self'", "data:", "https://www.google-analytics.com", "https://*.amazonaws.com")
CSP_CONNECT_SRC = ("'self'", "https://api.finasis.com.tr", "wss://*.finasis.com.tr")
CSP_FRAME_SRC = ("'self'",)
CSP_OBJECT_SRC = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
CSP_FRAME_ANCESTORS = ("'self'",)

# Database settings  
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'finasis'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
            'client_encoding': 'UTF8'
        }
    }
}

# Cloud SQL settings (if needed)
if os.environ.get('USE_CLOUD_SQL_AUTH_PROXY', 'False').lower() == 'true':
    DATABASES['default']['HOST'] = '/cloudsql/' + os.environ.get('CLOUD_SQL_CONNECTION_NAME', '')
    DATABASES['default']['PORT'] = ''

# Veritabanı yedekleme için ikinci bağlantı (salt okunur)
if os.environ.get('DB_USE_READONLY_REPLICA', 'False') == 'True':
    DATABASES['replica'] = {
        'ENGINE': os.environ.get('DB_ENGINE'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_REPLICA_USER', os.environ.get('DB_USER')),
        'PASSWORD': os.environ.get('DB_REPLICA_PASSWORD', os.environ.get('DB_PASSWORD')),
        'HOST': os.environ.get('DB_REPLICA_HOST', os.environ.get('DB_HOST')),
        'PORT': os.environ.get('DB_REPLICA_PORT', os.environ.get('DB_PORT')),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
            'client_encoding': 'UTF8',
            'application_name': 'FinAsis-ReadOnly',
            'sslmode': os.environ.get('DB_SSL_MODE', 'prefer'),
        },
    }

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'RETRY_ON_TIMEOUT': True,
            'MAX_CONNECTIONS': 1000,
            'CONNECTION_POOL_KWARGS': {'max_connections': 100},
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'finasis_prod',
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'RETRY_ON_TIMEOUT': True,
            'MAX_CONNECTIONS': 500,
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
        },
        'KEY_PREFIX': 'finasis_session',
    },
    'throttling': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'RETRY_ON_TIMEOUT': True,
        },
        'KEY_PREFIX': 'finasis_throttle',
    },
}

# Cache önbelleği kullan
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
SESSION_COOKIE_AGE = 86400  # 1 gün
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)
EMAIL_TIMEOUT = 30  # 30 saniye timeout
EMAIL_SUBJECT_PREFIX = '[FinAsis] '

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
            'datefmt': '%Y-%m-%dT%H:%M:%S%z'
        }
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'json'
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    }
}

# AWS S3 Configuration for static and media files
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', None)
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'eu-central-1')
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN', f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com')
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400,s-maxage=86400',
    'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
}
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False
AWS_S3_VERIFY = True

# StaticFiles ve MediaFiles ayarları
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'

# Security Middleware
MIDDLEWARE += [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',
    'core.middleware.HealthCheckMiddleware',  # Sağlık kontrolü için middleware
    'core.middleware.SecurityHeadersMiddleware',  # Ek güvenlik başlıkları
]

# Rate Limiting
RATELIMIT_ENABLE = os.environ.get('RATELIMIT_ENABLE', 'True') == 'True'
RATELIMIT_USE_CACHE = 'throttling'
RATELIMIT_KEY_PREFIX = os.environ.get('RATELIMIT_KEY_PREFIX', 'finasis_prod')
RATELIMIT_RATE = os.environ.get('RATELIMIT_RATE', '100/h')
RATELIMIT_BLOCK = os.environ.get('RATELIMIT_BLOCK', 'True') == 'True'
RATELIMIT_VIEW = 'core.views.rate_limited'

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('REDIS_URL')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Istanbul'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 3600,  # 1 saat
    'fanout_prefix': True,
    'fanout_patterns': True,
}
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_RESULT_EXTENDED = True
CELERY_TASK_ALWAYS_EAGER = False
CELERY_IGNORE_RESULT = False
CELERY_TASK_STORE_ERRORS_EVEN_IF_IGNORED = True

# Sentry Configuration
SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
        send_default_pii=True,
        environment=os.environ.get('SENTRY_ENVIRONMENT', 'production'),
        release=os.environ.get('RELEASE_VERSION', '0.1.0'),
        sample_rate=float(os.environ.get('SENTRY_SAMPLE_RATE', '0.2')),
        max_breadcrumbs=50,
        attach_stacktrace=True,
        in_app_include=['finasis', 'apps', 'core', 'edocument'],
    )

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': os.environ.get('THROTTLE_RATE_ANON', '100/day'),
        'user': os.environ.get('THROTTLE_RATE_USER', '1000/day'),
        'login': os.environ.get('THROTTLE_RATE_LOGIN', '5/minute'),
        'token_obtain': os.environ.get('THROTTLE_RATE_TOKEN_OBTAIN', '5/minute'),
        'token_refresh': os.environ.get('THROTTLE_RATE_TOKEN_REFRESH', '20/hour'),
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': int(os.environ.get('REST_API_PAGE_SIZE', '10')),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
    'EXCEPTION_HANDLER': 'api.handlers.custom_exception_handler',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', '60'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME_DAYS', '1'))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'FinAsis',
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
}
ORS_ALLOW_CREDENTIALS = True
# CORS settingsCORS_ALLOW_METHODS = [
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'https://finasis.com.tr,https://www.finasis.com.tr,https://api.finasis.com.tr').split(',')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cache-control',
]
CORS_EXPOSE_HEADERS = [
    'content-disposition',
]  # Dil ayarları
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 saat 'tr'

# Dil ayarları
LANGUAGE_CODE = 'tr'
LANGUAGES = [
    ('tr', 'Türkçe'),
    ('en', 'English'),
    ('ar', 'العربية'),
    ('ku', 'Kurdî'),
    ('de', 'Deutsch'),
]

# E-Belge Ayarları
EDOCUMENT_LOG_LEVEL = 'INFO'
EDOCUMENT_LOG_FILE = os.path.join(BASE_DIR, 'logs', 'edocument.log')
EDOCUMENT_STORAGE_PATH = os.path.join(BASE_DIR, 'media', 'edocuments')
os.makedirs(EDOCUMENT_STORAGE_PATH, exist_ok=True)

# Yetkilendirme Ayarları
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ['username', 'email', 'first_name', 'last_name'],
            'max_similarity': 0.7,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Admin Ayarları
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')
ADMINS = [tuple(admin.split(':')) for admin in os.environ.get('ADMINS', 'Admin:admin@finasis.com.tr').split(',')]
MANAGERS = ADMINS