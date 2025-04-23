import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finasis.settings')

app = Celery('finasis')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-game-state': {
        'task': 'games.tasks.update_game_state',
        'schedule': 300.0,  # Her 5 dakikada bir
    },
    'cleanup-inactive-games': {
        'task': 'games.tasks.cleanup_inactive_games',
        'schedule': crontab(hour=0, minute=0),  # Her gün gece yarısı
    },
} 