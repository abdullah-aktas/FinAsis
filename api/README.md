# API Modülü

Bu modül, FinAsis projesinde REST API ve servis entegrasyonlarını yönetir.

## Kapsam
- Tüm ana modüller için API endpoint'leri
- Kimlik doğrulama ve yetkilendirme
- Veri transferi ve entegrasyon
- Çoklu dil desteği (en, ku, ar)

## Klasör ve Dosya Yapısı
```
api/
├── __init__.py
├── apps.py
├── models.py (varsa)
├── views.py
├── admin.py (varsa)
├── urls.py
├── serializers.py
├── settings.py
├── tests.py
├── locale/
│   ├── en/LC_MESSAGES/django.po
│   ├── ku/LC_MESSAGES/django.po
│   └── ar/LC_MESSAGES/django.po
├── views/
├── serializers/
├── finance/
├── crm/
├── accounting/
```

## Test
- Tüm önemli fonksiyon ve sınıflar için testler `tests.py` ve `tests/` klasöründe yer alır.
- Testleri çalıştırmak için:
  ```bash
  pytest api/
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
