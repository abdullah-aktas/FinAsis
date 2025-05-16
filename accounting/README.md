# Accounting Modülü

Bu modül, FinAsis projesinde muhasebe işlemlerini yönetir.

## Kapsam
- Muhasebe kayıtları
- Hesap yönetimi
- Vergi işlemleri
- Finansal raporlar
- Çoklu dil desteği (en, ku, ar)

## Klasör ve Dosya Yapısı
```
accounting/
├── __init__.py
├── apps.py
├── models.py
├── views.py
├── admin.py
├── urls.py
├── forms.py
├── tests.py
├── services.py
├── tasks.py
├── managers.py
├── requirements.txt
├── turkish_tax.py
├── locale/
│   ├── en/LC_MESSAGES/django.po
│   ├── ku/LC_MESSAGES/django.po
│   └── ar/LC_MESSAGES/django.po
├── templates/
├── tests/
├── utils/
├── views/
├── serializers/
├── services/
├── forms/
├── api/
```

## Test
- Tüm önemli fonksiyon ve sınıflar için testler `tests.py` ve `tests/` klasöründe yer alır.
- Testleri çalıştırmak için:
  ```bash
  pytest accounting/
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