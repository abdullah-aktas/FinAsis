from celery.schedules import crontab
from celery import Celery
from django.conf import settings

app = Celery('integrations')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Zamanlanmış görevler
app.conf.beat_schedule = {
    # Her saat başı sağlık kontrolü
    'check-integration-health': {
        'task': 'apps.integrations.tasks.check_integration_health',
        'schedule': crontab(minute=0),  # Her saat başı
    },
    
    # Her gece yarısı log temizliği
    'cleanup-old-logs': {
        'task': 'apps.integrations.tasks.cleanup_old_logs',
        'schedule': crontab(minute=0, hour=0),  # Her gece yarısı
    },
    
    # E-ticaret entegrasyonları için senkronizasyon
    'sync-hepsiburada': {
        'task': 'apps.integrations.tasks.run_integration_sync',
        'schedule': crontab(minute='*/15'),  # Her 15 dakikada bir
        'args': ('hepsiburada',)
    },
    'sync-shopify': {
        'task': 'apps.integrations.tasks.run_integration_sync',
        'schedule': crontab(minute='*/5'),  # Her 5 dakikada bir
        'args': ('shopify',)
    },
    'sync-woocommerce': {
        'task': 'apps.integrations.tasks.run_integration_sync',
        'schedule': crontab(minute='*/10'),  # Her 10 dakikada bir
        'args': ('woocommerce',)
    },
    'sync-magento': {
        'task': 'apps.integrations.tasks.run_integration_sync',
        'schedule': crontab(minute='*/20'),  # Her 20 dakikada bir
        'args': ('magento',)
    },
    
    # ERP entegrasyonları için senkronizasyon
    'sync-luca': {
        'task': 'apps.integrations.tasks.run_integration_sync',
        'schedule': crontab(minute='*/30'),  # Her 30 dakikada bir
        'args': ('luca',)
    },
    'sync-mikro': {
        'task': 'apps.integrations.tasks.run_integration_sync',
        'schedule': crontab(minute='*/30'),  # Her 30 dakikada bir
        'args': ('mikro',)
    },
    'sync-logo': {
        'task': 'apps.integrations.tasks.run_integration_sync',
        'schedule': crontab(minute='*/30'),  # Her 30 dakikada bir
        'args': ('logo',)
    },
    'sync-netsis': {
        'task': 'apps.integrations.tasks.run_integration_sync',
        'schedule': crontab(minute='*/30'),  # Her 30 dakikada bir
        'args': ('netsis',)
    }
} 