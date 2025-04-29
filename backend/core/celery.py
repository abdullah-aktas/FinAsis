# -*- coding: utf-8 -*-
import os
from celery import Celery
from django.conf import settings

# Django settings modülünü Celery için ayarla
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Celery uygulamasını oluştur
app = Celery('finasis')

# Celery yapılandırmasını Django settings'den al
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tüm kayıtlı Django uygulama yapılandırmalarını yükle
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 