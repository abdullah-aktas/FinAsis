from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finasis.settings')

app = Celery('crm')

# Celery ayarlarını Django ayarlarından yükle
app.config_from_object('django.conf:settings', namespace='CELERY')

# Görev modüllerini otomatik olarak yükle
app.autodiscover_tasks()

# Periyodik görevleri tanımla
app.conf.beat_schedule = {
    'check-overdue-activities': {
        'task': 'crm.tasks.check_overdue_activities',
        'schedule': crontab(minute='*/15'),  # Her 15 dakikada bir
    },
    'update-customer-credit-scores': {
        'task': 'crm.tasks.update_customer_credit_scores',
        'schedule': crontab(hour='*/6'),  # Her 6 saatte bir
    },
    'process-seasonal-campaigns': {
        'task': 'crm.tasks.process_seasonal_campaigns',
        'schedule': crontab(hour='*/12'),  # Her 12 saatte bir
    },
    'send-opportunity-reminders': {
        'task': 'crm.tasks.send_opportunity_reminders',
        'schedule': crontab(hour='*/1'),  # Her saat başı
    },
}

# Görev zaman aşımı ayarları
app.conf.task_time_limit = 3600  # 1 saat
app.conf.task_soft_time_limit = 3000  # 50 dakika

# Yeniden deneme ayarları
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True
app.conf.task_default_retry_delay = 300  # 5 dakika
app.conf.task_max_retries = 3

# Sonuç backend ayarları
app.conf.result_backend = 'django-db'
app.conf.result_expires = 3600  # 1 saat

# Broker ayarları
app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.broker_connection_retry_on_startup = True 