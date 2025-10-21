# FinAsis - Modern Finansal Yönetim Platformu

**Yapay zeka destekli, rol tabanlı finansal yönetim ve eğitim platformu**

---

## 🎯 Proje Amacı

FinAsis, KOBİ'ler ve bireyler için **finansal yönetimi basitleştiren**, **eğitimle destekleyen** ve **oyunlaştırma ile öğretici** hale getiren kapsamlı bir SaaS platformudur.

**Temel Hedefler:**
- Muhasebe ve finans işlemlerini dijitalleştirme
- Finansal okuryazarlığı artırma
- e-Dönüşüm süreçlerini kolaylaştırma (e-Fatura, e-Defter)
- Yapay zeka ile akıllı öneriler sunma
- Oyunlaştırma ile öğrenmeyi eğlenceli hale getirme

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum

```bash
# Projeyi klonlayın
git clone https://github.com/abdullah-aktas/FinAsis.git
cd FinAsis/FinAsis

# Virtual environment oluşturun
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### 2. Veritabanı Kurulumu

```bash
# Migration'ları uygulayın
python manage.py migrate

# Superuser oluşturun
python manage.py createsuperuser
```

### 3. Sunucuyu Başlatın

```bash
python manage.py runserver 0.0.0.0:4747
```

**Tarayıcıda açın:** http://127.0.0.1:4747/

---

## ✨ Ana Özellikler

### 💼 Finansal Yönetim
- ✅ **Muhasebe:** Fatura, gider, ödeme takibi
- ✅ **Finans:** Nakit akışı, bütçe, finansal analiz
- ✅ **Banka Entegrasyonu:** Banka işlemleri takibi
- ✅ **e-Dönüşüm:** e-Fatura, e-Arşiv, e-Defter (GİB uyumlu)
- ✅ **Raporlama:** Yevmiye, kebir, mizan, KDV beyannamesi

### 🤖 Yapay Zeka
- ✅ **Yerel AI Asistan:** Gizlilik odaklı, kendi sunucunuzda
- ✅ **Risk Analizi:** Finansal risk skorlama
- ✅ **Tahminleme:** Gelir/gider tahminleri
- ✅ **Akıllı Öneriler:** Kişiselleştirilmiş finansal öneriler

### 🎓 Eğitim (LMS)
- ✅ **Kurs Yönetimi:** İnteraktif finansal eğitim kursları
- ✅ **Ödev ve Sınav:** Öğrenci performans takibi
- ✅ **Finansal Okuryazarlık:** Muhasebe ve finans eğitimleri

### 🎮 Oyunlaştırma
- ✅ **Finans Simülasyonları:** Trade simulator, bütçe challenge
- ✅ **Başarım Sistemi:** Rozetler ve puan sistemi
- ✅ **Liderlik Tablosu:** Kullanıcılar arası yarışma

### 🔐 Güvenlik & Uyumluluk
- ✅ **Rol Bazlı Erişim:** Her kullanıcı sadece yetkili olduğu işlemleri yapar
- ✅ **Audit Trail:** Tüm işlemler loglanır
- ✅ **KVKK/GDPR:** Gizlilik uyumlu
- ✅ **Blockchain:** İsteğe bağlı blokzincir kanıt sistemi

---

## 🏗️ Teknik Mimari

### Teknoloji Stack
- **Backend:** Django 5.2.7
- **Frontend:** Bootstrap 5.3.3, Vanilla JavaScript
- **Veritabanı:** SQLite (dev), PostgreSQL (production)
- **AI/ML:** Scikit-learn, Prophet (yerel)
- **Task Queue:** Celery + Redis
- **Cache:** File-based (dev), Redis (production)

### Proje Yapısı
```
FinAsis/
├── src/
│   ├── apps/               # Django uygulamaları
│   │   ├── accounting/     # Muhasebe modülü
│   │   ├── finance/        # Finans modülü
│   │   ├── ai_assistant/   # AI asistan
│   │   ├── education/      # LMS modülü
│   │   ├── games/          # Oyunlaştırma
│   │   ├── accounts/       # Kullanıcı yönetimi
│   │   ├── billing/        # Abonelik ve faturalama
│   │   ├── blockchain/     # Blockchain entegrasyonu
│   │   └── common/         # Ortak fonksiyonlar
│   ├── config/             # Proje ayarları
│   ├── static/             # CSS, JS, resimler
│   └── templates/          # HTML template'ler
├── docs/                   # Dokümantasyon
└── requirements.txt        # Python bağımlılıkları
```

---

## 👥 Rol Tabanlı Erişim Kontrolü

### Desteklenen Kullanıcı Rolleri

| Rol | Erişim |
|-----|--------|
| **Yönetici (Admin)** | Tüm modüller + yönetim paneli |
| **KOBİ Sahibi** | Muhasebe, Finans, Raporlar, AI |
| **Muhasebeci** | Muhasebe, Finans, Raporlar |
| **Mali Müşavir** | Muhasebe, Finans, Raporlar, AI |
| **Finans Müdürü** | Finans, Bütçe, Raporlar, AI |
| **Öğretmen** | Eğitim, AI Asistan |
| **Öğrenci** | Eğitim, Oyunlar |
| **Oyuncu** | Oyunlar |

Her kullanıcı **rolüne özel dashboard** ve **menü** görür.

Detaylı bilgi için: `rol_kontrolleri.md`

---

## 🎨 Kullanıcı Arayüzü

### Özellikler
- ✅ **Bootstrap 5.3.3** - Modern, responsive tasarım
- ✅ **Dark Mode** - Koyu/açık tema desteği (Ctrl+D)
- ✅ **Responsive** - Mobil, tablet, desktop uyumlu
- ✅ **Erişilebilirlik** - WCAG AA standartlarında
- ✅ **Çoklu Dil** - Türkçe, İngilizce ve daha fazlası

### Template Sistemi
- **Ana Template:** `templates/core_ui/base.html`
- **Rol Bazlı Header:** `templates/components/header_role_based.html`
- **Rol Bazlı Dashboard:** `templates/dashboard_role_based.html`

---

## 🔧 Yapılandırma

### Environment Variables (.env)
```bash
# Genel Ayarlar
DEBUG=True
SECRET_KEY=your-secret-key-here

