from __future__ import annotations

import logging
import os
from datetime import timedelta
from pathlib import Path
from typing import Any

from config import oidc as oidc_config

# -----------------------------------------------------------------------------
# Path & environment helpers
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

ENV = os.getenv


def env_list(name: str, fallback: str = '') -> list[str]:
    return [item.strip() for item in ENV(name, fallback).split(',') if item.strip()]


def env_bool(name: str, fallback: bool = False) -> bool:
    raw = ENV(name)
    if raw is None:
        return fallback
    return raw.lower() in {'1', 'true', 'yes', 'on'}



# -----------------------------------------------------------------------------
# Core settings
# -----------------------------------------------------------------------------
SECRET_KEY = ENV('DJANGO_SECRET_KEY', 'django-insecure-fin-as1s-placeholder-key')
DEBUG = env_bool('DJANGO_DEBUG', True)

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost,finasis.com.tr,www.finasis.com.tr')

CSRF_TRUSTED_ORIGINS = env_list(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    'https://finasis.com.tr,https://www.finasis.com.tr'
)

SITE_BASE_URL = ENV('DJANGO_SITE_BASE_URL', 'https://finasis.com.tr')
FINASIS_MEETING_BASE_URL = ENV('FINASIS_MEETING_BASE_URL', SITE_BASE_URL)
DEFAULT_VIDEO_PROVIDER = ENV('FINASIS_DEFAULT_VIDEO_PROVIDER', 'finasis')

INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party
    'django_prometheus',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_yasg',
    'channels',
    'django_otp',
    'django_otp.plugins.otp_totp',

    # Project applications
    'accounting.apps.AccountingConfig',
    'accounts.apps.AccountsConfig',
    'advisors.apps.AdvisorsConfig',
    'ai_assistant.apps.AIAssistantConfig',
    'audit.apps.AuditConfig',
    'billing.apps.BillingConfig',
    'blockchain.apps.BlockchainConfig',
    'common.apps.CommonConfig',
    'core_ui.apps.CoreUiConfig',
    'corporate.apps.CorporateConfig',
    'education.apps.EducationConfig',
    'education.teacher_dashboard.apps.TeacherDashboardConfig',
    'finance.apps.FinanceConfig',
    'finance.accounting.apps.AccountingConfig',
    'games.apps.GamesConfig',
    'games.game_app.apps.GameAppConfig',
    'games.ticaretin_izinde.apps.TicaretinIzindeConfig',
    'games.trade_sim',
    'games.finquest',
    'integrator_gib.apps.IntegratorGIBConfig',
    'integrator_mock.apps.IntegratorMockConfig',
    'kobi_analysis.apps.KobiAnalysisConfig',
    'locale.apps.LocaleConfig',
    'management.apps.ManagementConfig',
    'permissions.apps.PermissionsConfig',
    'developer_portal.apps.DeveloperPortalConfig',
    'partners.apps.PartnersConfig',
    'security.apps.SecurityConfig',
    'submissions.apps.SubmissionsConfig',
    'tenancy.apps.TenancyConfig',
    'virtual_company.apps.VirtualCompanyConfig',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'common.middleware.RequestContextLoggingMiddleware',
    'common.middleware_error_tracking.ErrorTrackingMiddleware',
    'developer_portal.middleware.APIUsageLoggingMiddleware',
    'common.middleware_rbac.RBACMiddleware',
    'security.middleware.SessionIdleTimeoutMiddleware',
    'security.middleware.ConcurrentSessionControlMiddleware',
    'security.middleware.OTPEnforcementMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'common.context_processors.rbac_context',
                'common.context_processors.user_roles',
                'common.context_processors.platform_context',
                'common.context_processors.brand_identity',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
