"""
Users Modülü - AppConfig
---------------------
Bu dosya, Users modülünün AppConfig sınıfını içerir.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = _('Kullanıcılar')
    
    def ready(self):
        """Uygulama hazır olduğunda çalışacak kodlar"""
        try:
            # Sinyalleri içe aktar
            import users.signals
        except ImportError:
            pass 