# Veritabanı
USE_SQLITE=True
# veya
USE_POSTGRES=True
POSTGRES_DB=finasis
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# AI Settings
AI_LOCAL_ONLY=True
AI_PRIVACY_MODE=True

# e-Dönüşüm (Opsiyonel)
EDOC_SCHEMAS_DIR=/path/to/UBL-TR-schemas
GIB_TEST_MODE=True
GIB_USERNAME=testuser
GIB_PASSWORD=testpass
```

---

## 📊 Veritabanı

### Migration Yönetimi
```bash
# Yeni migration oluştur
python manage.py makemigrations

# Migration'ları uygula
python manage.py migrate

# Belirli app'i migrate et
python manage.py migrate accounting

# Migration geri al
python manage.py migrate accounting 0005
```

### Örnek Veri Yükleme
```bash
# Fixture yükle
python manage.py loaddata fixtures/sample_data.json

# Muhasebe kurallarını yükle
python manage.py seed_posting_rules
```

---

## 🧪 Test

```bash
# Tüm testleri çalıştır
pytest

# Coverage raporu ile
pytest --cov=src --cov-report=html

# Belirli app'i test et
pytest src/apps/accounting/tests/

# Kod kalitesi kontrolü
flake8 src/
black --check src/
```

---

## 📚 API Dokümantasyonu

### API Endpoints
- **Swagger UI:** http://127.0.0.1:4747/swagger/
- **ReDoc:** http://127.0.0.1:4747/redoc/
- **Health Check:** http://127.0.0.1:4747/api/v1/health/

### Örnek AI API Kullanımı

#### Risk Skoru Hesaplama
```bash
curl -X POST http://127.0.0.1:4747/ai-assistant/ml/risk-score/ \
  -H "Content-Type: application/json" \
  -d '{
    "features": [5.0, 2, 2500.0, 10, 15, 0.3]
  }'
