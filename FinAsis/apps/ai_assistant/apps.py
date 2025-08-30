# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AIAssistantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'FinAsis.apps.ai_assistant'
    verbose_name = _('AI Asistan')

    def ready(self):
        try:
            import FinAsis.apps.ai_assistant.signals
        except ImportError:
            pass
