from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "stock_management"
    verbose_name = _('Envanter ve Varlık Yönetimi')

    def ready(self):
        """Uygulama başlatıldığında yapılacak işlemler"""
        try:
            import stock_management.signals
        except ImportError:
            pass
