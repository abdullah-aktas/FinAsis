# Locale (Çoklu Dil) Yönetimi

## Amaç
Bu klasör, FinAsis projesinin hem backend (Django) hem de frontend (JS) için çoklu dil ve yerelleştirme desteğini sağlar.

## Klasör Yapısı
- `tr/`, `en/`, `de/`, `fr/`, `ar/`, `ku/` : Her dil için Django .po/.mo dosyaları (`LC_MESSAGES/django.po`)
- `tr.json`, `en.json`, ... : Frontend için kısa JSON çeviri dosyaları (navbar, temel butonlar vs.)
- `js/` : Frontend için kapsamlı modüler JSON dosyaları (dashboard, hata mesajları, modüller vs.)

## Backend (Django) Çevirileri
- Django'nun klasik i18n altyapısı kullanılır.
- .po dosyalarını güncellemek için:
  ```bash
  django-admin makemessages -a
  django-admin compilemessages
  ```
- Backend'de `ugettext`, `gettext_lazy` gibi fonksiyonlarla kullanılır.

## Frontend (JS) Çevirileri
- JSON dosyaları ile modern, hızlı ve dinamik frontend çeviri desteği sağlanır.
- `static/locales/` veya `apps/locale/js/` altındaki JSON dosyaları, React/Vue gibi frameworklerde veya vanilla JS ile kolayca kullanılabilir.
- Anahtarlar kısa ve anlamlı tutulmalı, backend ile paralellik sağlanmalı.

## Yeni Dil Ekleme
1. Django için:
   ```bash
   django-admin makemessages -l yeni_dil
   django-admin compilemessages
   ```
2. Frontend için:
   - `static/locales/yeni_dil.json` dosyasını oluşturun.
   - Gerekirse `apps/locale/js/yeni_dil.json` ekleyin.

## Çeviri Güncelleme
- `.po` dosyalarını güncelledikten sonra:
  ```bash
  django-admin compilemessages
  ```
- JSON dosyalarını güncelledikten sonra frontend'i yeniden başlatın.

## RTL Diller
- Arapça ve Kürtçe gibi sağdan sola diller için `rtl.css` ve uygun HTML `dir` kullanımı gereklidir.
- Frontend'de otomatik yön değişimi için dil kodu kontrolü yapılmalıdır.

## Notlar
- Backend ve frontend çevirileri arasında tutarlılık sağlanmalı.
- Dil seçici (language selector) tüm arayüzlerde erişilebilir olmalı.
- Çeviri anahtarları hem backend hem frontend için anlamlı ve kısa tutulmalı. 