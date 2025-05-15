"""
FinAsis Temel Ayar Dosyası
--------------------------
Projenin tüm yapılandırma ayarlarını içerir.
Mantıksal bölümlere ayrılmış şekilde düzenlenmiştir.
"""

import os
from pathlib import Path
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
import environ
from django.contrib.auth.signals import user_logged_in
import logging

# .env dosyasını oku
env = environ.Env(
    DEBUG=(bool, True),
)
environ.Env.read_env(os.path.join(Path(__file__).resolve().parent.parent, '.env'))

# Temel dizin
BASE_DIR = Path(__file__).resolve().parent.parent

# Güvenlik
SECRET_KEY = env("SECRET_KEY") or "degistir_bunu_gizli_bir_degerle"
DEBUG = True  # Hata ayıklama için doğrudan True
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS") or ["127.0.0.1", "localhost", "finasis.com.tr", "www.finasis.com.tr"]

# Uygulamalar
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_filters',
]

LOCAL_APPS = [
    'core.apps.CoreConfig',
    'users.apps.UsersConfig',
    'finance.apps.FinanceConfig',
    'virtual_company.apps.VirtualCompanyConfig',
    'apps.edocument',
    'apps.customers.apps.CustomersConfig',
    'integrations.bank_integration',
    'integrations.efatura',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

if DEBUG:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'FinAsis.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# Veritabanı (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Uluslararasılaştırma
LANGUAGE_CODE = env("LANGUAGE_CODE") or "tr"
TIME_ZONE = env("TIME_ZONE") or "Europe/Istanbul"
try:
    USE_I18N = env.bool("USE_I18N")
except Exception:
    USE_I18N = True
try:
    USE_L10N = env.bool("USE_L10N")
except Exception:
    USE_L10N = True
try:
    USE_TZ = env.bool("USE_TZ")
except Exception:
    USE_TZ = True

LANGUAGES = [
    ('tr', 'Türkçe'),
    ('en', 'English'),
    ('ku', 'Kurdî'),
    ('ar', 'العربية'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

# Statik ve Medya
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Güvenlik
try:
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT")
except Exception:
    SECURE_SSL_REDIRECT = False
try:
    SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE")
except Exception:
    SESSION_COOKIE_SECURE = True
try:
    CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE")
except Exception:
    CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CSRF güvenilen domainler
CSRF_TRUSTED_ORIGINS = [
    "https://www.finasis.com.tr",
    "https://finasis.com.tr",
]

# REST Framework
try:
    PAGE_SIZE = env.int("API_PAGE_SIZE")
except Exception:
    PAGE_SIZE = 10
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': PAGE_SIZE,
}

# Email
EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

# AWS S3 (isteğe bağlı)
try:
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
except Exception:
    AWS_STORAGE_BUCKET_NAME = None
if AWS_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
    try:
        AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
    except Exception:
        AWS_S3_REGION_NAME = ""
    try:
        AWS_S3_FILE_OVERWRITE = env.bool("AWS_S3_FILE_OVERWRITE")
    except Exception:
        AWS_S3_FILE_OVERWRITE = False
    try:
        AWS_DEFAULT_ACL = env("AWS_DEFAULT_ACL")
    except Exception:
        AWS_DEFAULT_ACL = ""
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

# Debug Toolbar
INTERNAL_IPS = ['127.0.0.1'] if DEBUG else []

# Logging
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

# Varsayılan otomatik alan tipi
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# JWT Ayarları

logger = logging.getLogger("user_login")

def log_user_login(sender, request, user, **kwargs):
    logger.info(f"Kullanıcı girişi: {user.username} - IP: {request.META.get('REMOTE_ADDR')}")

user_logged_in.connect(log_user_login)