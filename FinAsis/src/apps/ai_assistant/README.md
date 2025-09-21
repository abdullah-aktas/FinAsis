# AI Assistant Uygulaması

Bu modül, FinAsis platformunda yapay zeka destekli finansal asistan, analiz, öneri ve otomasyon işlemlerini yönetir.

## Kapsam
- AI tabanlı asistan fonksiyonları
- Doğal dil işleme ve yanıt üretimi
- API ve servis entegrasyonları
- Çoklu dil desteği (en, ku, ar)

## Klasör Yapısı
- `models/` ve `models.py`: Veri modelleri
- `views/`: Fonksiyonel view dosyaları
- `services/`: Servis ve yardımcı fonksiyonlar
- `serializers/`: API için serializerlar
- `templates/ai_assistant/`: Web arayüzü şablonları
- `static/ai_assistant/`: Statik dosyalar
- `api/`: API endpointleri ve urls
- `urls/`: Web ve API için ayrı URL dosyaları
- `tests/`: Birim testler

## Geliştirme Notları
- Kodlar modüler ve fonksiyonel olarak ayrılmıştır.
- API ve web endpointleri ayrıdır.
- Testler `tests/` klasöründe yer alır.

## Test
- Tüm önemli fonksiyon ve sınıflar için testler `tests.py` ve `tests/` klasöründe yer alır.
- Testleri çalıştırmak için:
  ```bash
  pytest ai_assistant/
  ```

## Çeviri
- Çoklu dil desteği için `locale/` klasörü kullanılır.
- Çeviri dosyalarını güncellemek için:
  ```bash
  python manage.py makemessages -a
  python manage.py compilemessages
  ```

## Katkı
- Kodda fonksiyon ve sınıf açıklamaları bulunmalıdır.
- Kod standartlarına ve proje dokümantasyonuna uyulmalıdır.
- Kodunuzu göndermeden önce testlerinizi çalıştırın ve PEP8'e uygun kod yazmaya özen gösterin. 