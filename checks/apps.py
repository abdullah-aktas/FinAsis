from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ChecksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "checks"
    verbose_name = _('Kontroller')

    def ready(self):
        try:
            import checks.signals  # noqa
        except ImportError:
            pass
