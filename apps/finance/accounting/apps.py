# -*- coding: utf-8 -*-
"""
FinAsis Muhasebe modülü uygulaması
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountingConfig(AppConfig):
    """Muhasebe uygulaması yapılandırması"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance.accounting'
    verbose_name = _('Muhasebe')
    label = 'finance_accounting'  # Benzersiz etiket
    
    def ready(self):
        """Uygulama başlatıldığında yapılacak işlemler"""
        # Signal handlers'ları import et
        try:
            import finance.accounting.signals  # noqa
        except ImportError:
            pass 