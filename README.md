# FinAsis ERP

FinAsis ERP, modern ve kullanıcı dostu bir kurumsal kaynak planlama (ERP) sistemidir. Türkiye'ye özgü vergi ve muhasebe kurallarına uygun olarak geliştirilmiş, e-devlet entegrasyonları ile güçlendirilmiş ve mobil uygulama desteği ile zenginleştirilmiş bir çözümdür.

## Özellikler

### Temel Özellikler
- Kullanıcı dostu arayüz
- İki faktörlü kimlik doğrulama
- Veri şifreleme ve güvenlik
- Mobil uygulama desteği
- Gerçek zamanlı bildirimler

### Muhasebe Modülü
- Türkiye'ye özgü vergi hesaplamaları
- KDV, stopaj ve tevkifat hesaplamaları
- E-fatura ve e-arşiv entegrasyonu
- Banka entegrasyonları
- Otomatik raporlama

### CRM Modülü
- Müşteri yönetimi
- Potansiyel müşteri takibi
- Fırsat yönetimi
- Müşteri iletişim geçmişi
- E-posta entegrasyonu

### İK Modülü
- Personel yönetimi
- İzin ve devam takibi
- Performans değerlendirme
- SGK entegrasyonu
- Bordro yönetimi

### Stok Yönetimi
- Stok takibi
- Depo yönetimi
- Sipariş yönetimi
- Tedarikçi yönetimi
- Envanter raporlama

## Kurulum

### Gereksinimler
- Python 3.8+
- Django 4.2+
- PostgreSQL 13+
- Redis 6+

### Kurulum Adımları
1. Sanal ortam oluştur:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Bağımlılıkları yükle:
```bash
pip install -r requirements.txt
```

3. Veritabanını oluştur:
```bash
python manage.py migrate
```

4. Geliştirme sunucusunu başlat:
```bash
python manage.py runserver
```

## Docker ile Kurulum

1. Docker imajını oluştur:
```bash
docker-compose build
```

2. Konteynerleri başlat:
```bash
docker-compose up -d
```

## Mobil Uygulama

FinAsis ERP mobil uygulaması, web uygulamasının tüm özelliklerini mobil cihazlarda kullanmanıza olanak sağlar.

### Özellikler
- Çevrimdışı çalışma
- Anlık bildirimler
- QR kod ile hızlı giriş
- Biyometrik kimlik doğrulama
- Veri senkronizasyonu

## Güvenlik

FinAsis ERP, en son güvenlik standartlarını kullanarak verilerinizi korur:

- İki faktörlü kimlik doğrulama
- Veri şifreleme
- Güvenlik duvarı
- DDoS koruması
- Düzenli yedekleme

## E-Devlet Entegrasyonları

- Vergi borcu sorgulama
- SGK bilgileri sorgulama
- Firma bilgileri sorgulama
- E-fatura entegrasyonu
- E-arşiv entegrasyonu

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## İletişim

- E-posta: info@finasis.com
- Web: https://www.finasis.com
- Telefon: +90 212 123 45 67

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir özellik dalı oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Dalınıza push edin (`git push origin feature/yeni-ozellik`)
5. Bir Pull Request oluşturun

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

## İletişim

