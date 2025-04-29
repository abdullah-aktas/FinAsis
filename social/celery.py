# -*- coding: utf-8 -*-
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social.settings')

# Celery uygulamasını oluştur
app = Celery('social')

# Celery ayarlarını Django ayarlarından yükle
app.config_from_object('django.conf:settings', namespace='CELERY')

# Zamanlanmış görevleri yapılandır
app.conf.beat_schedule = {
    'send-daily-notification-summary': {
        'task': 'social.tasks.send_daily_notification_summary',
        'schedule': crontab(hour=20, minute=0),  # Her gün saat 20:00'de
        'options': {
            'queue': 'notifications',
            'expires': 3600,  # 1 saat sonra süresi dolar
        },
    },
    'cleanup-old-notifications': {
        'task': 'social.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=0, minute=0),  # Her gün gece yarısı
        'options': {
            'queue': 'maintenance',
            'expires': 3600,
        },
    },
    'process-pending-media': {
        'task': 'social.tasks.process_pending_media',
        'schedule': crontab(minute='*/15'),  # Her 15 dakikada bir
        'options': {
            'queue': 'media',
            'expires': 900,  # 15 dakika sonra süresi dolar
        },
    },
}

# Görev kuyruklarını yapılandır
app.conf.task_queues = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'notifications': {
        'exchange': 'notifications',
        'routing_key': 'notifications',
    },
    'media': {
        'exchange': 'media',
        'routing_key': 'media',
    },
    'maintenance': {
        'exchange': 'maintenance',
        'routing_key': 'maintenance',
    },
}

# Görev yönlendirme kurallarını ayarla
app.conf.task_routes = {
    'social.tasks.send_notification_email': {'queue': 'notifications'},
    'social.tasks.send_daily_notification_summary': {'queue': 'notifications'},
    'social.tasks.process_uploaded_image': {'queue': 'media'},
    'social.tasks.process_uploaded_video': {'queue': 'media'},
    'social.tasks.cleanup_old_notifications': {'queue': 'maintenance'},
}

# Görev zaman aşımı ayarları
app.conf.task_time_limit = 3600  # 1 saat
app.conf.task_soft_time_limit = 3000  # 50 dakika

# Hata işleme ayarları
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True
app.conf.task_ignore_result = True

# Otomatik olarak görev modüllerini keşfet
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Hata işleyicisi
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 