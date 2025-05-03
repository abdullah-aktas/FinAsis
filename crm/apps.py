# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CrmConfig(AppConfig):
    """CRM ve Müşteri Yönetimi uygulaması yapılandırması"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'
    verbose_name = _('Müşteri İlişkileri')
    
    def ready(self):
        """Uygulama hazır olduğunda sinyalleri yükle"""
        try:
            import crm.signals
        except ImportError:
            pass
