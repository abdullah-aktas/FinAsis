"""
Django temel ayarları
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# Log ayarlarını dahil et
from config.settings.logging import LOGGING

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-development-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

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
    'corsheaders',
    'debug_toolbar',
    
    # Local apps
    'accounts.apps.AccountsConfig',
    'virtual_company.apps.VirtualCompanyConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'config.wsgi.application'

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
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Rest framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'finasis'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Bağlantı havuzu süresi (saniye)
        'OPTIONS': {
            'connect_timeout': 10,
            'client_encoding': 'UTF8',
            'timezone': 'UTC',
            'sslmode': 'prefer',
        },
        'ATOMIC_REQUESTS': True,  # Her istek için otomatik transaction
        'CONN_HEALTH_CHECKS': True,  # Bağlantı sağlık kontrolleri
    }
}

# PostgreSQL özel ayarları
POSTGRES_OPTIMIZATIONS = {
    'statement_timeout': 30000,  # 30 saniye
    'lock_timeout': 10000,  # 10 saniye
    'idle_in_transaction_session_timeout': 60000,  # 60 saniye
    'work_mem': '64MB',  # Sıralama ve hash işlemleri için bellek
    'maintenance_work_mem': '256MB',  # Bakım işlemleri için bellek
    'effective_cache_size': '1GB',  # Önbellek boyutu
    'random_page_cost': 1.1,  # SSD için optimize
    'effective_io_concurrency': 200,  # Paralel I/O işlemleri
    'max_worker_processes': 8,  # Worker process sayısı
    'max_parallel_workers': 8,  # Paralel worker sayısı
    'max_parallel_workers_per_gather': 4,  # Her sorgu için paralel worker
    'max_parallel_maintenance_workers': 4,  # Bakım işlemleri için paralel worker
}

# Django AllAuth settings
SITE_ID = 1
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']

# Crispy Forms settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# JWT settings
SIMPLE_JWT = {
    # Token süreleri - .env'den alınabilir
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', 60))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME_DAYS', 1))),
    'MOBILE_ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_MOBILE_TOKEN_LIFETIME_MINUTES', 30))),
    'ADMIN_ACCESS_TOKEN_LIFETIME': timedelta(hours=int(os.getenv('JWT_ADMIN_TOKEN_LIFETIME_HOURS', 2))),
    'REMEMBER_ME_LIFETIME': timedelta(days=int(os.getenv('JWT_REMEMBER_ME_LIFETIME_DAYS', 7))),
    
    # Token yenileme ayarları
    'ROTATE_REFRESH_TOKENS': True,  # Refresh token kullanıldığında yeni token üretilir
    'BLACKLIST_AFTER_ROTATION': True,  # Eski token blacklist'e eklenir
    
    # Algoritma ve imzalama ayarları
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    
    # Token içeriği ayarları
    'TOKEN_TYPE_CLAIM': 'token_type',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    # Sliding token ayarları
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_SLIDING_TOKEN_LIFETIME_MINUTES', 30))),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=int(os.getenv('JWT_SLIDING_TOKEN_REFRESH_LIFETIME_DAYS', 1))),
    
    # Token yeniden kullanım ayarları
    'JTI_CLAIM': 'jti',
    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSerializer',
}

# Authentication settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# OpenAI settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Blockchain settings
BLOCKCHAIN_NETWORK = os.getenv('BLOCKCHAIN_NETWORK', 'testnet')
BLOCKCHAIN_API_KEY = os.getenv('BLOCKCHAIN_API_KEY')

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

# Brute-force koruma ayarları
MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
LOGIN_BLOCK_TIME_MINUTES = int(os.getenv('LOGIN_BLOCK_TIME_MINUTES', 15))
BRUTE_FORCE_PROTECTED_URLS = [
    '/api/token/',
    '/api/token/refresh/',
    '/accounts/login/',
    '/admin/login/',
]

# IP kısıtlama ayarları (varsayılan olarak boş)
RESTRICTED_IPS = []
ALLOWED_IPS = [] 