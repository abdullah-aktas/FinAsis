"""
FinAsis Temel Ayar Dosyası
--------------------------
Projenin tüm yapılandırma ayarlarını içerir.
Mantıksal bölümlere ayrılmış şekilde düzenlenmiştir.
"""

import environ
import os
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# === TEMEL AYARLAR ===
# Type-safe env değişkenleri
env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, 'your-secret-key'),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    CORS_ALLOWED_ORIGINS=(list, ['http://localhost:8000', 'http://127.0.0.1:8000', 'http://localhost:3000']),
    EMAIL_HOST=(str, 'smtp.gmail.com'),
    EMAIL_PORT=(int, 587),
    EMAIL_USE_TLS=(bool, True),
    EMAIL_HOST_USER=(str, ''),
    EMAIL_HOST_PASSWORD=(str, ''),
    AWS_ACCESS_KEY_ID=(str, ''),
    AWS_SECRET_ACCESS_KEY=(str, ''),
    AWS_STORAGE_BUCKET_NAME=(str, ''),
    AWS_S3_REGION_NAME=(str, 'eu-central-1')
)
environ.Env.read_env()

# Proje dizin yapısı
BASE_DIR = Path(__file__).resolve().parent

# === GÜVENLİK AYARLARI ===
SECRET_KEY = env.str('SECRET_KEY', default='your-secret-key')
DEBUG = env.bool('DEBUG', default='True')  # 'False' as string for env compatibility
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default='localhost,127.0.0.1')

# === UYGULAMA TANIMLARI ===
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
    'django_filters',
    'corsheaders',
    'drf_yasg',
]

LOCAL_APPS = [
    'core.apps.CoreConfig',
    'accounting.apps.AccountingConfig',
    'inventory.apps.InventoryConfig',
    'permissions.apps.PermissionsConfig',
    'hr_management.apps.HrManagementConfig',
    'finance.apps.FinanceConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# === MIDDLEWARE AYARLARI ===
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# === VERİTABANI AYARLARI ===
from decouple import config

# PostgreSQL ayarları güncellemesi
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='finasis'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='your-db-password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'client_encoding': 'UTF8'
        }
    }
}

# === CORS AYARLARI ===
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default='http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000')

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# === ŞABLON AYARLARI ===
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
                'django.template.context_processors.i18n',
            ],
        },
    },
]

# === STATİK DOSYA AYARLARI ===
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# === ULUSLARARASILAŞTIRMA AYARLARI ===
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('tr', 'Türkçe'),
    ('en', 'English'),
    ('ku', 'Kurdî'),
    ('ar', 'العربية'),
    ('de', 'Deutsch'),
    ('fr', 'Français'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

# === REST FRAMEWORK AYARLARI ===
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

# === GÜVENLİK AYARLARI ===
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# === CACHE AYARLARI ===
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# === EMAIL AYARLARI ===
# Tip güvenli email ayarları
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')  # type: str
EMAIL_PORT = env('EMAIL_PORT')  # type: int
EMAIL_USE_TLS = env('EMAIL_USE_TLS')  # type: bool
EMAIL_HOST_USER = env('EMAIL_HOST_USER')  # type: str
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')  # type: str

# === AWS S3 AYARLARI ===
# Tip güvenli AWS ayarları
AWS_ACCESS_KEY_ID: str = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY: str = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME: str = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME: str = env('AWS_S3_REGION_NAME')
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

