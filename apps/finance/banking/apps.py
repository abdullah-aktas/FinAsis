# -*- coding: utf-8 -*-
"""
FinAsis Bankacılık modülü uygulaması
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BankingConfig(AppConfig):
    """Bankacılık uygulaması yapılandırması"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.finance.banking'
    verbose_name = _('Bankacılık')
    label = 'finance_banking'  # Benzersiz etiket
    
    def ready(self):
        """Uygulama başlatıldığında yapılacak işlemler"""
        try:
            import apps.finance.banking.signals  # noqa
        except ImportError:
            pass 