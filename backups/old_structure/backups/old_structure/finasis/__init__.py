# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Bu import, Celery uygulamasının Django başlatıldığında otomatik olarak yüklenmesini sağlar
from .celery import app as celery_app

__all__ = ('celery_app',)