DATABASES: dict[str, dict[str, Any]] = {
    'default': {
        'ENGINE': ENV('DJANGO_DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': ENV('DJANGO_DB_NAME', str(BASE_DIR / 'db.sqlite3')),
        'USER': ENV('DJANGO_DB_USER', ''),
        'PASSWORD': ENV('DJANGO_DB_PASSWORD', ''),
        'HOST': ENV('DJANGO_DB_HOST', ''),
        'PORT': ENV('DJANGO_DB_PORT', ''),
    }
}

if 'django_prometheus' in INSTALLED_APPS:
    _PROM_DB_ENGINES = {
        'django.db.backends.sqlite3': 'django_prometheus.db.backends.sqlite3',
        'django.db.backends.postgresql': 'django_prometheus.db.backends.postgresql',
        'django.db.backends.postgresql_psycopg2': 'django_prometheus.db.backends.postgresql',
        'django.db.backends.mysql': 'django_prometheus.db.backends.mysql',
    }
    default_engine = DATABASES['default'].get('ENGINE')
    DATABASES['default']['ENGINE'] = _PROM_DB_ENGINES.get(default_engine, default_engine)

# -----------------------------------------------------------------------------
# Authentication & authorization
# -----------------------------------------------------------------------------
AUTH_USER_MODEL = 'accounts.CustomUser'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

SESSION_COOKIE_AGE = int(ENV('SESSION_COOKIE_AGE', 60 * 60 * 12))  # 12 saat
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', not DEBUG)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
SESSION_IDLE_TIMEOUT = int(ENV('SESSION_IDLE_TIMEOUT', 60 * 30))  # 30 dakika
SESSION_CONCURRENT_LIMIT = int(ENV('SESSION_CONCURRENT_LIMIT', 3))
OTP_LOGIN_URL = 'accounts:otp_verify'

LOGIN_REDIRECT_URL = 'accounts:user_profile'
LOGOUT_REDIRECT_URL = 'accounts:login'
LOGIN_URL = 'accounts:login'

if oidc_config.OIDC_ENABLED and oidc_config.KEYCLOAK_CLIENT_SECRET:
    INSTALLED_APPS.append('mozilla_django_oidc')
    AUTHENTICATION_BACKENDS.insert(0, 'mozilla_django_oidc.auth.OIDCAuthenticationBackend')
    LOGIN_URL = 'oidc_authentication_init'
    LOGIN_REDIRECT_URL = oidc_config.LOGIN_REDIRECT_URL
    LOGOUT_REDIRECT_URL = oidc_config.LOGOUT_REDIRECT_URL
    OIDC_RP_CLIENT_ID = oidc_config.KEYCLOAK_CLIENT_ID
    OIDC_RP_CLIENT_SECRET = oidc_config.KEYCLOAK_CLIENT_SECRET
    OIDC_OP_AUTHORIZATION_ENDPOINT = f"{oidc_config.KEYCLOAK_AUTHORITY}/protocol/openid-connect/auth"
    OIDC_OP_TOKEN_ENDPOINT = f"{oidc_config.KEYCLOAK_AUTHORITY}/protocol/openid-connect/token"
    OIDC_OP_USER_ENDPOINT = f"{oidc_config.KEYCLOAK_AUTHORITY}/protocol/openid-connect/userinfo"
    OIDC_OP_JWKS_ENDPOINT = f"{oidc_config.KEYCLOAK_AUTHORITY}/protocol/openid-connect/certs"
    OIDC_RP_SCOPES = 'openid email profile'
    OIDC_STORE_ID_TOKEN = True
    OIDC_USE_NONCE = True
    OIDC_EXEMPT_URLS = [
        r'^accounts/otp/',
    ]

# -----------------------------------------------------------------------------
# Internationalisation
# -----------------------------------------------------------------------------
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('tr', 'Türkçe'),
    ('en', 'English'),
    ('de', 'Deutsch'),
    ('es', 'Español'),
    ('ar', 'العربية'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

SUPPORTED_REGIONS = env_list('FINASIS_SUPPORTED_REGIONS', 'TR,EU,US')
DEFAULT_REGION = ENV('FINASIS_DEFAULT_REGION', SUPPORTED_REGIONS[0] if SUPPORTED_REGIONS else 'TR')
REGIONAL_PRICING: dict[str, dict[str, Any]] = {
    'TR': {
        'currency': 'TRY',
        'vat_rate': 0.18,
        'price_multiplier': 1.0,
    },
    'EU': {
        'currency': 'EUR',
        'vat_rate': 0.20,
        'price_multiplier': 0.050,
    },
    'US': {
        'currency': 'USD',
        'sales_tax': 'state_based',
        'price_multiplier': 0.055,
    },
    'APAC': {
        'currency': 'SGD',
        'gst_rate': 0.08,
        'price_multiplier': 0.045,
    },
}
BASE_PRICING_CURRENCY = 'TRY'
REGION_LABELS = {
    'TR': 'Türkiye',
    'EU': 'Avrupa Birliği',
    'US': 'ABD',
    'APAC': 'APAC',
}

# -----------------------------------------------------------------------------
# Static & media
# -----------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

if (BASE_DIR / 'static').exists():
    STATICFILES_DIRS = [BASE_DIR / 'static']
else:
    STATICFILES_DIRS: list[Path] = []

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -----------------------------------------------------------------------------
# Django REST Framework
# -----------------------------------------------------------------------------
REST_FRAMEWORK: dict[str, Any] = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'developer_portal.authentication.APIKeyAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_THROTTLE_CLASSES': [
        'developer_portal.throttling.DeveloperAPIKeyRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'developer_freemium': '120/day',
        'developer_standard': '1000/hour',
        'developer_professional': '5000/hour',
        'developer_enterprise': '20000/hour',
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(ENV('JWT_ACCESS_MINUTES', '30'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(ENV('JWT_REFRESH_DAYS', '7'))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# -----------------------------------------------------------------------------
# Channels (WebSocket) configuration
# -----------------------------------------------------------------------------
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# -----------------------------------------------------------------------------
# Cache
# -----------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'finasis-cache',
    },
}

if 'django_prometheus' in INSTALLED_APPS:
    cache_backend = CACHES['default'].get('BACKEND')
    if cache_backend == 'django.core.cache.backends.locmem.LocMemCache':
        CACHES['default']['BACKEND'] = 'django_prometheus.cache.backends.locmem.LocMemCache'

# -----------------------------------------------------------------------------
# Email & notifications
# -----------------------------------------------------------------------------
EMAIL_BACKEND = ENV('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = ENV('DJANGO_DEFAULT_FROM_EMAIL', 'FinAsis <noreply@finasis.local>')

# -----------------------------------------------------------------------------
# Observability
# -----------------------------------------------------------------------------
ENABLE_STRUCTURED_LOGS = env_bool('DJANGO_ENABLE_JSON_LOGS', not DEBUG)

SENTRY_DSN = ENV('SENTRY_DSN', '')
SENTRY_ENVIRONMENT = ENV('SENTRY_ENVIRONMENT', 'development' if DEBUG else 'production')
SENTRY_TRACES_SAMPLE_RATE = float(ENV('SENTRY_TRACES_SAMPLE_RATE', '0.0'))
SENTRY_PROFILES_SAMPLE_RATE = float(ENV('SENTRY_PROFILES_SAMPLE_RATE', '0.0'))

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    def _scrub_event(event: dict[str, Any], hint: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            from common.presenters import maskers
        except Exception:
            return event

        def _sanitize(value):
            if isinstance(value, str):
                return maskers.mask_text(value)
            if isinstance(value, dict):
                return {key: _sanitize(val) for key, val in value.items()}
            if isinstance(value, list):
                return [_sanitize(item) for item in value]
            return value

        return _sanitize(event)

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENVIRONMENT,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE,
        send_default_pii=False,
        before_send=_scrub_event,
    )

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOGGING: dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'mask_pii': {
            '()': 'common.logging.PIIMaskFilter',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} | {message}',
            'style': '{',
        },
        'json': {
            '()': 'common.logging.JsonFormatter',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['mask_pii'],
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'finasis': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
    },
}

if ENABLE_STRUCTURED_LOGS:
    LOGGING['handlers']['structured'] = {
        'class': 'logging.StreamHandler',
        'formatter': 'json',
        'filters': ['mask_pii'],
    }
    _root_handlers = ['structured', 'console']
else:
    _root_handlers = ['console']

LOGGING['root']['handlers'] = _root_handlers
LOGGING['loggers']['django']['handlers'] = _root_handlers
LOGGING['loggers']['finasis']['handlers'] = _root_handlers

# -----------------------------------------------------------------------------
# Misc
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATA_UPLOAD_MAX_MEMORY_SIZE = int(ENV('DJANGO_DATA_UPLOAD_MAX_MEMORY_SIZE', str(10 * 1024 * 1024)))

# --------------------------------------------------------------------------
# Data governance
# --------------------------------------------------------------------------
DATA_ENCRYPTION_KEY = ENV('DATA_ENCRYPTION_KEY', '')
DATA_ENCRYPTION_FALLBACK_KEY = ENV('DATA_ENCRYPTION_FALLBACK_KEY', '')

