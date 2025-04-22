from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CrmConfig(AppConfig):
    """CRM ve Müşteri Yönetimi uygulaması yapılandırması"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.crm'
    verbose_name = _('CRM ve Müşteri Yönetimi')
    label = 'crm'
    
    def ready(self):
        """Uygulama başlatıldığında yapılacak işlemler"""
        try:
            import crm.signals  # noqa
        except ImportError:
            pass
