"""
Finance Modülü - Uygulama Yapılandırması
---------------------
Bu dosya, Finance modülünün uygulama yapılandırmasını içerir.
"""

from django.apps import AppConfig

class FinanceConfig(AppConfig):
    """
    Finance modülü yapılandırması.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance'
    verbose_name = 'Finans Yönetimi'
    
    def ready(self):
        """
        Uygulama hazır olduğunda çalışacak kod.
        """
        try:
            import finance.signals
        except ImportError:
            pass 