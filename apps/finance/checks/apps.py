# -*- coding: utf-8 -*-
"""
FinAsis Çek/Senet modülü uygulaması
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ChecksConfig(AppConfig):
    """Çek/Senet uygulaması yapılandırması"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.finance.checks'
    verbose_name = _('Çek/Senet Yönetimi')
    label = 'finance_checks'  # Benzersiz etiket
    
    def ready(self):
        """Uygulama başlatıldığında yapılacak işlemler"""
        try:
            import apps.finance.checks.signals  # noqa
        except ImportError:
            pass 