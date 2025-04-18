from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import django

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finasis.settings')
django.setup()

# Celery uygulamasını oluştur
app = Celery('finasis')

# Celery ayarlarını Django settings'ten yükle
app.config_from_object('django.conf:settings', namespace='CELERY')

# Görev modüllerini otomatik olarak keşfet
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 