from django.apps import AppConfig


class EdocumentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.edocument"
    verbose_name = "E-Document"

    def ready(self):
        """Uygulama hazır olduğunda sinyalleri yükle"""
        import apps.edocument.signals
