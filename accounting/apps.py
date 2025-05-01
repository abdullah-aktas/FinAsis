# -*- coding: utf-8 -*-
# accounting/apps.py
from django.apps import AppConfig

class AccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounting'
    verbose_name = 'Hesap Yönetimi'

    def ready(self):
        """Uygulama başlatıldığında yapılacak işlemler"""
        # Signal handlers'ları import et
        try:
            import accounting.signals  # noqa
        except ImportError:
            pass
        # Diğer başlangıç işlemleri
        # Örneğin, başlangıç verilerini yükleme, görev zamanlayıcıları ayarlama vb.
        # Burada uygulama başlatıldığında yapılacak diğer işlemleri ekleyebilirsiniz.
        # Örnek: print("Muhasebe uygulaması başlatıldı.")