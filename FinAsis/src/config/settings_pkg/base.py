"""
Base Django settings for FinAsis.
Split from monolithic settings; behavior kept identical.
"""
from pathlib import Path
import os
import sys
import importlib
from typing import Any
import json as _json
try:
    import environ  # type: ignore
except ModuleNotFoundError:  # Lightweight fallback for test/import-time
    class _FallbackEnv:
        def __call__(self, key: str, default: Any | None = None, cast: Any | None = None) -> Any | None:
            val = os.environ.get(key, None)
            if val is None:
                return default
            if cast:
                try:
                    return cast(val)
                except Exception:
                    return default
            return val

        @staticmethod
        def read_env(path: str, override: bool = False) -> None:  # no-op
            return None

    class _EnvironModule:
        Env = _FallbackEnv

    environ = _EnvironModule()  # type: ignore

# Initialize django-environ and read possible .env files from repo/inner roots
env = environ.Env()
_HERE = os.path.dirname(os.path.abspath(__file__))
# base.py at: .../FinAsis/src/config/settings_pkg/base.py
_SRC_DIR = os.path.abspath(os.path.join(_HERE, '..', '..'))
_INNER_ROOT = os.path.abspath(os.path.join(_SRC_DIR, '..'))        # .../FinAsis
_REPO_ROOT = os.path.abspath(os.path.join(_INNER_ROOT, '..'))      # repo root
for _candidate in (os.path.join(_REPO_ROOT, '.env'), os.path.join(_INNER_ROOT, '.env')):
    if os.path.exists(_candidate):
        environ.Env.read_env(_candidate, override=False)

# Backwards-compatible helper to mirror decouple.config API using django-environ
def config(key: str, default: Any | None = None, cast: Any | None = None) -> Any | None:
    """Backwards-compatible env getter.

    - Avoid passing a possibly-None `default` to `environ.Env.__call__` to satisfy typing
      (its stub expects a sentinel type, not None).
    - If the variable is missing and `default` is None, emulate decouple behavior by
      catching and returning None.
    """
    try:
        # Build kwargs conditionally to keep Pyright happy with `default` param type.
        kwargs: dict[str, Any] = {}
        if cast is not None:
            kwargs["cast"] = cast
        if default is not None:
            kwargs["default"] = default
        if not kwargs:
            return env(key)
        return env(key, **kwargs)
    except Exception:
        return default

# Build paths: we want BASE_DIR to be the 'src' directory (as in original).
# This file lives at src/config/settings_pkg/base.py, go up 3 levels -> src
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure that the project root (parent of the 'src' package)
# is available on sys.path so imports like 'src.apps.*' work in all contexts
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- TEST IMPORT UYUMLULUK ALIASLARI ---
try:  # Koruyucu blok: production'da gereksiz olabilir
    src_pkg = importlib.import_module('src')
    sys.modules.setdefault('FinAsis', src_pkg)
    # 'FinAsis.src' aliası
    sys.modules.setdefault('FinAsis.src', src_pkg)
    # apps altındaki doğrudan paketler için dinamik alias (sadece ilk seferde)
    apps_path = os.path.join(PROJECT_ROOT, 'src', 'apps')
    if os.path.isdir(apps_path):
        for entry in os.listdir(apps_path):
            full = os.path.join(apps_path, entry)
            if os.path.isdir(full) and os.path.isfile(os.path.join(full, '__init__.py')):
                alias_name = f'FinAsis.src.apps.{entry}'
                real_name = f'src.apps.{entry}'
                if real_name in sys.modules and alias_name not in sys.modules:
                    sys.modules[alias_name] = sys.modules[real_name]
except Exception:  # Sessiz geç
    pass


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='test-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# In production, override via environment. Leaving default here keeps tests/tools working.

_ALLOWED_HOSTS_ENV = str(config('ALLOWED_HOSTS', default=''))
if _ALLOWED_HOSTS_ENV.strip():
    ALLOWED_HOSTS = [h.strip() for h in _ALLOWED_HOSTS_ENV.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "167.71.46.215", "finasis.com.tr", "www.finasis.com.tr"]

