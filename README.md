# FinAsis Django Platform

Bu depo, FinAsis ekosistemindeki tüm modülleri tek bir Django projesi altında toplar.
Mimari, **Model–View–Presenter (MVP)** yaklaşımına uyacak şekilde düzenlenmiştir:

- **Modeller (Model)**: Her uygulamanın `models.py` dosyalarında yer alır.
- **Presenter Katmanı**: `common/presenters` ve uygulama bazlı `presenters/` paketleri;
  view'ların iş mantığını sadeleştirir.
- **View Katmanı**: HTTP isteklerini karşılayan ince katmandır; presenter'lardan dönen yanıtları işler.

## Kurulum

1. Gerekli paketleri yükleyin:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # (Windows)
   pip install -r requirements.txt
   ```

2. Ortam değişkenlerini tanımlayın (`env.example` dosyasını kopyalayarak başlayabilirsiniz):

   ```bash
   cp env.example .env
   ```

   Ardından aşağıdaki değerleri güncelleyin:
   ```dotenv
   DJANGO_SECRET_KEY=change-me
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=finasis.com.tr,www.finasis.com.tr
   DJANGO_CSRF_TRUSTED_ORIGINS=https://finasis.com.tr,https://www.finasis.com.tr
   DJANGO_SITE_BASE_URL=https://finasis.com.tr

   DJANGO_DB_ENGINE=django.db.backends.postgresql
   DJANGO_DB_NAME=finasis
   DJANGO_DB_USER=finasis
   DJANGO_DB_PASSWORD=change-me
   DJANGO_DB_HOST=127.0.0.1
   DJANGO_DB_PORT=5432

   DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   DJANGO_DEFAULT_FROM_EMAIL="FinAsis <noreply@finasis.com.tr>"
   DJANGO_EMAIL_HOST=smtp.finasis.com.tr
   DJANGO_EMAIL_PORT=587
   DJANGO_EMAIL_USE_TLS=True
   DJANGO_EMAIL_HOST_USER=apikey
   DJANGO_EMAIL_HOST_PASSWORD=change-me
   ```

3. Veritabanını hazırlayın:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. Geliştirme sunucusunu başlatın:
   ```bash
   python manage.py runserver
   ```

## Önemli Dosyalar

- `manage.py`: Django yönetim komutları için giriş noktası.
- `config/settings/`: Ortak ayarlar (`base.py`) ve ortam bazlı genişletmeler için başlangıç noktası.
- `config/asgi.py`: HTTP + WebSocket (Channels) yapılandırması.
- `config/urls.py`: Tüm uygulama URL'lerini merkezi olarak toplar.
- `src/apps/__init__.py`: Mevcut uygulamaları `src.apps.*` yolu üzerinden kullanılabilir hale getirir.

## MVP Presenter Yapısı

- `common/presenters/base.py`: Presenter için temel sınıf (`BasePresenter`) ve sonuç sarmalayıcısı (`PresenterResult`).
- Örnek kullanım: `accounts/presenters/dashboard.py` dosyası kullanıcı profilini bir presenter ile sunar.
  View tarafında ise `accounts/views.py` içinde `user_profile` fonksiyonu yalnızca:
  ```python
  presenter = UserDashboardPresenter(request)
  return presenter.render()
  ```
  şeklinde presenter'ı çağırır.

Bu yaklaşım, yeniden kullanılabilirliği artırır ve karmaşık iş kurallarını view katmanından izole eder.

## Notlar

- Channels varsayılan olarak bellek içi katman ile gelir. Üretim ortamında `CHANNEL_LAYERS` ayarını Redis gibi kalıcı bir katmanla güncelleyiniz.
- JWT tabanlı API kimliği doğrulama için `djangorestframework-simplejwt` kullanılır.
- `requirements.txt` dosyası temel bağımlılıkları içerir; modül gereksinimleri proje büyüdükçe genişletilebilir.
- PDF/WeasyPrint bileşeni için sistem bağımlılıklarını kurmayı unutmayın:
  - Ubuntu/Debian: `apt install libpango-1.0-0 libcairo2 libffi-dev libpangoft2-1.0-0 libjpeg-dev`
  - macOS (Homebrew): `brew install pango cairo gdk-pixbuf libffi`
  - Windows: Resmi WeasyPrint kurulum rehberindeki (https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation) paketleri yükleyin.

## Veri Maskeleme & Retention

- Log filtreleri, e-posta/telefon/IBAN/TCKN gibi PII verilerini otomatik maskeleyerek çıktı güvenliğini sağlar.
- Uygulama içi şifreleme için 32 baytlık Fernet anahtarını `DATA_ENCRYPTION_KEY` olarak tanımlayın:

  ```bash
  python - <<'PY'
  from cryptography.fernet import Fernet
  print(Fernet.generate_key().decode())
  PY
  ```

- Veri saklama politikalarını uygulamak için:

  ```bash
  python manage.py retention_execute --profile default          # kayıtları uygula
  python manage.py retention_execute --profile default --dry-run  # yalnızca önizleme
  ```

- Retention kuralları `retention/profiles/*.yml` altında tutulur; yeni profilleri bu dizine ekleyin veya mevcutları özelleştirin.

## Developer API Erişimi

- REST endpoint'leri artık `Authorization: ApiKey <prefix.secret>` veya `X-API-Key` başlıklarını kabul eder.
- API anahtarlarının hız limitleri plan bazlıdır (varsayılan `standard` = 1000 istek/saat, `freemium` = 120 istek/gün, `professional` = 5000 istek/saat, `enterprise` = 20000 istek/saat).
- Geliştirici portali üzerinden oluşturulan anahtarlar sadece whitelist'te yer alan IP'lerden kullanılabilir.
- Kullanım metrikleri otomatik olarak `DeveloperAPIKeyUsageLog` tablosuna yazılır; portal arayüzü son 24 saatlik özetleri gösterir.

## CI/CD İçin Sistem Bağımlılıkları

WeasyPrint ve PDF çıktıları için GitHub Actions veya Docker imajlarında aşağıdaki paketlerin yüklü olduğundan emin olun:

```bash
apt-get update && apt-get install -y \
  libcairo2 \
  libpango-1.0-0 \
  libpangoft2-1.0-0 \
  libffi-dev \
  libjpeg-dev \
  libxml2 \
  libxslt1.1
```

Servis çalışanı ve PWA manifesti `static/js/service-worker.js` ile senkronize edildiğinden, statik varlıkları güncelledikten sonra cache ismini (`finasis-cache-vX`) artırmayı unutmayın.

## CI Pipeline (GitHub Actions)

- Otomatik pipeline `/.github/workflows/ci.yml` dosyasında tanımlıdır; `main` ve `develop` branch'lerine push, tüm pull request'ler için tetiklenir.
- **Lint jobu:** `ruff` ve `black` ile stil kontrolü. Yerelde `pip install ruff black` ardından `ruff check .` ve `black --check .` komutlarını çalıştırabilirsiniz.
- **Tests jobu:** `pytest` + `coverage` ile Django testleri çalışır, HTML ve XML coverage raporları artefact olarak saklanır. Yerelde `coverage run -m pytest` ardından `coverage html` komutları aynı çıktıyı üretir.
- **Security jobu:** `bandit` kaynak kod taraması ve `pip-audit` bağımlılık güvenlik raporu üretir. Rapor pipeline sonunda artefact olarak indirilebilir.
- Dependabot konfigürasyonu (`.github/dependabot.yml`) haftalık olarak pip ve GitHub Actions güncellemelerini takip eder.

## Gözlemlenebilirlik

- **Sentry:** `SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_TRACES_SAMPLE_RATE`, `SENTRY_PROFILES_SAMPLE_RATE` değişkenlerini tanımlayın. Varsayılan olarak PII maskeleme aktif, log seviyesinden `error` ve üzeri olaylar Sentry’ye gönderilir.
- **Prometheus:** `django-prometheus` entegrasyonu sayesinde `/metrics` endpoint’i hazırdır. Ingress/Nginx tarafında temel kimlik doğrulama veya IP kısıtlaması tanımlamanız önerilir.
- **JSON logları:** `DJANGO_ENABLE_JSON_LOGS=True` ile loglar `common.logging.JsonFormatter` üzerinden maskelenmiş ve yapılandırılmış olarak stdout’a yazılır; Fluent Bit / OpenSearch pipeline’ına uygun format.
- **Görev ve metrikler:** Developer API istekleri Prometheus metrikleri (`finasis_api_calls_total`, `finasis_api_call_latency_seconds`) üzerinden takip edilir; görev motoru YAML kataloğu ile AI/gamification görevleri yönetilir.

## Çoklu Dil (i18n)

- Varsayılan diller `settings.LANGUAGES` altında tanımlıdır (TR, EN, DE, ES, AR). Navbar’da yer alan dil anahtarı `available_languages` context değişkeni ile doldurulur.
- Dil değişimi `set_language` view’i üzerinden yapılır; POST isteğinde `language` ve `next` parametreleri kullanılır.
- Yeni çeviri eklemek için:

```bash
django-admin makemessages -l en -l de
django-admin compilemessages
```

- Örnek çeviri dosyaları `locale/<lang>/LC_MESSAGES/django.po` altında tutulur.

## Globalleşme & Fiyatlandırma

- Desteklenen diller: `LANGUAGES` listesi Türkçe, İngilizce, Almanca, İspanyolca ve Arapça olarak genişletildi.
- Bölgesel fiyat parametreleri: `FINASIS_SUPPORTED_REGIONS`, `FINASIS_DEFAULT_REGION` ve `REGIONAL_PRICING` sözlüğü (TRY/EUR/USD/APAC) ile çevresel olarak yönetilir.
- Yeni checklist’ler: `eu_gdpr.yml` ve `us_finreg.yml` profilleri `manage.py compliance_check` komutu ile çalıştırılabilir.
- Marketplace & Academy sayfaları resource hub üzerinden erişilebilir (`/resources/academy/`, `/resources/developer-hub/`, `/resources/partner-marketplace/`).

