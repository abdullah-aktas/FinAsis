# Accounting Uygulaması

Bu modül, FinAsis platformunda temel muhasebe işlemlerini yönetir. Şirket, müşteri, fatura, gider, ürün, satış, ödeme, banka hesabı ve banka işlemleri gibi temel finansal süreçleri kapsar.

## Klasör Yapısı
- `models/` ve `models.py`: Veri modelleri
- `views/`: Her model için ayrı view dosyaları
- `services/`: Servis ve yardımcı fonksiyonlar
- `serializers/`: API için serializerlar
- `templates/accounting/`: Web arayüzü şablonları
- `static/accounting/`: Statik dosyalar
- `urls/`: API ve web için ayrı URL dosyaları
- `tests/`: Birim testler

## Geliştirme Notları
- Kodlar modüler ve fonksiyonel olarak ayrılmıştır.
- API ve web endpointleri ayrıdır.
- Ortak servis fonksiyonları `services/common_services.py` dosyasında toplanmıştır.
- Testler `tests/` klasöründe yer alır.

## Katkı
Kodunuzu göndermeden önce testlerinizi çalıştırın ve PEP8'e uygun kod yazmaya özen gösterin. 