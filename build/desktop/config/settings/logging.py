# -*- coding: utf-8 -*-
"""
Uygulama günlük kaydı (logging) yapılandırması.
"""
import os
from pathlib import Path

# Proje kök dizini
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Log dizini oluştur
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Günlük kaydı ayarları
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
        'standard': {
            'format': '{levelname} [{asctime}] {name}: {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
        'file_app': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'app.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 10,
            'formatter': 'standard',
        },
        'file_security': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'security.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 10,
            'formatter': 'standard',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'error.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'file_database': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'database.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'query_performance': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'query_performance.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_app', 'mail_admins'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file_error', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file_database'],
            'level': 'DEBUG' if os.environ.get('DJANGO_DEBUG', 'False') == 'True' else 'INFO',
            'propagate': False,
        },
        'django.db.backends.postgresql': {
            'handlers': ['file_database'],
            'level': 'DEBUG' if os.environ.get('DJANGO_DEBUG', 'False') == 'True' else 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file_security', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'finasis': {
            'handlers': ['console', 'file_app'],
            'level': os.environ.get('FINASIS_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'security': {
            'handlers': ['console', 'file_security', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends.postgresql.performance': {
            'handlers': ['query_performance'],
            'level': 'INFO',
            'propagate': False,
        },
    },
} 