_LOCAL_HOSTS = {"localhost", "127.0.0.1"}
if DEBUG:
    for h in ALLOWED_HOSTS:
        domain = h.split(':')[0]
        if domain not in _LOCAL_HOSTS:
            import logging
            logging.getLogger(__name__).warning(
                "DEBUG mode is ON while host '%s' is allowed. Disable DEBUG in production!", h
            )
            break


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django.contrib.humanize',
    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap5',
    'channels',
    'django_filters',
    # Core reusable corporate UI (base templates, components)
    'src.apps.core_ui',
    'src.apps.common.apps.CommonConfig',
    'src.apps.accounts',
    'src.apps.accounting',
    'src.apps.games',
    'src.apps.games.trade_sim',
    'src.apps.games.game_app',
    'src.apps.finance',
    'src.apps.finance.banking.apps.BankingConfig',
    'src.apps.finance.accounting.apps.AccountingConfig',
    'src.apps.blockchain',
    'src.apps.education',
    'src.apps.education.student',
    'src.apps.education.teacher_dashboard',
    'src.apps.management',
    'src.apps.tenancy.apps.TenancyConfig',
    'src.apps.audit.apps.AuditConfig',
    'src.apps.virtual_company.apps.VirtualCompanyConfig',
    'src.apps.ai_assistant.apps.AIAssistantConfig',
    'src.apps.corporate.apps.CorporateConfig',
    'src.apps.billing.apps.BillingConfig',
    'src.apps.kobi_analysis.apps.KobiAnalysisConfig',
    'src.apps.security.apps.SecurityConfig',
    # New regulatory compliance apps
    'src.apps.advisors.apps.AdvisorsConfig',
    'src.apps.submissions.apps.SubmissionsConfig',
    'src.apps.integrator_gib.apps.IntegratorGIBConfig',
    # HTTP adapter smoke test mock
    'src.apps.integrator_mock.apps.IntegratorMockConfig',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Tenant & audit middlewares (order: tenant first so others can rely on request.tenant)
    'src.apps.tenancy.middleware.CurrentTenantMiddleware',
    'src.apps.audit.middleware.AuditRequestMetaMiddleware',
    'src.apps.common.middleware.RequestContextLoggingMiddleware',
    'src.apps.games.trade_sim.middleware.AutoOnboardingMiddleware',
]

ROOT_URLCONF = 'src.config.urls'

_TEMPLATE_DIR = os.path.join(os.path.dirname(BASE_DIR), 'templates')
_SRC_TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
_IN_PYTEST = bool(os.environ.get('PYTEST_CURRENT_TEST'))
_BASE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [_TEMPLATE_DIR, _SRC_TEMPLATES_DIR],
    # Explicit loaders so we can drop cached loader in tests (stale template issue prevention)
    'OPTIONS': {
        'loaders': _BASE_LOADERS if _IN_PYTEST else [
            ('django.template.loaders.cached.Loader', _BASE_LOADERS)
        ],
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'src.apps.billing.context_processors.billing_settings',
            'src.apps.core_ui.context_processors.marketing_features',
            'src.apps.core_ui.context_processors.project_meta',
            'src.apps.common.context_processors.user_roles',
            'src.apps.common.context_processors.platform_context',
        ],
        'builtins': [
            'src.apps.education.student.templatetags.student_filters',
        ],
    },
}]

WSGI_APPLICATION = 'src.config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

"""
Database Configuration Strategy
Priority order (first True flag wins):
1. USE_POSTGRES=True  -> Use Postgres settings (recommended for staging/prod)
2. USE_SQLITE=True    -> Fallback lightweight dev DB (default True if nothing specified)
Environment Variables (example):
  USE_POSTGRES=1 POSTGRES_DB=finasis POSTGRES_USER=finasis POSTGRES_PASSWORD=secret POSTGRES_HOST=postgres POSTGRES_PORT=5432
Security: Hard‑coded credentials removed; all sensitive values must come from env/secret store.
"""

USE_POSTGRES = config('USE_POSTGRES', default=False, cast=bool)
USE_SQLITE = config('USE_SQLITE', default=not USE_POSTGRES, cast=bool)

if USE_POSTGRES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('POSTGRES_DB', default='finasis'),
            'USER': config('POSTGRES_USER', default='postgres'),
            'PASSWORD': config('POSTGRES_PASSWORD', default=''),
            'HOST': config('POSTGRES_HOST', default='localhost'),
            'PORT': config('POSTGRES_PORT', default='5432'),
            'CONN_MAX_AGE': config('POSTGRES_CONN_MAX_AGE', default=60, cast=int),
        }
    }
elif USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:  # Safety fallback
    raise RuntimeError("No database configured. Set USE_POSTGRES=1 or USE_SQLITE=1")

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 10}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'accounts.CustomUser'


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'tr-tr'

