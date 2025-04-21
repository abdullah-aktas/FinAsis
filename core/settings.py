import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'debug_toolbar',
    'django_celery_beat',
    'django_celery_results',
    'django_filters',
    'drf_yasg',
    'channels',
    'django_redis',
    'pwa',
    
    # Local apps
    'accounts.apps.AccountsConfig',
    'users.apps.UsersConfig',
    'customer_management.apps.CustomerManagementConfig',
    'company_management.apps.CompanyManagementConfig',
    'ext_services.apps.ExtServicesConfig',
    'seo_management.apps.SeoManagementConfig',
    'virtual_company.apps.VirtualCompanyConfig',
    'ai_assistant.apps.AiAssistantConfig',
    'blockchain.apps.BlockchainConfig',
    'accounting.apps.AccountingConfig',
    'crm',
    'reporting',
    'games.apps.GamesConfig',
    'apps.social',  # Sosyal medya uygulaması
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Dil arayüzü için
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['D:\\TeknoFest Proje\\FinAsis\\templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', ''),
        'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', 600)),
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',
        },
    }
}

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
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

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'tr-tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_L10N = True  # Yerel tarih, saat ve sayı biçimlendirmesi
USE_TZ = True

# Çoklu dil desteği
from django.utils.translation import gettext_lazy as _
LANGUAGES = [
    ('tr', _('Türkçe')),
    ('en', _('İngilizce')),
    ('ar', _('Arapça')),
    ('ku', _('Kürtçe')),
    ('de', _('Almanca')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Dil algılama ayarları
LANGUAGE_COOKIE_NAME = 'finasis_language'
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365  # 1 yıl
LANGUAGE_COOKIE_DOMAIN = None
LANGUAGE_COOKIE_PATH = '/'
LANGUAGE_COOKIE_SECURE = not DEBUG
LANGUAGE_COOKIE_HTTPONLY = True
LANGUAGE_COOKIE_SAMESITE = 'Lax'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auth settings
AUTH_USER_MODEL = 'accounts.User'

# Django AllAuth settings
SITE_ID = 1
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']

# Crispy Forms settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Debug Toolbar settings
INTERNAL_IPS = [
    '127.0.0.1',
]

# CORS settings
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# OpenAI settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Blockchain settings
BLOCKCHAIN_NETWORK = os.getenv('BLOCKCHAIN_NETWORK', 'testnet')
BLOCKCHAIN_API_KEY = os.getenv('BLOCKCHAIN_API_KEY')

# Authentication settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# LangChain settings
LANGCHAIN_WARNINGS = 'ignore'

# E-Belge Ayarları
EDOCUMENT_API_KEY = os.getenv('EDOCUMENT_API_KEY')
EDOCUMENT_API_URL = os.getenv('EDOCUMENT_API_URL', 'https://api.example.com/edocument')
EDOCUMENT_SERVICE_TYPE = os.getenv('EDOCUMENT_SERVICE_TYPE', 'earchive')

# Şirket Bilgileri
COMPANY_VKN = os.getenv('COMPANY_VKN')
COMPANY_NAME = os.getenv('COMPANY_NAME')
COMPANY_WEBSITE = os.getenv('COMPANY_WEBSITE')
COMPANY_ADDRESS = os.getenv('COMPANY_ADDRESS')
COMPANY_DISTRICT = os.getenv('COMPANY_DISTRICT')
COMPANY_CITY = os.getenv('COMPANY_CITY')
COMPANY_POSTAL_CODE = os.getenv('COMPANY_POSTAL_CODE')
COMPANY_COUNTRY = os.getenv('COMPANY_COUNTRY', 'Türkiye')
COMPANY_TAX_OFFICE = os.getenv('COMPANY_TAX_OFFICE')
COMPANY_PHONE = os.getenv('COMPANY_PHONE')
COMPANY_EMAIL = os.getenv('COMPANY_EMAIL')

# E-Belge Dosya Ayarları
EDOCUMENT_STORAGE_PATH = os.path.join(BASE_DIR, 'media', 'edocuments')
EDOCUMENT_PDF_PATH = os.path.join(EDOCUMENT_STORAGE_PATH, 'pdf')
EDOCUMENT_XML_PATH = os.path.join(EDOCUMENT_STORAGE_PATH, 'xml')

# E-Belge Arşivleme Ayarları
EDOCUMENT_RETENTION_PERIOD = int(os.getenv('EDOCUMENT_RETENTION_PERIOD', '10'))  # Yıl
EDOCUMENT_BACKUP_ENABLED = os.getenv('EDOCUMENT_BACKUP_ENABLED', 'True').lower() == 'true'
EDOCUMENT_BACKUP_PATH = os.path.join(BASE_DIR, 'backups', 'edocuments')

# E-Belge Önbellek Ayarları
EDOCUMENT_CACHE_ENABLED = os.getenv('EDOCUMENT_CACHE_ENABLED', 'True').lower() == 'true'
EDOCUMENT_CACHE_TIMEOUT = int(os.getenv('EDOCUMENT_CACHE_TIMEOUT', '3600'))  # Saniye

# E-Belge Log Ayarları
EDOCUMENT_LOG_LEVEL = os.getenv('EDOCUMENT_LOG_LEVEL', 'INFO')
EDOCUMENT_LOG_FILE = os.path.join(BASE_DIR, 'logs', 'edocument.log')

# Güvenlik ayarları
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 yıl
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Şifreleme algoritması güçlendirme
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Rate limiting ve güvenlik
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_VIEW = True
RATELIMIT_KEY_FUNCTION = 'django_ratelimit.utils.get_client_ip'

# SEO ayarları
SEO_TITLE = "FinAsis - Finansal Asistan ve Entegrasyon Platformu"
SEO_DESCRIPTION = "FinAsis, işletmenizi finansal olarak yönetmeyi kolaylaştıran entegre bir çözümdür. Muhasebe, fatura, stok, CRM ve daha fazlası."
SEO_KEYWORDS = "finans, muhasebe, crm, işletme yönetimi, fatura, e-fatura, stok yönetimi, finansal analiz"
SEO_AUTHOR = "FinAsis"
SEO_IMAGE = "img/og-image.png"
SEO_SITE_NAME = "FinAsis"
SEO_TWITTER_CREATOR = "@finasis"
SEO_TWITTER_SITE = "@finasis"
SEO_ROBOTS = "index, follow"
SEO_CANONICAL_URL = os.getenv('DJANGO_CANONICAL_URL', 'https://finasis.com.tr')

# PWA Ayarları
PWA_APP_NAME = 'FinAsis'
PWA_APP_DESCRIPTION = 'Finansal Asistan ve Entegrasyon Platformu'
PWA_APP_THEME_COLOR = '#0097a7'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'any'
PWA_APP_START_URL = '/'
PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_ICONS = [
    {
        'src': '/static/images/icons/icon-192x192.png',
        'sizes': '192x192',
        'type': 'image/png'
    },
    {
        'src': '/static/images/icons/icon-512x512.png',
        'sizes': '512x512',
        'type': 'image/png'
    }
]
PWA_APP_SPLASH_SCREEN = [
    {
        'src': '/static/images/icons/splash-640x1136.png',
        'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'
    }
]
PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'tr-TR'
PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'static', 'pwa', 'serviceworker.js') 