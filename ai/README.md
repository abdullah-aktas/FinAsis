# AI Modülü

Bu modül, FinAsis projesinde yapay zeka ve asistan servislerini yönetir.

## Kapsam
- AI tabanlı asistan fonksiyonları
- Doğal dil işleme servisleri
- Entegrasyon ve yardımcı AI servisleri
- Çoklu dil desteği (en, ku, ar)

## Klasör ve Dosya Yapısı
```
ai/
├── __init__.py
├── apps.py
├── models.py
├── views.py
├── admin.py
├── urls.py
├── forms.py
├── tests.py
├── assistant.py
├── locale/
│   ├── en/LC_MESSAGES/django.po
│   ├── ku/LC_MESSAGES/django.po
│   └── ar/LC_MESSAGES/django.po
├── services/
```

## Test
- Tüm önemli fonksiyon ve sınıflar için testler `tests.py` ve `tests/` klasöründe yer alır.
- Testleri çalıştırmak için:
  ```bash
  pytest ai/
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