TIME_ZONE = 'Europe/Istanbul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    # Dış statik dizin (FinAsis/FinAsis/FinAsis/static mevcutsa)
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
ASGI_APPLICATION = 'src.config.asgi.application'

# Channels katmanı (varsayılan hafıza; production'da Redis önerilir)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

SESSION_COOKIE_AGE = 60 * 30  # 30 dakika
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache'),
    }
}

# GİB (e-Fatura / e-Defter) ayarları
GIB_USERNAME = config('GIB_USERNAME', default='testuser')
GIB_PASSWORD = config('GIB_PASSWORD', default='testpass')
GIB_TEST_MODE = config('GIB_TEST_MODE', default=True, cast=bool)
GIB_EFATURA_BASE_URL = config('GIB_EFATURA_BASE_URL', default='https://efatura-test.efatura.gov.tr/api')
GIB_EDEFTER_BASE_URL = config('GIB_EDEFTER_BASE_URL', default='https://edefter-test.edefter.gov.tr/api')

# EDOC/GİB istemcisi ayarları (stub/http modu)
EDOC_GIB_MODE = config('EDOC_GIB_MODE', default='stub')  # 'stub' | 'http'
EDOC_GIB_BASE_URL = config('EDOC_GIB_BASE_URL', default='')  # http modunda zorunlu
EDOC_PROFILE_ID = config('EDOC_PROFILE_ID', default='TICARIFATURA')
EDOC_CUSTOMIZATION_ID = config('EDOC_CUSTOMIZATION_ID', default='TR1.2')
EDOC_SCHEMAS_DIR = config('EDOC_SCHEMAS_DIR', default='')
EDOC_RETRY_MAX = config('EDOC_RETRY_MAX', default=3, cast=int)
EDOC_RETRY_BACKOFF = config('EDOC_RETRY_BACKOFF', default=0.7)
EDOC_RETRY_MAX_BACKOFF = config('EDOC_RETRY_MAX_BACKOFF', default=8.0)

# OCR/AI yerel ayarları
USE_GOOGLE_VISION = config('USE_GOOGLE_VISION', default=False, cast=bool)
STT_ENABLED = config('STT_ENABLED', default=False, cast=bool)
VOSK_MODEL_PATH = config('VOSK_MODEL_PATH', default='')
AI_LOCAL_ONLY = config('AI_LOCAL_ONLY', default=True, cast=bool)
AI_PRIVACY_MODE = config('AI_PRIVACY_MODE', default=True, cast=bool)

# Django Crispy Forms & Bootstrap5 ayarları
CRISPY_ALLOWED_TEMPLATE_PACKS = ["bootstrap5"]
CRISPY_TEMPLATE_PACK = "bootstrap5"

# REST Framework temel filtre backend tanımı (django_filters entegre)
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

# Meetings/WebRTC settings
# video mode: 'mesh' (P2P) or 'sfu'
MEETINGS_VIDEO_MODE = config('MEETINGS_VIDEO_MODE', default='mesh')
# When using SFU via Jitsi (self-host), set domain like 'meet.yourdomain.com'
MEETINGS_JITSI_DOMAIN = config('MEETINGS_JITSI_DOMAIN', default='')
# ICE servers for P2P mesh mode (JSON string). Example:
#   [ {"urls": "stun:stun.l.google.com:19302"}, {"urls": "turn:turn.domain:3478", "username": "u", "credential": "p"} ]
try:
    _ice_json = str(config('MEETINGS_ICE_SERVERS', default='[]'))
    MEETINGS_ICE_SERVERS = _json.loads(_ice_json) if _ice_json else []
except Exception:
    MEETINGS_ICE_SERVERS = []

# Optional Jitsi JWT auth (Secure Domain)
JITSI_JWT_ENABLED = config('JITSI_JWT_ENABLED', default=False, cast=bool)
JITSI_JWT_APP_ID = config('JITSI_JWT_APP_ID', default='')
JITSI_JWT_SECRET = config('JITSI_JWT_SECRET', default='')
JITSI_JWT_ISS = config('JITSI_JWT_ISS', default='finasis')
JITSI_JWT_AUD = config('JITSI_JWT_AUD', default='jitsi')
JITSI_JWT_TTL = config('JITSI_JWT_TTL', default=60 * 60, cast=int)

