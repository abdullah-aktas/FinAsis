# FinAsis - Finansal Yönetim ve Asistan Platformu

![FinAsis Logo](static/img/logo.png)

FinAsis, işletmelerin finansal yönetim, müşteri ilişkileri ve stok yönetimi süreçlerini dijitalleştirmesine yardımcı olan kapsamlı bir yazılım çözümüdür. Hem web uygulaması hem de masaüstü uygulaması olarak kullanılabilir.

## Özellikler

- **Muhasebe Yönetimi**: Hesap planı, faturalar, yevmiye kayıtları, vergi beyannameleri
- **Müşteri İlişkileri (CRM)**: Müşteri yönetimi, fırsat takibi, aktivite planlaması
- **E-Belge Entegrasyonu**: E-Fatura, E-Arşiv Fatura, E-İrsaliye ve E-Defter oluşturma ve yönetme
- **Stok Yönetimi**: Ürün kataloğu, stok giriş/çıkış işlemleri, sayım
- **Raporlama ve Analitik**: Mali tablolar, performans analizleri, iş zekası, özelleştirilebilir dashboardlar
- **Yapay Zeka Asistanı**: Nakit akışı tahmini, müşteri risk skorlaması, OCR ile belge işleme
- **Sanal Şirket Simülasyonu**: Eğitim amaçlı sanal şirket oluşturma ve yönetme
- **Progressive Web App (PWA)**: Çevrimiçi/çevrimdışı çalışma modu, mobil uyumlu arayüz
- **Çoklu Dil Desteği**: Türkçe, İngilizce, Kürtçe, Arapça ve Almanca dil desteği
- **Güvenlik ve Kimlik Doğrulama**: JWT tabanlı kimlik doğrulama, 2FA desteği, rate limiting

## Kurulum

### Gereksinimler

- Python 3.9 veya üzeri
- pip (Python paket yöneticisi)
- PostgreSQL 13+ (önerilen) veya SQLite
- Node.js 14+ ve npm 6+
- Redis 6+ (görev kuyruğu için)
- Docker & Docker Compose (opsiyonel)

### Web Uygulaması

1. Projeyi klonlayın:
```bash
git clone https://github.com/finasis/finasis.git
cd finasis
```

2. Sanal ortam oluşturun ve etkinleştirin:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
npm install
```

4. Ortam değişkenlerini ayarlayın:
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

5. Veritabanını oluşturun:
```bash
python manage.py migrate
```

6. Yönetici kullanıcısı oluşturun:
```bash
python manage.py createsuperuser
```

7. Statik dosyaları toplayın:
```bash
python manage.py collectstatic
```

8. Geliştirme sunucusunu başlatın:
```bash
python manage.py runserver
```

9. Tarayıcınızda `http://127.0.0.1:8000` adresine giderek uygulamayı görüntüleyin.

### Docker ile Kurulum

```bash
# Geliştirme ortamı
docker-compose up -d

# Üretim ortamı
docker-compose -f docker-compose.prod.yml up -d
```

### Masaüstü Uygulaması

#### Windows
```bash
scripts\build_and_run.bat
```

#### Linux/macOS
```bash
chmod +x scripts/build_and_run.sh
./scripts/build_and_run.sh
```

## Dokümantasyon

Detaylı dokümantasyon için `docs/` dizinine bakın:

- [Kurulum ve Geliştirme](docs/01_kurulum_ve_gelistirme.md) - Kurulum ve geliştirme ortamı hazırlama
- [Veritabanı ve Altyapı](docs/02_veritabani_ve_altyapi.md) - Veritabanı yapısı ve yönetimi
- [AI Assistant Modülü](docs/03_ai_assistant.md) - Yapay zeka özellikleri
- [E-Belge Sistemi](docs/04_edocument.md) - E-Fatura, E-İrsaliye ve E-Defter
- [Analytics & Dashboard](docs/05_analytics.md) - Raporlama ve analiz özellikleri
- [PWA ve Çevrimdışı Kullanım](docs/06_pwa.md) - Progressive Web App özellikleri
- [Dil ve Yerelleştirme](docs/07_i18n.md) - Çoklu dil desteği
- [CI/CD Süreçleri](docs/08_cicd.md) - Sürekli entegrasyon ve dağıtım
- [Güvenlik ve Kimlik Doğrulama](docs/09_security.md) - Güvenlik özellikleri
- [Kullanım Kılavuzu](docs/user_manual_tr.md) - Kullanıcılar için rehber
- [Geliştirici Rehberi](docs/developer_guide_tr.md) - Geliştiriciler için teknik dokümantasyon
- [API Dokümantasyonu](docs/api_documentation.md) - API kullanımı
- [Dağıtım Kılavuzu](docs/deployment_guide.md) - Üretim ortamına dağıtım
- [Sürüm Notları](docs/release_notes.md) - Sürüm değişiklikleri

## Katkıda Bulunma

Projeye katkıda bulunmak isteyenler için adımlar:

1. Projeyi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## İletişim

- Proje Websitesi: [https://finasis.com.tr](https://finasis.com.tr)
- E-posta: [info@finasis.com.tr](mailto:info@finasis.com.tr)
- Twitter: [@FinAsisTR](https://twitter.com/FinAsisTR)
- LinkedIn: [FinAsis](https://www.linkedin.com/company/finasis/)