# -*- coding: utf-8 -*-
import os
from celery import Celery

# Django ayarlarını varsayılan Django ayarları modülü olarak ayarla
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Celery'nin Django ayarlarını kullanmasını sağla
app.config_from_object('django.conf:settings', namespace='CELERY')

# Görev modüllerini otomatik olarak yükle
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 