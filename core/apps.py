# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = _('Ã‡ekirdek')

    def ready(self):
        try:
            import core.signals  # noqa
        except ImportError:
            pass 