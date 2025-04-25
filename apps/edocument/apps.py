from django.apps import AppConfig


class EdocumentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "edocument"
    verbose_name = "E-Doküman Yönetimi"

    def ready(self):
        """Uygulama hazır olduğunda sinyalleri yükle"""
        import edocument.signals
