from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

app = Celery('finasis')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Zamanlanmış görevler
app.conf.beat_schedule = {
    # Veritabanı bakım görevleri
    'vacuum-analyze-database': {
        'task': 'apps.accounting.tasks.vacuum_analyze_database',
        'schedule': crontab(hour=2, minute=0),  # Her gün saat 02:00'de
    },
    'reindex-database': {
        'task': 'apps.accounting.tasks.reindex_database',
        'schedule': crontab(hour=3, minute=0, day_of_week='sunday'),  # Her Pazar saat 03:00'de
    },
    'cleanup-old-data': {
        'task': 'apps.accounting.tasks.cleanup_old_data',
        'schedule': crontab(hour=4, minute=0, day_of_week='sunday'),  # Her Pazar saat 04:00'de
    },
    'optimize-tables': {
        'task': 'apps.accounting.tasks.optimize_tables',
        'schedule': crontab(hour=1, minute=0, day_of_week='sunday'),  # Her Pazar saat 01:00'de
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 