"""
Celery Yapılandırması
---------------------
Bu dosya, Celery yapılandırmasını içerir.
"""

import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Celery uygulamasını oluştur
app = Celery('config')

# Celery ayarlarını Django ayarlarından al
app.config_from_object('django.conf:settings', namespace='CELERY')

# Görevleri otomatik olarak yükle
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Zamanlanmış görevler
app.conf.beat_schedule = {
    # Veritabanı bakım görevleri
    'vacuum-analyze-database': {
        'task': 'accounting.tasks.vacuum_analyze_database',
        'schedule': crontab(hour=2, minute=0),  # Her gün saat 02:00'de
    },
    'reindex-database': {
        'task': 'accounting.tasks.reindex_database',
        'schedule': crontab(hour=3, minute=0, day_of_week='sunday'),  # Her Pazar saat 03:00'de
    },
    'cleanup-old-data': {
        'task': 'accounting.tasks.cleanup_old_data',
        'schedule': crontab(hour=4, minute=0, day_of_week='sunday'),  # Her Pazar saat 04:00'de
    },
    'optimize-tables': {
        'task': 'accounting.tasks.optimize_tables',
        'schedule': crontab(hour=1, minute=0, day_of_week='sunday'),  # Her Pazar saat 01:00'de
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 