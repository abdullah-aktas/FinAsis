# -*- coding: utf-8 -*-

"""
FinAsis Analitik Modülü Ayarları
--------------------------------
Bu modül, FinAsis analitik sisteminin temel yapılandırma ayarlarını içerir.
"""

from datetime import timedelta
import os
from typing import Dict, List, Any
from decouple import config, Csv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Temel Güvenlik Ayarları
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'corsheaders',
    'drf_yasg',
    'django_celery_beat',
    'django_celery_results',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.migrations',
    
    # Local apps
    'apps.finance.apps.FinanceConfig',
    'apps.crm.apps.CRMConfig',
    'apps.edocument.apps.EDocumentConfig',
    'apps.accounting.apps.AccountingConfig',
    'apps.banking.apps.BankingConfig',
    'apps.checks.apps.ChecksConfig',
    'apps.permissions.apps.PermissionsConfig',
    'apps.users.apps.UsersConfig',
    'apps.core.apps.CoreConfig',
    'apps.blockchain.apps.BlockchainConfig',
    'apps.ai_assistant.apps.AIAssistantConfig',
    'apps.virtual_company.apps.VirtualCompanyConfig',
    'apps.common.apps.CommonConfig',
]

# Veritabanı ayarları
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
    }
}

# Redis cache ayarları
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{config('REDIS_HOST')}:{config('REDIS_PORT')}/{config('REDIS_DB')}",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Email ayarları
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# AWS S3 ayarları
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

# Statik dosya ayarları
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media dosya ayarları
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Güvenlik ayarları
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Celery ayarları
CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Sentry ayarları
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=config('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)

# Genel Analitik Ayarları
ANALYTICS_SETTINGS = {
    'ENVIRONMENT': os.getenv('ANALYTICS_ENV', 'production'),
    'DEBUG': os.getenv('ANALYTICS_DEBUG', 'False').lower() == 'true',
    'VERSION': '2.0.0',
    'DEFAULT_TIMEZONE': 'Europe/Istanbul',
    'ALLOWED_DATE_FORMATS': ['%Y-%m-%d', '%d.%m.%Y', '%Y/%m/%d'],
    'MAX_QUERY_EXECUTION_TIME': 300,  # saniye
}

# Önbellek Ayarları
ANALYTICS_CACHE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'TIMEOUT': 3600,  # 1 saat
        'KEY_PREFIX': 'finasis_analytics',
        'VERSION': 1,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'RETRY_ON_TIMEOUT': True,
            'MAX_CONNECTIONS': 100,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        }
    },
    'session': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/2'),
        'TIMEOUT': 86400,  # 1 gün
    }
}

# Veri Noktası Limitleri
ANALYTICS_DATA_LIMITS = {
    'MAX_DATA_POINTS': int(os.getenv('MAX_DATA_POINTS', 10000)),
    'MAX_CONCURRENT_QUERIES': int(os.getenv('MAX_CONCURRENT_QUERIES', 5)),
    'MAX_EXPORT_ROWS': int(os.getenv('MAX_EXPORT_ROWS', 100000)),
    'MAX_CHART_SERIES': 10,
    'MAX_DASHBOARD_WIDGETS': 20,
}

# Rate Limiting Ayarları
ANALYTICS_RATE_LIMIT = {
    'default': {
        'max_requests': int(os.getenv('RATE_LIMIT_MAX', 100)),
        'time_window': 60,  # saniye
        'block_time': 300,  # 5 dakika bloke
    },
    'export': {
        'max_requests': 10,
        'time_window': 300,  # 5 dakika
    },
    'api': {
        'max_requests': 1000,
        'time_window': 3600,  # 1 saat
        'per_user': True,
    }
}

# Widget ve Görselleştirme Ayarları
ANALYTICS_VISUALIZATION = {
    'theme': {
        'light': {
            'primary': '#2193B0',
            'secondary': '#6DD5ED',
            'success': '#30B32D',
            'warning': '#FFDD00',
            'danger': '#F03E3E',
            'background': '#FFFFFF',
            'text': '#333333',
        },
        'dark': {
            'primary': '#1A73E8',
            'secondary': '#5C6BC0',
            'success': '#00C853',
            'warning': '#FFD600',
            'danger': '#FF1744',
            'background': '#121212',
            'text': '#FFFFFF',
        }
    },
    'chart_defaults': {
        'responsive': True,
        'maintainAspectRatio': False,
        'animation': {
            'duration': 1000,
            'easing': 'easeInOutQuart'
        },
        'plugins': {
            'legend': {'position': 'top'},
            'tooltip': {'mode': 'index'},
        }
    },
    'supported_types': [
        'line', 'bar', 'pie', 'doughnut', 'radar',
        'polarArea', 'bubble', 'scatter', 'heatmap'
    ]
}

