# FinAsis Config Paketi
"""
Bu paket projenin tüm yapılandırma dosyalarını içerir.
- /settings: Django yapılandırma dosyaları
""" 

from .celery import app as celery_app

__all__ = ('celery_app',) 