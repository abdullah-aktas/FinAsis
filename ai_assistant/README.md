# AI Assistant Modülü

Bu modül, FinAsis projesinde yapay zeka tabanlı asistan ve ilgili servisleri yönetir.

## Kapsam
- AI tabanlı asistan fonksiyonları
- Doğal dil işleme ve yanıt üretimi
- API ve servis entegrasyonları
- Çoklu dil desteği (en, ku, ar)

## Klasör ve Dosya Yapısı
```
ai_assistant/
├── __init__.py
├── apps.py
├── models.py
├── views.py
├── admin.py
├── urls.py
├── serializers.py
├── services.py
├── tests.py
├── locale/
│   ├── en/LC_MESSAGES/django.po
│   ├── ku/LC_MESSAGES/django.po
│   └── ar/LC_MESSAGES/django.po
├── templates/
├── static/
├── services/
├── views/
├── tests/
├── api/
```

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