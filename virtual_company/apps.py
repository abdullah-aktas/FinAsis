from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class VirtualCompanyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'virtual_company'
    verbose_name = _('Sanal Şirket')

    def ready(self):
        """
        Uygulama başlatıldığında sinyalleri yükle.
        """
        import virtual_company.signals  # noqa 