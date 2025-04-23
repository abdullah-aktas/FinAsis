# E-posta Ayarları
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Gmail SMTP sunucusu
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Gmail adresiniz
EMAIL_HOST_PASSWORD = 'your-app-password'  # Gmail uygulama şifreniz
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'  # Varsayılan gönderen e-posta

# Site Ayarları
SITE_NAME = 'FinAsis'
SITE_URL = 'https://finasis.com'  # Gerçek site URL'si

# Bildirim Ayarları
NOTIFICATION_SETTINGS = {
    'email_notifications': True,  # E-posta bildirimlerini etkinleştir
    'daily_summary': True,  # Günlük özet e-postalarını etkinleştir
    'notification_types': {
        'like': True,  # Beğeni bildirimlerini etkinleştir
        'comment': True,  # Yorum bildirimlerini etkinleştir
        'follow': True,  # Takip bildirimlerini etkinleştir
        'mention': True,  # Etiketleme bildirimlerini etkinleştir
    },
    'retention_days': 30,  # Bildirimlerin saklanma süresi (gün)
}

# Medya Ayarları
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Resim İşleme Ayarları
IMAGE_SETTINGS = {
    'max_size': (1200, 1200),  # Maksimum resim boyutu
    'quality': 85,  # JPEG kalitesi
    'allowed_formats': ['jpg', 'jpeg', 'png', 'gif'],
    'max_file_size': 5 * 1024 * 1024,  # 5MB
}

# Video İşleme Ayarları
VIDEO_SETTINGS = {
    'max_duration': 300,  # Maksimum süre (saniye)
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'allowed_formats': ['mp4', 'mov', 'avi'],
    'thumbnail_size': (320, 180),  # Video önizleme boyutu
}

# Önbellek Ayarları
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery Ayarları
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Istanbul'

# Zamanlanmış Görevler
CELERY_BEAT_SCHEDULE = {
    'send-daily-notification-summary': {
        'task': 'social.tasks.send_daily_notification_summary',
        'schedule': crontab(hour=20, minute=0),  # Her gün saat 20:00'de
    },
    'cleanup-old-notifications': {
        'task': 'social.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=0, minute=0),  # Her gün gece yarısı
    },
}

# Güvenlik Ayarları
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Loglama Ayarları
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
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/social.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'social': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
} 