from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class VirtualCompanyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.virtual_company'
    verbose_name = _('Sanal Şirket')

    def ready(self):
        import virtual_company.signals  # noqa 