# Veri Kaynağı Ayarları
ANALYTICS_DATA_SOURCES = {
    'database': {
        'max_connections': int(os.getenv('DB_MAX_CONNECTIONS', 20)),
        'timeout': 30,
        'pool_settings': {
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 1800,
        }
    },
    'api': {
        'timeout': 10,
        'retry_attempts': 3,
        'retry_delay': 1,
        'verify_ssl': True,
        'max_redirects': 5,
    },
    'cache': {
        'enabled': True,
        'ttl': 300,  # 5 dakika
        'max_size': '1GB',
    }
}

# Rapor ve Export Ayarları
ANALYTICS_REPORTING = {
    'formats': {
        'csv': {
            'enabled': True,
            'delimiter': ',',
            'encoding': 'utf-8-sig',
        },
        'excel': {
            'enabled': True,
            'engine': 'xlsxwriter',
            'options': {
                'strings_to_numbers': True,
                'strings_to_formulas': False,
            }
        },
        'pdf': {
            'enabled': True,
            'page_size': 'A4',
            'orientation': 'portrait',
            'template_path': 'reports/templates/',
        }
    },
    'scheduling': {
        'enabled': True,
        'max_scheduled': 10,
        'allowed_intervals': ['daily', 'weekly', 'monthly'],
    },
    'notifications': {
        'email': {
            'enabled': True,
            'template_path': 'notifications/email/',
        },
        'slack': {
            'enabled': True,
            'webhook_url': os.getenv('SLACK_WEBHOOK_URL'),
        }
    }
}

# Güvenlik ve İzleme Ayarları
ANALYTICS_SECURITY = {
    'audit_logging': {
        'enabled': True,
        'log_level': 'INFO',
        'exclude_paths': ['/health', '/metrics'],
    },
    'ip_whitelist': {
        'enabled': True,
        'allowed_ips': os.getenv('ALLOWED_IPS', '').split(','),
    },
    'api_key': {
        'expiry_days': 90,
        'key_length': 32,
        'rotation_enabled': True,
    }
}

# Performans İzleme
ANALYTICS_MONITORING = {
    'enabled': True,
    'metrics': {
        'query_duration': True,
        'cache_hits': True,
        'error_rates': True,
        'user_activity': True,
    },
    'alerting': {
        'enabled': True,
        'thresholds': {
            'query_duration_ms': 5000,
            'error_rate_percent': 5,
            'cache_hit_rate_percent': 80,
        }
    },
    'prometheus': {
        'enabled': True,
        'push_gateway': os.getenv('PROMETHEUS_PUSHGATEWAY'),
    }
}

# Middleware Yapılandırması
MIDDLEWARE = [
    # Güvenlik
    'django.middleware.security.SecurityMiddleware',
    'analytics.middleware.SecurityHeadersMiddleware',
    
    # Oturum ve Kimlik Doğrulama
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'analytics.middleware.JWTAuthMiddleware',
    'permissions.middleware.TwoFactorAuthMiddleware',
    
    # CORS ve API
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # İzinler ve Güvenlik
    'permissions.middleware.IPWhitelistMiddleware',
    'permissions.middleware.PermissionMiddleware',
    'permissions.middleware.RateLimitMiddleware',
    
    # İzleme ve Hata Yönetimi
    'analytics.middleware.RequestLoggingMiddleware',
    'analytics.middleware.PerformanceMonitoringMiddleware',
    'analytics.middleware.ErrorHandlingMiddleware',
    'permissions.middleware.AuditLogMiddleware',
    
    # Diğer
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

# Hata Ayıklama Ayarları
if ANALYTICS_SETTINGS['DEBUG']:
    MIDDLEWARE.extend([
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'analytics.middleware.QueryDebugMiddleware',
    ]) 