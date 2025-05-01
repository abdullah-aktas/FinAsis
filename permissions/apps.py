# -*- coding: utf-8 -*-
from django.apps import AppConfig

class PermissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'permissions'
    verbose_name = 'İzinler'

    def ready(self):
        import permissions.signals  # noqa