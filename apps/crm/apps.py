from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CrmConfig(AppConfig):
    """CRM ve Müşteri Yönetimi uygulaması yapılandırması"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'
    verbose_name = 'Müşteri İlişkileri Yönetimi'
    label = 'crm'
    
    def ready(self):
        """Uygulama hazır olduğunda sinyalleri yükle"""
        import crm.signals
