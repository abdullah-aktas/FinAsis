# -*- coding: utf-8 -*-
"""
FinAsis E-Fatura modülü uygulaması
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EInvoiceConfig(AppConfig):
    """E-Fatura uygulaması yapılandırması"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.finance.einvoice'
    verbose_name = _('E-Fatura')
    label = 'finance_einvoice'  # Benzersiz etiket
    
    def ready(self):
        """Uygulama başlatıldığında yapılacak işlemler"""
        try:
            import apps.finance.einvoice.signals  # noqa
        except ImportError:
            pass 