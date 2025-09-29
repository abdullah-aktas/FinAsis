<<<<<<< HEAD
<div align="center">
  <h1>FinAsis – Geleceğin Finansal Asistanı 🧠📊</h1>
  <p><strong>KOBİ'ler, bireyler ve öğrenciler için finansal yönetim, muhasebe, eğitim (FinEd), oyunlaştırma (FinGame), yapay zeka destekli analizler ve blockchain tabanlı şeffaf kayıt altyapısı.</strong></p>
  <p>
    <em>All key sections below • English summary at the end</em>
  </p>
</div>

---

## 📑 İçindekiler
1. [Genel Bakış](#-genel-bakış)
2. [Öne Çıkan Özellikler](#-öne-çıkan-özellikler)
3. [Mimari ve Modüller](#-mimari-ve-modüller)
4. [Kurulum (Hızlı)](#-kurulum-hızlı)
5. [Ortam Değişkenleri (.env Örneği)](#-ortam-değişkenleri-env-örneği)
6. [Hızlı Başlangıç Adımları](#-hızlı-başlangıç-adımları)
7. [Test & Kod Kalitesi](#-test--kod-kalitesi)
8. [Muhasebe Motoru (Çekirdek)](#-muhasebe-motoru-çekirdek)
9. [Yönetim Komutları](#-yönetim-komutları)
10. [Rapor URL'leri](#-rapor-urlleri)
11. [Makine Öğrenmesi (ML) API'leri](#-makine-öğrenmesi-ml-apileri)
12. [RBAC / Permissions Modülü](#-rbac--permissions-modülü)
13. [Virtual Company Modülü](#-virtual-company-modülü)
14. [Çoklu Dil • i18n • SEO • A11y](#-çoklu-dil--i18n--seo--a11y)
15. [Blockchain & Güvenlik](#-blockchain--güvenlik)
16. [Deploy](#-deploy)
17. [Katkı Rehberi](#-katkı-rehberi)
18. [Lisans](#-lisans)
19. [English Summary](#english-summary)

---

## 🌍 Genel Bakış
**FinAsis**, muhasebe & finansal okuryazarlığı hem işletmelere hem bireylere öğreten; **oyunlaştırma**, **AR/3D**, **yapay zeka destekli öneri & risk analizi**, **blockchain ile değiştirilemez kayıt**, **çoklu dil**, **PWA + SEO + erişilebilirlik** yetenekleriyle bütünleşik bir platformdur.

> Hedef: Finansal karar alma kalitesini artırmak, eğitimle beceri geliştirmek ve operasyonel finans/muhasebe süreçlerini otomatikleştirmek.

---

## 🚀 Öne Çıkan Özellikler
- 💼 KOBİ Finans & Muhasebe (fatura, cari, stok, banka, vergi, raporlar)
- 🧠 Yapay Zeka Destekli Analiz & Öneri (risk skoru, tahmin, tavsiye)
- 🎓 FinEd Eğitim Modülü (senaryo, quiz, seviye, rozet)
- 🕹️ FinGame (3D şirket simülasyonu, görevler, skorlar)
- 🔗 Blockchain Entegrasyonu (şeffaflık, denetlenebilirlik, NFT rozet/sertifika)
- 🌐 Çoklu Dil & RTL Desteği (tr, en, de, fr, ar, ku ...)
- 🧩 Modüler Yapı & Genişletilebilir API (DRF + JWT)
- 📊 Gerçek Zamanlı Raporlama (yevmiye, kebir, mizan, KDV, BA/BS, yaşlandırma)
- 📦 Muhasebe Motoru (JSON kural tabanlı otomatik fiş üretimi)
- ♻️ Çift Onay / Workflow Kancaları
- 🔐 RBAC (Rol & Yetki Hiyerarşisi)
- 🪪 PWA, SEO, A11y, Performans & Güvenlik optimizasyonları

---

## 🏗️ Mimari ve Modüller
| Modül | Amaç | Örnek İçerik |
|-------|------|--------------|
| `accounting` | Fişler, hesap planı, vergi, envanter | Voucher, GLBalance, PostingRule |
| `finance` | Banka, e-fatura, çek/senet, raporlar | Entegrasyon & mutabakat |
| `ai_assistant` | ML/AI endpointleri, risk, tahmin, öneri | `/ai-assistant/ml/*` |
| `education` | Eğitim içerikleri & quizler | Senaryo, quiz API |
| `games` | 3D / simülasyon | Görevler, skorlar |
| `virtual_company` | Sanal şirket & ürün yönetimi | CRUD + bulk işlemler |
| `accounts` | Kullanıcı, şirket, başarımlar | Profil, ayarlar |
| `blockchain` | Kayıt doğrulama & NFT | Hashing, işaretleme |
| `common` | Ortak util, templatetag, mixin | Base sınıflar |
| `rbac/permissions` | Rol & yetki sistemi | Role, Permission, UserRole |

---

## 🛠️ Kurulum (Hızlı)
```bash
git clone <repo-url>
cd FinAsis
python -m venv .venv
.venv\Scripts\activate          # Windows
# veya (Linux/Mac)  source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Alternatif (Make / Task Runner varsa)
```bash
invoke setup   # örnek: bağımlılık + migrate + collectstatic
```

---

## 🔐 Ortam Değişkenleri (.env Örneği)
```dotenv
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=change_me
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
DEFAULT_LANGUAGE=tr
ENABLE_BLOCKCHAIN=true
AI_RISK_MODEL_VERSION=20240610120000
```
Ek değişkenler için `settings.py` içinde yorumlara bakın.

---

## ⚡ Hızlı Başlangıç Adımları
1. Bağımlılıkları kur (yukarıdaki adımlar)
2. `python manage.py migrate`
3. `python manage.py createsuperuser`
4. (Opsiyonel) Örnek kural & test verisi: `python manage.py seed_posting_rules`
5. Sunucu: `python manage.py runserver`
6. Swagger: `http://127.0.0.1:8000/api/docs/`

---

## ✅ Test & Kod Kalitesi
```bash
pytest -q --maxfail=1
pytest --cov=FinAsis --cov-report=term-missing
flake8 .
black --check .
isort --check-only .
```
CI (GitHub Actions) push/PR üzerinde otomatik çalıştırır.

---

## 🧾 Muhasebe Motoru (Çekirdek)
Özellikler:
- `PostingRule` → Belge satırlarından dinamik `Voucher` üretimi (JSON kural)
- `GLBalance` → Aylık begin/debit/credit/end otomatik güncelleme (fiş post)
- Raporlar: Yevmiye, Kebir, Mizan gerçek veri tablosundan
- FIFO stok maliyet, kur farkı, KDV & tevkifat yardımcıları
- Çift Onay: Toplam > eşik ise `reference` içinde `APPROVED2` aranır

Örnek kural (satış %20 KDV):
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
Programatik kullanım: `post_document(...)` (bkz. `finance/accounting/services.py`).

---

## 🛎️ Yönetim Komutları
| Komut | Amaç |
|-------|------|
| `einvoice_outbox` | e‑Fatura ilk gönderimler |
| `einvoice_retry` | Hatalı e‑fatura tekrar denemesi |
| `run_period_end` | Dönem sonu (amortisman / reeskont / kur değerleme stub) |
| `package_edefter --year Y --month M` | e‑Defter paket stub |
| `seed_posting_rules` | Örnek muhasebe kuralı yükler |

---

## 📊 Rapor URL'leri
| Rapor | Örnek URL |
|-------|-----------|
| Ana sayfa | `/finance/reports/` |
| Yevmiye | `/accounting/defter/yevmiye/?year=2025&month=6&company=<id>` |
| Kebir | `/accounting/defter/kebir/?year=2025&month=6&company=<id>` |
| Mizan | `/accounting/defter/mizan/?year=2025&month=6&company=<id>` |
| KDV | `/accounting/declarations/kdv/?period=2025-06&company=<id>` |
| BA/BS | `/accounting/declarations/babs/?period=2025-06&company=<id>` |
| Alacak Yaşlandırma | `/accounting/reports/ar-aging/?company=<id>` |

---

## 🤖 Makine Öğrenmesi (ML) API'leri
Swagger: `/api/docs/` • Redoc: `/api/redoc/`

1. Risk Skoru
```http
POST /ai-assistant/ml/risk-score/
{ "features": [5.0, 2, 2500.0, 10, 15, 0.3] }
```
Yanıt: `{ "risk_score": 0.72, "model_version": "20240610120000" }`

2. Finansal Tahmin (Prophet)
```http
POST /ai-assistant/ml/financial-forecast/
{ "data": [{"ds": "2024-01-01", "y": 1000}], "periods": 10 }
```

3. Öneri Sistemi
```http
POST /ai-assistant/ml/recommendation/
{ "income": 10000, "expenses": 5000, "savings": 2000, "goals": "investment" }
```

Tüm endpointler JWT veya session auth ile korunur. Pytest senaryoları hazırdır.

---

## 🛡️ RBAC / Permissions Modülü
Özellikler: Soft delete, hiyerarşik rol, direkt kullanıcı yetkisi, DRF filtering/search/ordering.

API (örn.):
| Endpoint | İşlev |
|----------|-------|
| `/api/permissions/` | Permission CRUD |
| `/api/roles/` | Rol CRUD |
| `/api/user-roles/` | Kullanıcı-rol |
| `/api/user-permissions/` | Kullanıcıya doğrudan yetki |

Örnek Yetki:
```http
POST /api/permissions/
{ "name": "Rapor Görüntüle", "codename": "view_report", "content_type": 1 }
```

---

## 🏢 Virtual Company Modülü
Özellikler: Şirket & ürün CRUD, bulk create, sahiplik kontrolü, arama & filtre.

Bulk Örnek:
```http
POST /products/bulk_create/
{
  "items": [
    {"name": "Ürün 1", "price": 10, "stock": 5},
    {"name": "Ürün 2", "price": 20, "stock": 2}
  ]
}
```

---

## 🌐 Çoklu Dil • i18n • SEO • A11y
- Diller: tr, en, de, fr, ar (RTL), ku
- Backend: `django-admin makemessages -l <lang> && django-admin compilemessages`
- Frontend: `static/locales/<lang>/*.json`
- Hreflang, schema.org microdata, Open Graph & Twitter Card otomatik
- Erişilebilirlik: Kontrast modu, screen reader etiketleri, skip linkler
- PWA: Manifest + service worker + offline stratejisi
- Analytics: GA4 / Plausible / (opsiyonel) Hotjar / Matomo

---

## 🔗 Blockchain & Güvenlik
- Hash tabanlı doğrulanabilir finansal kayıt
- NFT rozet / sertifika konsepti (genişletilebilir)
- CSP, XSS korumaları, HTTPS yönlendirme fallback
- Yetki katmanları + audit log (geliştirilebilir)

---

## 🚀 Deploy
Örnek manuel süreç:
```bash
git pull origin main
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py check --deploy
sudo systemctl restart finasis_gunicorn   # (Linux örneği)
```
CI/CD: `.github/workflows/` altında (varsa) otomasyon.

---

## 🤝 Katkı Rehberi
1. Fork + branch: `feature/<özellik-adı>`
2. Test ekle/güncelle
3. Lint & format: black, isort, flake8
4. Anlamlı commit mesajları (Conventional önerilir)
5. PR açıklamasında: Amaç + Özet + Test kapsamı

Geliştirme sırasında ek öneriler:
- Yeni model → sinyal + admin kaydı + test
- Yeni API → swagger şeması + izin kontrolü + negatif test

---

## 📄 Lisans
MIT – Ayrıntılar için `LICENSE` dosyasına bakın.

---

## English Summary
FinAsis is a modular financial management, education, gamification and AI analytics platform for SMEs and individuals. It includes: accounting engine (rule-based voucher posting), finance & reports, AI risk/forecast/recommendation APIs, RBAC, virtual company simulation, multilingual & RTL support, SEO & accessibility optimizations, PWA, and optional blockchain-backed record integrity.

Key Highlights:
- Modular Django + DRF backend
- JSON rule-based accounting posting engine
- ML endpoints (risk score, forecasting, recommendation)
- RBAC with hierarchical roles and direct user permissions
- Virtual company simulation & gamified learning
- Multilingual (tr/en/de/fr/ar/ku) with hreflang & schema.org
- PWA, SEO, Accessibility, Security hardening

See sections above for installation, commands, and API usage.

---
<sub>FinAsis © 2025 – Geliştiriciler ve katkıda bulunanlara teşekkürler.</sub>
>>>>>>> 49574730cf71aa7220e8b73f6183c085f398841c
