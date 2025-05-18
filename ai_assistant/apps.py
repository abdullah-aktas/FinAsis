# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AIAssistantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_assistant'
    verbose_name = _('AI Asistan')

    def ready(self):
        try:
            import ai_assistant.signals
        except ImportError:
            pass
