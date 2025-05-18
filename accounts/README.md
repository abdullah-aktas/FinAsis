# Accounts Modülü

Bu modül, FinAsis projesinde kullanıcı hesap yönetimi ve kimlik doğrulama işlemlerini yönetir.

## Kapsam
- Kullanıcı hesapları
- Kimlik doğrulama ve yetkilendirme
- Kullanıcı profilleri
- Bildirimler ve tercihler
- Çoklu dil desteği (en, ku, ar)

## Klasör ve Dosya Yapısı
```
accounts/
├── __init__.py
├── apps.py
├── models.py
├── views.py
├── admin.py
├── urls.py
├── forms.py
├── tests.py
├── signals.py
├── decorators.py
├── locale/
│   ├── en/LC_MESSAGES/django.po
│   ├── ku/LC_MESSAGES/django.po
│   └── ar/LC_MESSAGES/django.po
├── templates/
├── tests/
├── utils/
├── views/
├── serializers/
├── api/
├── forms/
├── mixins/
```

## Test
- Tüm önemli fonksiyon ve sınıflar için testler `tests.py` ve `tests/` klasöründe yer alır.
- Testleri çalıştırmak için:
  ```bash
  pytest accounts/
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