# -*- coding: utf-8 -*-
from django.apps import AppConfig

class FinAsisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finasis'
    verbose_name = 'FinAsis' 
    label = 'finasis'  # Benzersiz etiket
    def ready(self):
        """Uygulama başlatıldığında yapılacak işlemler"""
        # Signal handlers'ları import et
        try:
            import finasis.signals  # noqa
        except ImportError:
            pass
        # Diğer başlangıç işlemleri
        # Örneğin, başlangıç verilerini yükleme, görev zamanlayıcıları ayarlama vb.
        # Burada uygulama başlatıldığında yapılacak diğer işlemleri ekleyebilirsiniz.
        # Örnek: print("FinAsis uygulaması başlatıldı.")
        # print("FinAsis uygulaması başlatıldı.")
        