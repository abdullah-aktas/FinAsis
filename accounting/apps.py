# -*- coding: utf-8 -*-
# accounting/apps.py
from django.apps import AppConfig

class AccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounting'
    verbose_name = 'Muhasebe'
    
    def ready(self):
        pass