# If Redis details are provided and channels_redis is installed, switch channel layer to Redis
_REDIS_URL = config('REDIS_URL', default='')
_REDIS_HOST = config('CHANNEL_REDIS_HOST', default='')
if _REDIS_URL or _REDIS_HOST:
    try:
        import channels_redis  # type: ignore  # noqa: F401
        _hosts = []
        if _REDIS_URL:
            _hosts = [_REDIS_URL]
        elif _REDIS_HOST:
            _port_val = config('CHANNEL_REDIS_PORT', default='6379')
            try:
                _port = int(_port_val) if _port_val is not None else 6379
            except Exception:
                _port = 6379
            _hosts = [(str(_REDIS_HOST), _port)]
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {'hosts': _hosts},
            }
        }
    except Exception:
        # Fallback to in-memory if channels_redis not available
        pass

# Email settings
# Use console backend in development; allow override via env
if DEBUG:
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
else:
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='no-reply@finasis.local')
SUPPORT_EMAIL = config('SUPPORT_EMAIL', default='support@finasis.local')
SALES_EMAIL = config('SALES_EMAIL', default='sales@finasis.local')

# Billing / PayTR settings
PAYTR_MERCHANT_ID = config('PAYTR_MERCHANT_ID', default='')
PAYTR_MERCHANT_KEY = config('PAYTR_MERCHANT_KEY', default='')
PAYTR_MERCHANT_SALT = config('PAYTR_MERCHANT_SALT', default='')

# Billing UI defaults (configurable ordering and featured modules)
# Override in environment-specific settings if needed.
BILLING_PLAN_ORDER = {
    # SME: Starter → Pro → Enterprise
    'sme': ['starter', 'sme_pro', 'sme_enterprise'],
    # EDU: Student → Teacher → Campus
    'edu': ['edu_student', 'edu_teacher', 'edu_campus'],
}

BILLING_FEATURED_MODULES = {
    'sme': ['e-Fatura', 'Nakit Akışı', 'Banka Entegrasyonları', 'AI Destekli Analiz'],
    'edu': ['Eğitim/LMS', 'Analitik & Gelişmiş Raporlama', 'AI Destekli Analiz'],
}

# --- Logging (JSON structured) ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'src.apps.common.logging.JsonFormatter',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'finasis.log'),
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# DRF throttling scaffolding (rate limit hazırlığı)
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    'DEFAULT_THROTTLE_CLASSES': [
        'src.apps.common.throttling.BurstUserThrottle',
        'src.apps.common.throttling.SustainedUserThrottle',
        'src.apps.common.throttling.BurstAnonThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'burst': config('THROTTLE_BURST_USER', default='20/minute'),
        'sustained': config('THROTTLE_SUSTAINED_USER', default='1000/hour'),
        'burst_anon': config('THROTTLE_BURST_ANON', default='10/minute'),
    }
}
PAYTR_SANDBOX = config('PAYTR_SANDBOX', default=True, cast=bool)
_PAYTR_ALLOWED_IPS_RAW = config('PAYTR_ALLOWED_IPS', default='')
try:
    PAYTR_ALLOWED_IPS = [ip.strip() for ip in str(_PAYTR_ALLOWED_IPS_RAW).split(',') if ip.strip()]
except Exception:
    PAYTR_ALLOWED_IPS = []

# Bank transfer info
BANK_TRANSFER_ENABLED = config('BANK_TRANSFER_ENABLED', default=True, cast=bool)
BANK_ACCOUNT_HOLDER = config('BANK_ACCOUNT_HOLDER', default='FinAsis Teknoloji A.Ş.')
BANK_ACCOUNT_IBAN = config('BANK_ACCOUNT_IBAN', default='TR00 0000 0000 0000 0000 0000 00')
BANK_ACCOUNT_BANK = config('BANK_ACCOUNT_BANK', default='Finasis Bankası')

# --- Project Meta ---
APP_VERSION = config('APP_VERSION', default='v1.0')
BRAND_NAME = config('BRAND_NAME', default='FinAsis')

# --- Warnings cleanup / compatibility ---
# drf_yasg renderer format deprecation: use new renderers
SWAGGER_USE_COMPAT_RENDERERS = False
# Django 6.0 URLField default scheme change: opt into https to silence warning
FORMS_URLFIELD_ASSUME_HTTPS = True

# --- Regulatory feature flags ---
# By default, disable direct taxpayer submissions; require advisor mediation.
SUBMISSIONS_ALLOW_DIRECT = bool(config('SUBMISSIONS_ALLOW_DIRECT', default=False, cast=bool))

# --- Auth redirects ---
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/panel/'  # Kullanıcı giriş sonrası kişisel paneline yönlendirilir
LOGOUT_REDIRECT_URL = '/'
