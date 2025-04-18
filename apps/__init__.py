# -*- coding: utf-8 -*-
"""
FinAsis Modül Paketleri

Bu paket, FinAsis uygulamasının tüm modüllerini içerir.
Django projesi için, her bir alt klasör bir Django uygulaması veya uygulama grubu olarak tasarlanmıştır.

Dizin Yapısı:
-------------
/finance       - Finans modülleri (muhasebe, bankacılık, çek, e-fatura)
/assets        - Varlık yönetimi modülleri
/docs          - Dokümantasyon ve belge yönetimi
/integration   - Dış sistem entegrasyonları
/company       - Şirket ve müşteri yönetimi
/inventory     - Stok ve envanter yönetimi
/game          - Eğitim oyunları ve simülasyonlar
/users         - Kullanıcı yönetimi ve yetkilendirme
/core          - Çekirdek sistem fonksiyonları
/api           - API servisleri ve uç noktaları
/analytics     - Raporlama ve analitik modülleri

Kullanım:
---------
Bu modüller doğrudan import edilebilir:
    from apps.finance import apps.accounting
    from apps.users import apps.permissions

Geliştiriciler İçin Not:
-----------------------
1. Her modül kendi içinde bağımsız olmalıdır.
2. Modüller arası bağımlılıklar en aza indirilmelidir.
3. Ortak işlevler core modülüne taşınmalıdır.
"""

# Django yapılandırmasını basitleştirmek için paket 
# yapısını auto-discovery mekanizmasıyla uyumlu hale getiriyoruz.
default_app_config = 'apps.AppsConfig' 