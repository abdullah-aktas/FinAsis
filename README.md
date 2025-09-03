# FinAsis – Geleceğin Finansal Asistanı 🧠📊

**FinAsis**, KOBİ'ler ve bireyler için finansal yönetim, eğitim, oyunlaştırma ve yapay zeka destekli analizler sunan modern bir platformdur. Muhasebe, finansal okuryazarlık, simülasyon, oyun ve blockchain tabanlı şeffaf kayıt sistemleriyle öne çıkar.

---

## 🚀 Temel Özellikler

- **KOBİ Finans Yönetimi:** Gelir/gider takibi, fatura, stok, cari hesaplar
- **Yapay Zeka Destekli Danışman:** Otomatik analiz, risk ve kârlılık değerlendirmesi, öneri sistemleri
- **FinEd Eğitim Modülü:** Finansal okuryazarlık eğitimi, testler, oyunlaştırılmış öğrenme
- **FinGame:** 3D muhasebe oyunu, şirket kurma ve yönetme simülasyonu
- **Blockchain Entegrasyonu:** Şeffaf, güvenli ve değiştirilemez finansal kayıtlar, NFT destekli rozet/sertifika sistemi
- **Çoklu Dil Desteği:** Türkçe, İngilizce, Almanca, Fransızca, Arapça, Kürtçe ve daha fazlası
- **Modern Arayüz:** Responsive, koyu/açık tema, erişilebilirlik (A11y), gelişmiş grafikler

---

## 🏗️ Ana Modüller

- **accounting:** Temel muhasebe işlemleri (fatura, gider, banka, ürün, satış, ödeme)
- **accounts:** Kullanıcı, şirket, başarımlar, ayarlar
- **games:** Oyunlar ve simülasyonlar (3D oyun, görevler, skorlar)
- **ai_assistant:** Akıllı asistan, ML API'leri, öneri ve analizler
- **blockchain:** Blokzincir entegrasyonları
- **finance:** Banka, e-fatura, çek/senet, finansal raporlama
- **education:** Finansal eğitim, interaktif senaryolar
- **virtual_company:** Sanal şirket yönetimi
- **common:** Ortak izinler, mixinler, templatetag'ler

---

## 🌐 Çoklu Dil (i18n) ve Yerelleştirme Desteği

FinAsis, hem arayüzde hem de API/servislerde kapsamlı çoklu dil ve yerelleştirme (i18n) desteği sunar.

- **Desteklenen Diller:** Türkçe (tr), İngilizce (en), Almanca (de), Fransızca (fr), Arapça (ar), Kürtçe (ku)
- **Backend (Django):**
  - Tüm metinler .po/.mo dosyaları ile çevrilebilir.
  - Django'nun klasik i18n altyapısı kullanılır.
  - Yeni dil eklemek için:
    ```bash
    django-admin makemessages -l yeni_dil
    django-admin compilemessages
    ```
- **Frontend (JS):**
  - Tüm arayüz metinleri `static/locales/` altında JSON dosyalarında yönetilir.
  - Dinamik dil seçici ile kullanıcı arayüzü anında değişir.
  - RTL (sağdan sola) diller (Arapça, Kürtçe-Sorani) için tam destek.
  - Tarih, saat, para birimi ve sayı formatları otomatik olarak yerelleştirilir.
- **Oyun ve Simülasyonlar:**
  - 3D oyun modüllerinde de çoklu dil desteği ve anlık dil değişimi mevcuttur.
- **Dil Seçici:**
  - Tüm sayfalarda erişilebilir bir dil seçici bulunur.
  - Kullanıcı tercihi localStorage'da saklanır ve sonraki ziyaretlerde otomatik olarak uygulanır.
- **Çeviri Güncelleme:**
  - Backend ve frontend çevirileri arasında tutarlılık sağlanır.
  - JSON veya .po dosyalarını güncelledikten sonra ilgili servisi yeniden başlatmak yeterlidir.

**Not:** Yeni bir dil eklemek veya mevcut çevirileri güncellemek için `FinAsis/apps/locale/README.md` dosyasındaki adımları takip edebilirsiniz.

