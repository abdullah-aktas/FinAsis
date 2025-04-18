from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HrManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.hr_management"
    verbose_name = _('İnsan Kaynakları ve Kullanıcı Yönetimi')

    def ready(self):
        """Uygulama başlatıldığında yapılacak işlemler"""
        try:
            # Sinyaller (signals) var ise burada import edilir
            import apps.hr_management.signals
        except ImportError:
            pass