```

#### Finansal Tahmin
```bash
curl -X POST http://127.0.0.1:4747/ai-assistant/ml/financial-forecast/ \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"ds": "2024-01-01", "y": 1000},
      {"ds": "2024-02-01", "y": 1200}
    ],
    "periods": 10
  }'
```

---

## 🛠️ Management Commands

### e-Dönüşüm Komutları
```bash
# e-Fatura gönderimi
python manage.py einvoice_outbox

# Hatalı faturaları yeniden dene
python manage.py einvoice_retry

# e-Defter paketi oluştur
python manage.py package_edefter --year 2025 --month 6
```

### Dönem Sonu İşlemleri
```bash
# Amortisman, reeskont, kur farkı hesaplama
python manage.py run_period_end
```

---

## 🌐 Çoklu Dil Desteği

### Desteklenen Diller
- 🇹🇷 Türkçe (tr)
- 🇬🇧 İngilizce (en)
- 🇩🇪 Almanca (de)
- 🇫🇷 Fransızca (fr)
- 🇸🇦 Arapça (ar)

### Yeni Dil Ekleme
```bash
# Çeviri dosyaları oluştur
django-admin makemessages -l es

# Çevirileri derle
django-admin compilemessages
```

---

## 📈 Production Deployment

### Güvenlik Checklist
- [ ] `DEBUG=False` ayarla
- [ ] `SECRET_KEY` değiştir ve güvenli tut
- [ ] `ALLOWED_HOSTS` ayarla
- [ ] HTTPS kullan (SSL sertifikası)
- [ ] PostgreSQL kullan
- [ ] Redis cache kullan
- [ ] Güvenlik headers ayarla
- [ ] Regular backup stratejisi kur

### Docker ile Deploy
```bash
docker-compose up -d
```

### Static Files
```bash
python manage.py collectstatic --noinput
```

---

## 🔐 Güvenlik

- **JWT Authentication:** API güvenliği
- **RBAC:** Rol tabanlı erişim kontrolü
- **CSRF Protection:** Django built-in
- **XSS Protection:** Content Security Policy
- **SQL Injection:** Django ORM ile korumalı
- **Audit Logging:** Tüm kritik işlemler loglanır

---

## 📱 Responsive & PWA

- **Mobil Uyumlu:** Tüm ekranlar responsive
- **Touch Friendly:** 44px minimum touch target
- **PWA Ready:** Progressive Web App desteği
- **Offline Capable:** Temel özellikler offline çalışır

---

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Test yazın ve çalıştırın (`pytest`)
4. Commit yapın (`git commit -m 'feat: add amazing feature'`)
5. Push edin (`git push origin feature/amazing`)
6. Pull Request açın

**Katkı Kuralları:**
- PEP8 kod standardına uyun
- Her yeni özellik için test yazın
- Açıklayıcı commit mesajları kullanın
- Dokümantasyon ekleyin/güncelleyin

---

## 📄 Lisans

Bu proje [MIT lisansı](LICENSE) altında lisanslanmıştır.

---

## 💬 Destek ve İletişim

- **Email:** destek@finasis.com.tr
- **GitHub Issues:** Hata bildirimi ve özellik önerileri
- **Dokümantasyon:** `docs/` klasörü
- **RBAC Kılavuzu:** `rol_kontrolleri.md`

---

## 📊 Proje İstatistikleri

- **Toplam Kod Satırı:** ~50,000+
- **Test Coverage:** ~75%
- **Django Apps:** 25+
- **API Endpoints:** 100+
- **Desteklenen Dil:** 5
- **Responsive:** %100

---

## 🎯 Versiyon Bilgisi

**Versiyon:** 2.0 (Ekim 2025)

### Son Güncellemeler:
- ✅ Rol bazlı erişim kontrolü (RBAC)
- ✅ 254 gereksiz dosya temizlendi
- ✅ CSS optimize edildi (%70 azaltma)
- ✅ Dashboard'lar modernize edildi
- ✅ Bootstrap 5.3.3'e güncellendi
- ✅ Dark mode iyileştirildi
- ✅ Performance optimizasyonu

---

**FinAsis ile finansal dönüşümünüze bugün başlayın!** 🚀