---

## 🛠️ Kurulum

1. Depoyu klonlayın:
   ```bash
   git clone <repo-url>
   cd FinAsis
   ```
2. Sanal ortamı oluşturun ve aktif edin:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```
3. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
4. Ortam değişkenlerini ayarlayın:
   `.env` dosyasını oluşturun ve gerekli değişkenleri girin.

## Veritabanı Kurulumu
```bash
python manage.py migrate
```

## Testler
```bash
pytest --cov=FinAsis --cov-report=term-missing
```

## Kod Kalitesi
```bash
flake8 .
black --check .
```

## Deploy
- Otomatik deploy için `.github/workflows/deploy.yml` kullanılır.
- Manuel deploy için:
  ```bash
  git pull origin main
  source venv/bin/activate
  pip install -r requirements.txt
  python manage.py collectstatic --noinput
  python manage.py migrate --noinput
  sudo systemctl restart finasis_gunicorn
  ```

## Katkı
Pull request göndermeden önce testleri ve lint işlemlerini çalıştırın.

## Lisans
MIT

---

## 📘 Muhasebe – Yeni Özellikler ve Komutlar

### Çekirdek
- GL özet tablosu: `GLBalance` (aylık begin/debit/credit/end) – fiş onayında otomatik güncellenir
- JSON kural tabanlı “Muhasebe Motoru”: `PostingRule` → belge satırlarından denklikli `Voucher` üretimi
- Raporlar gerçek veriden: Yevmiye, Kebir, Mizan – `Voucher/VoucherLine/GLBalance` üzerinden

### KDV / Tevkifat / Kur Farkı / Stok
- KDV: `FinAsis/apps/finance/accounting/tax_utils.py`
- Tevkifatlı KDV bölüşümü (satıcı/alıcı payı)
- Kur farkı: `FinAsis/apps/finance/accounting/fx_utils.py`
- FIFO maliyet: `FinAsis/apps/finance/accounting/inventory_fifo.py`

### e‑Belge ve Dönem Sonu
- e‑Fatura outbox ve retry komutları (GİB gönderim akışı şablonu)
- e‑Defter paketleme (stub) komutu
- Dönem sonu stub komutu (amortisman/reeskont/kur değerleme fişi)

### Çift Onay
- `Voucher.post` üzerinde basit çift onay örneği: toplam > 100.000 ise `reference` içinde `APPROVED2` anahtarı aranır

---

## 🔧 Hızlı Kurulum – Muhasebe Motoru

### 1) Migration ve superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 2) Örnek kural seed et
```bash
python manage.py seed_posting_rules
```

Örnek kural JSON (satış %20):
```json
{
  "condition": { "tax_rate_eq": 0.20 },
  "lines": [
    { "side": "D", "account": "100", "formula": "gross" },
    { "side": "C", "account": "600", "formula": "net" },
    { "side": "C", "account": "391", "formula": "net*tax_rate" }
  ]
}
```

### 3) Belgeyi fişe dönüştürme (programatik)
`FinAsis/apps/finance/accounting/services.py` içindeki `post_document(...)` fonksiyonunu kullanın.

---

## 🧾 Yönetim Komutları (Management Commands)

- e‑Fatura Outbox (ilk göndermeler):
```bash
python manage.py einvoice_outbox
```

- e‑Fatura Retry (hatalıları yeniden dene):
```bash
python manage.py einvoice_retry
```

- Dönem Sonu Stub (amortisman/reeskont/kur değerleme fişi):
```bash
python manage.py run_period_end
```

- e‑Defter Paketleme (stub):
```bash
python manage.py package_edefter --year 2025 --month 6
```

---

## 📊 Rapor ve Ekran Linkleri

- Raporlar ana sayfası: `/finance/reports/`
- Yevmiye: `/accounting/defter/yevmiye/?year=2025&month=6&company=<id>`
- Kebir: `/accounting/defter/kebir/?year=2025&month=6&company=<id>`
- Mizan: `/accounting/defter/mizan/?year=2025&month=6&company=<id>`
- KDV: `/accounting/declarations/kdv/?period=2025-06&company=<id>`
- BA/BS: `/accounting/declarations/babs/?period=2025-06&company=<id>`
- Alacak Yaşlandırma: `/accounting/reports/ar-aging/?company=<id>`


Daha fazla bilgi için kodu inceleyin veya [Yardım ve Dökümantasyon](./FinAsis/templates/help/index.html) sayfasına bakın!

# FinAsis – Geleceğin Finansal Asistanı

## 🚀 Makine Öğrenmesi (ML) API'leri
FinAsis, dünya standartlarında makine öğrenmesi tabanlı API'ler sunar. Tüm ML endpoint'leri JWT/session ile korumalıdır ve Swagger/Redoc ile dokümante edilmiştir.

- **Swagger UI:** `/api/docs/`
- **Redoc:** `/api/redoc/`

### 1. Risk Skoru API
Kullanıcıdan alınan finansal özelliklerle risk skoru hesaplar.

**Endpoint:**
```
POST /ai-assistant/ml/risk-score/
{
  "features": [5.0, 2, 2500.0, 10, 15, 0.3]
}
```
Yanıt:
```
{
  "risk_score": 0.72,
  "model_version": "20240610120000",
  "model_parameters": {"C": 1.0, "max_iter": 1000, ...}
}
```

### 2. Finansal Tahmin API (Prophet)
Geçmiş veriyle ileriye dönük finansal tahmin yapar.

**Endpoint:**
```
POST /ai-assistant/ml/financial-forecast/
{
  "data": [
    {"ds": "2024-01-01", "y": 1000},
    {"ds": "2024-01-02", "y": 1200}
  ],
  "periods": 10
}
```
Yanıt:
```
{
  "dates": [...],
  "predictions": [...],
  "lower_bound": [...],
  "upper_bound": [...],
  "model_version": "20240610120000",
  "model_parameters": {"yearly_seasonality": true, ...}
}
```

### 3. Öneri Sistemi API
Kullanıcı finansal verilerine göre kişiselleştirilmiş öneri üretir.

**Endpoint:**
```
POST /ai-assistant/ml/recommendation/
{
  "income": 10000,
  "expenses": 5000,
  "savings": 2000,
  "goals": "investment"
}
```
Yanıt:
```
{
  "recommendation": "Birikiminizin bir kısmını düşük riskli yatırım araçlarında değerlendirebilirsiniz.",
  "model_version": "v1.0.0",
  "model_parameters": {"type": "rule-based", "rules": 5}
}
```

### Frontend Entegrasyonu
Tüm ML API'leri, ilgili template dosyalarında AJAX ile entegre edilmiştir. Sonuçlar kullanıcıya anında ve kullanıcı dostu şekilde gösterilir.

### Test ve Kalite
- Tüm ML API'leri için pytest tabanlı otomatik testler hazırdır.
- Kodlar PEP8 ve modern Python standartlarına uygundur.

---

## Proje Amacı
FinAsis, şirketler ve bireyler için finansal işlemleri kolaylaştıran, raporlama, oyunlaştırma ve yapay zeka destekli analizler sunan modern bir finansal asistan ve yönetim platformudur.

## Hızlı Başlangıç
1. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
2. Veritabanını oluşturun:
   ```bash
   python manage.py migrate
   ```
3. Süper admin (yönetici) hesabı oluşturun:
   ```bash
   python manage.py createsuperuser
   ```
   Komut satırında sizden kullanıcı adı, e-posta ve şifre istenecektir. Bu kullanıcı ile yönetim paneline giriş yapabilirsiniz.
4. Sunucuyu başlatın:
   ```bash
   python manage.py runserver
   ```
5. Testleri çalıştırın:
   ```bash
   python manage.py test
   ```

## Otomatik Test & Kalite
- Her push/pull request'te **GitHub Actions** ile otomatik test ve kod kalite kontrolü (flake8, black) çalışır.
- Tüm kodlar PEP8 uyumlu ve testlerle güvence altındadır.

## API Dokümantasyonu
- Tüm API endpointleri için **Swagger/OpenAPI** dokümantasyonu `/api/docs/` adresindedir.
- DRF ve Redoc desteğiyle kolay entegrasyon.

## Çoklu Dil & Globalizasyon
- Türkçe, İngilizce, Almanca, Fransızca, Arapça, Kürtçe desteği
- Tüm arayüz metinleri `static/locales/` altında JSON dosyalarında yönetilir.
- RTL (sağdan sola) diller için tam destek

## Ana Modüller
- **accounting:** Fatura, gider, banka işlemleri, raporlar
- **accounts:** Kullanıcı, şirket, başarımlar, ayarlar
- **games:** Oyunlar ve simülasyonlar
- **ai_assistant:** Akıllı asistan modülü
- **blockchain:** Blokzincir entegrasyonları
- **finance:** Finansal işlemler, entegrasyonlar ve raporlar
- **education:** Finansal eğitim ve interaktif senaryolar
- **virtual_company:** Sanal şirket yönetimi

## Katkı Kuralları
- Fork'layın, yeni bir branch açın, değişikliklerinizi yapın ve PR gönderin.
- Kodda PEP8 ve Django en iyi uygulamalarına uyun.
- Her yeni özellik için test eklemeye özen gösterin.
- Açık ve anlaşılır commit mesajları kullanın.

## Özellikler
- Modern ve responsive arayüz (Bootstrap 5, koyu/açık tema)
- Çoklu dil desteği ve erişilebilirlik (A11y)
- Gelişmiş grafikler ve raporlar (Chart.js)
- API, webhook, AI öneri ve analiz fonksiyonları
- SEO, PWA, güvenlik ve performans optimizasyonları

## Lisans
MIT

---
Daha fazla bilgi için: [Brand Guide](./config/brand_guide.md) ve [i18n Guide](./config/i18n_guide.md)

## 🌍 Globalization, SEO & Accessibility

### SEO & Social Meta Tags
- All pages include dynamic `<title>`, `<meta name="description">`, Open Graph and Twitter Card tags for multilingual SEO.
- Favicon and manifest are provided for PWA and browser support.
- Language and direction (LTR/RTL) are set automatically based on user selection.

### Internationalization (i18n)
- All UI texts are managed via JSON files under `static/locales/` (tr, en, de, fr, ar, ku).
- Language selector dropdown is available on all pages.
- RTL support for Arabic and other right-to-left languages.
- Date, time, currency and number formats are localized using Intl API helpers.

### Accessibility (A11y)
- High contrast mode, focus styles, color-blind friendly palette.
- Screen reader support with `.sr-only` and skip links.
- All cookie and contrast toggles are translatable and accessible.

### Legal
- GDPR/KVKK/Cookie Policy banners are multilingual and accessible.

### SEO Automation
- `sitemap.xml` covers all main pages and languages for search engines.
- `robots.txt` allows only public pages, blocks API/static/admin, and references sitemap.
- Advanced analytics: Google Analytics 4 and privacy-first Plausible integration (see `static/components/analytics.html`).

### Advanced SEO
- Hreflang tags for all supported languages (tr, en, de, fr, ar, ku) for proper international indexing.
- schema.org microdata (Organization, WebSite, WebPage) in all languages for rich search results.
- Google Tag Manager integration for advanced tracking and marketing tools.

### Extra (Optional)
- **Advanced Analytics:** Hotjar, Matomo (self-hosted) and event tracking infrastructure included. See `static/components/analytics.html`.
- **PWA:** Manifest, service worker, offline support and add-to-home-screen ready. See `static/manifest.json` and `static/js/service-worker.js`.
- **Performance:** Lazy load for images, minified assets, CDN usage for Bootstrap, Icons and Fonts.
- **Security:** Content Security Policy (CSP), XSS protection, HTTPS redirect fallback.

---

For more details, see the [Brand Guide](./config/brand_guide.md) and [i18n Guide](./config/i18n_guide.md).

---

**English**

FinAsis is a modern, user-friendly financial assistant and management platform for companies and individuals. It offers financial transactions, reports, gamified modules, and much more.

See above for installation and usage instructions.

# Permissions (RBAC) Modülü

Bu modül, FinAsis projesinde rol tabanlı erişim ve yetkilendirme işlemlerini yönetir. Modern, genişletilebilir ve kullanıcı dostu bir yapıya sahiptir.

## Özellikler
- Soft delete (is_active) desteği
- Django native permission ile tam entegrasyon
- Hiyerarşik rol desteği
- Kullanıcıya doğrudan yetki atama
- Modern DRF API endpoint'leri (filter, search, ordering)
- Kullanıcı dostu admin ve template arayüzü

## Modeller
- **Permission**: Özel yetki modeli, Django Permission ile eşleşir.
- **Role**: Roller, hiyerarşik yapı destekler.
- **UserRole**: Kullanıcı-rol ilişkisi.
- **UserPermission**: Kullanıcıya doğrudan yetki atama.

## API Kullanımı
Tüm endpointler JWT veya session ile kimlik doğrulama gerektirir.

| Endpoint | Açıklama |
|---|---|
| `/api/permissions/` | Yetki CRUD |
| `/api/roles/` | Rol CRUD |
| `/api/user-roles/` | Kullanıcı-rol CRUD |
| `/api/user-permissions/` | Kullanıcıya doğrudan yetki CRUD |

### Örnek: Yetki Oluşturma
```http
POST /api/permissions/
{
  "name": "Rapor Görüntüle",
  "codename": "view_report",
  "content_type": 1,
  "description": "Raporları görüntüleme yetkisi"
}
```

### Örnek: Kullanıcıya Yetki Atama
```http
POST /api/user-permissions/
{
  "user": 5,
  "permission": 12
}
```

## Admin Paneli
- Tüm modellerde soft delete uygulanır (is_active=False olanlar gizlenir).
- Arama, filtreleme ve ilişkili alanlar kolayca yönetilebilir.

## Geliştirici Notları
- Yeni bir Permission oluşturulduğunda, Django native Permission otomatik oluşur.
- API endpoint'lerinde filtering, search ve ordering desteği vardır.
- Tüm template'ler responsive ve kullanıcı dostudur.

---
Daha fazla bilgi için kodu inceleyin veya sorularınızı iletin!

# Virtual Company Modülü

Bu modül, öğrenciler veya kullanıcılar tarafından sanal şirketler oluşturulmasını, ürün ve finansal işlemler yönetilmesini sağlar.

## Özellikler
- Şirket ve ürün yönetimi (CRUD)
- Sadece şirket sahibi kendi şirketini ve ürünlerini görebilir
- API üzerinden toplu ürün ekleme (bulk create)
- Filtering, search, ordering desteği
- Admin panelinde inline ürün yönetimi
- Kullanıcı dostu ve çok dilli hata mesajları

## API Kullanımı
Tüm endpointler JWT veya session ile kimlik doğrulama gerektirir.

| Endpoint | Açıklama |
|---|---|
| `/companies/` | Şirket CRUD |
| `/products/` | Ürün CRUD |
| `/products/bulk_create/` | Toplu ürün ekleme |

### Örnek: Şirket Oluşturma
```http
POST /companies/
{
  "name": "Test Şirket",
  "description": "Açıklama"
}
```

### Örnek: Toplu Ürün Ekleme
```http
POST /products/bulk_create/
{
  "items": [
    {"name": "Ürün 1", "description": "Açıklama", "price": 10, "stock": 5},
    {"name": "Ürün 2", "description": "Açıklama", "price": 20, "stock": 2}
  ]
}
```

## Admin Paneli
- Şirket detayında inline ürün yönetimi
- Gelişmiş arama ve filtreleme

## Test
- pytest ile API endpoint testleri hazırdır.

---
Daha fazla bilgi için kodu inceleyin veya sorularınızı iletin! 