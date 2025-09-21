# -*- coding: utf-8 -*-
from django.apps import AppConfig

class PermissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.apps.permissions'
    verbose_name = 'İzinler'

    def ready(self):
    from src.apps.permissions import signals  # noqa