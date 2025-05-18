# -*- coding: utf-8 -*-
"""
Test ortamı ayarları
"""
from .base import *

DEBUG = False

# Kullanılacak test veritabanı
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Test için hızlandırma
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Cache disable
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Debug toolbar'ı devre dışı bırak
MIDDLEWARE = [
    middleware for middleware in MIDDLEWARE
    if middleware != 'debug_toolbar.middleware.DebugToolbarMiddleware'
]

# Third-party uygulamaları test ortamında kullanmayacağız
INSTALLED_APPS = [
    app for app in INSTALLED_APPS
    if not app.startswith('debug_toolbar')
]

# Email
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Celery
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Medya
MEDIA_ROOT = os.path.join(BASE_DIR, 'tests/media')

# Süreçleri hızlandırmak için
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'