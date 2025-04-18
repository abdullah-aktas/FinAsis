# -*- coding: utf-8 -*-
"""
FinAsis Apps Django Yapılandırması
"""
from django.apps import AppConfig


class AppsConfig(AppConfig):
    """
    Apps ana paketinin yapılandırması.
    Bu sınıf, tüm alt modüllerin Django tarafından doğru şekilde tanınmasını sağlar.
    """
    name = 'apps'
    verbose_name = 'FinAsis Uygulamaları'
    
    def ready(self):
        """
        Django uygulaması hazır olduğunda çalışacak metot.
        Burada sinyal bağlantıları ve uygulama başlangıcında yapılması 
        gereken diğer işlemler yapılabilir.
        """
        # İçe aktarmaları burada yapın, döngüsel bağımlılıklardan kaçınmak için
        # Örnek: import apps.users.signals 