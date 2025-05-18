# -*- coding: utf-8 -*-
"""
Geliştirme ortamı ayarları
"""
from .base import *
import os

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database - SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Debug toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# E-Belge Dosya Ayarları
EDOCUMENT_STORAGE_PATH = os.path.join(BASE_DIR, 'media', 'edocuments')
EDOCUMENT_PDF_PATH = os.path.join(EDOCUMENT_STORAGE_PATH, 'pdf')
EDOCUMENT_XML_PATH = os.path.join(EDOCUMENT_STORAGE_PATH, 'xml')

# E-Belge Arşivleme Ayarları
EDOCUMENT_RETENTION_PERIOD = 10  # Yıl
EDOCUMENT_BACKUP_ENABLED = True
EDOCUMENT_BACKUP_PATH = os.path.join(BASE_DIR, 'backups', 'edocuments')

# E-Belge Önbellek Ayarları
EDOCUMENT_CACHE_ENABLED = True
EDOCUMENT_CACHE_TIMEOUT = 3600  # Saniye

# E-Belge Log Ayarları
EDOCUMENT_LOG_LEVEL = 'INFO'
EDOCUMENT_LOG_FILE = os.path.join(BASE_DIR, 'logs', 'edocument.log')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'debug.log'),
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}