- Proje Websitesi: [https://finasis.com.tr](https://finasis.com.tr)
- E-posta: [info@finasis.com.tr](mailto:info@finasis.com.tr)
- Twitter: [@FinAsisTR](https://twitter.com/FinAsisTR)
- LinkedIn: [FinAsis](https://www.linkedin.com/company/finasis/)

## CI/CD ve Canlıya Alım Rehberi

Bu rehber, FinAsis projesinin sürekli entegrasyon (CI), sürekli dağıtım (CD) ve canlıya alım süreçlerini açıklamaktadır.

### 1. CI/CD İş Akışları

Projede iki farklı CI/CD iş akışı bulunmaktadır:

#### 1.1. `.github/workflows/ci-cd.yml`

Bu iş akışı aşağıdaki adımları içerir:

- **test**: Python ve Node.js ile testler, güvenlik kontrolleri, linting ve kalite kontrolleri
- **deploy-staging**: Test aşaması başarılı olduğunda, `develop` dalı değişikliklerini staging ortamına dağıtır
- **deploy-production**: Test aşaması başarılı olduğunda, `main` dalı değişikliklerini production ortamına dağıtır
- **rollback**: Production dağıtımı başarısız olduğunda, otomatik geri alma gerçekleştirir

#### 1.2. `.github/workflows/django-deploy.yml`

Bu iş akışı aşağıdaki adımları içerir:

- **test**: Django uygulaması için test, güvenlik kontrolleri ve kalite kontrolleri
- **build-and-push**: Docker imajları oluşturur ve Docker Hub'a gönderir
- **deploy**: Production ortamına dağıtım yapar

### 2. Dependabot Yapılandırması

`.github/dependabot.yml` dosyası, aşağıdaki paket ekosistemlerini haftalık olarak takip eder:

- npm (JavaScript bağımlılıkları)
- pip (Python bağımlılıkları)
- docker (Docker imajları)
- github-actions (GitHub Actions iş akışları)

Tüm güncellemeler `develop` dalına gönderilir.

### 3. Monitoring ve Alarmlar

`monitoring/grafana/provisioning/alerting/rules.yml` dosyası, Grafana için alarm kurallarını içerir:

- Yüksek CPU kullanımı
- Yüksek bellek kullanımı
- Yüksek gecikme süresi
- Yüksek hata oranı
- Servis durumları

### 4. Canlıya Alım Süreci

#### 4.1. Geliştirme Aşaması

1. Yeni özellikler için feature branch oluşturun: `git checkout -b feature/yeni-ozellik`
2. Değişikliklerinizi yapın ve testleri çalıştırın
3. Değişikliklerinizi commit edin ve push edin: `git push origin feature/yeni-ozellik`
4. GitHub'da bir Pull Request (PR) oluşturun (`develop` dalına hedefleyin)
5. CI testlerinin geçtiğinden emin olun
6. PR'ı birleştirin

#### 4.2. Staging'e Dağıtım

1. `develop` dalındaki değişiklikler CI/CD pipeline tarafından otomatik olarak staging ortamına dağıtılır
2. Staging ortamında manuel testler yapın: `https://staging.finasis.com.tr`

#### 4.3. Production'a Dağıtım

1. Staging ortamında testler başarılı olduğunda, `develop` dalından `main` dalına PR oluşturun
2. CI testlerinin geçtiğinden emin olun
3. PR'ı birleştirin
4. `main` dalındaki değişiklikler CI/CD pipeline tarafından otomatik olarak production ortamına dağıtılır
5. Production ortamını kontrol edin: `https://finasis.com.tr`

#### 4.4. Acil Durum Müdahalesi

Hızlı düzeltme (hotfix) gerektiren acil durumlar için:

1. `main` dalından bir hotfix branch oluşturun: `git checkout -b hotfix/acil-duzeltme`
2. Düzeltmeyi yapın ve testleri çalıştırın
3. Değişikliklerinizi commit edin ve push edin: `git push origin hotfix/acil-duzeltme`
4. `main` dalına PR oluşturun ve birleştirin
5. Daha sonra düzeltmenin `develop` dalına da entegre edildiğinden emin olun

#### 4.5. Rollback Prosedürü

Production dağıtımı başarısız olduğunda otomatik rollback gerçekleşir. Manuel rollback için:

```bash
cd /opt/finasis
./scripts/rollback.sh [YEDEK_TARIH] [SLACK_WEBHOOK_URL]
```

### 5. Ortam Değişkenleri

GitHub Secrets'ta aşağıdaki değişkenlerin yapılandırıldığından emin olun:

- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Veritabanı bilgileri
- `DJANGO_SECRET_KEY`: Django gizli anahtarı
- `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`: Docker Hub kimlik bilgileri
- `PROD_HOST`, `PROD_USER`, `PROD_KEY`: Production sunucu bilgileri
- `PROD_URL`: Production URL
- `SLACK_WEBHOOK`: Slack bildirimleri için webhook URL
- `SONAR_TOKEN`, `SONAR_HOST_URL`: SonarQube kimlik bilgileri
- `STAGING_HOST`, `STAGING_USERNAME`, `STAGING_SSH_KEY`: Staging sunucu bilgileri

### 6. Performans İzleme

Grafana ve Prometheus ile sistem performansını izleyebilirsiniz:
- Grafana: `https://monitoring.finasis.com.tr`
- Prometheus: `https://prometheus.finasis.com.tr`

### 7. Sorun Giderme

- CI/CD hataları için GitHub Actions sekmesini kontrol edin
- Uygulama logları: `/var/www/finasis/logs/` dizininde bulunur
- Veritabanı yedekleri: `/var/www/finasis/` dizininde `backup_YYYYMMDD_HHMMSS.sql` formatında saklanır
