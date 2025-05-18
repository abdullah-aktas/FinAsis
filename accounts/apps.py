# -*- coding: utf-8 -*-
from django.apps import AppConfig # type: ignore

class AccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounting'  # klasör adıyla birebir aynı olmalı
    verbose_name = 'Hesap Yönetimi'  # admin panelinde görünen isim
    
    def ready(self):
        """
        Uygulama başlatıldığında sinyalleri yükle.
        """
        import accounts.signals 