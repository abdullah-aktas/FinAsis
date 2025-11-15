from django.apps import AppConfig


class AdvisorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'advisors'
    verbose_name = 'Mali Müşavirler'

    def ready(self):
        # Marketplace modellerini app registry'e kaydet
        from . import models_marketplace  # noqa: F401