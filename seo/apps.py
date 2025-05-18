# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SeoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "seo"
    verbose_name = _('SEO Yönetimi')

    def ready(self):
        """Uygulama hazır olduğunda çalışacak kodlar"""
        try:
            import seo.signals  # noqa
            import seo.tasks  # noqa
        except ImportError:
            pass
