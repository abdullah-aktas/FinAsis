# Deploy Klasörü - Script ve Dokümantasyon Rehberi

Bu klasör, FinAsis uygulamasının Cloud Run'a deployment'ı için gerekli script ve dokümantasyonları içerir.

## 🚀 Deployment Scriptleri

### `manual_deploy_cloud_shell.sh` ⭐ **ÖNERİLEN**
**Cloud Shell'de manuel deployment yapmak için kullanın.**
- Secret'ları interaktif olarak alır
- Docker image build eder ve Artifact Registry'ye push eder
- Cloud Run'a deploy eder
- CLOUD_RUN_HOST'u otomatik günceller

**Kullanım:**
```bash
bash deploy/manual_deploy_cloud_shell.sh
```

## 🔍 Kontrol ve Debug Scriptleri

### `check_deployment_status.sh`
**Deployment durumunu detaylı kontrol eder.**
- Son revision bilgisi
- Revision durumu
- Environment variables kontrolü
- Son loglar
- Hata logları

**Kullanım:**
```bash
bash deploy/check_deployment_status.sh
```

### `check_500_error.sh`
**HTTP 500 hatalarını detaylı analiz eder.**
- Son logları kontrol eder
- Exception ve Traceback'leri bulur
- Database bağlantı sorunlarını tespit eder

**Kullanım:**
```bash
bash deploy/check_500_error.sh
```

### `check_health_400.sh`
**Health check endpoint'lerini test eder.**
- `/health/` endpoint'ini test eder
- ALLOWED_HOSTS sorunlarını tespit eder
- CSRF_TRUSTED_ORIGINS kontrolü yapar

**Kullanım:**
```bash
bash deploy/check_health_400.sh
```

### `get_recent_logs.sh`
**Son logları JSON formatından parse ederek gösterir.**
- Son 100 log satırını gösterir
- Önemli mesajları filtreler (ERROR, Exception, Traceback, etc.)

**Kullanım:**
```bash
bash deploy/get_recent_logs.sh
```

## 🗄️ Database Scriptleri

### `check_database_connection.sh`
**Database bağlantısını detaylı kontrol eder.**
- Cloud SQL bağlantı durumu
- Database erişim testi
- Migration durumu
- Tablo varlık kontrolü

**Kullanım:**
```bash
bash deploy/check_database_connection.sh
```

### `quick_check_database.sh`
**Database durumunu hızlıca kontrol eder.**
- Bağlantı testi
- Migration durumu
- Kritik tabloların varlığı

**Kullanım:**
```bash
bash deploy/quick_check_database.sh
```

### `check_and_fix_migrations.sh`
**Migration'ları kontrol eder ve gerekirse çalıştırır.**
- Eksik migration'ları tespit eder
- Migration'ları çalıştırır
- Kritik tabloları doğrular

**Kullanım:**
```bash
bash deploy/check_and_fix_migrations.sh
```

### `fix_database_connection.sh`
**Database bağlantı sorunlarını düzeltmeye çalışır.**
- Cloud SQL proxy kontrolü
- Environment variables kontrolü
- Bağlantı testi

**Kullanım:**
```bash
bash deploy/fix_database_connection.sh
```

## 🔐 Secret ve Güvenlik Scriptleri

### `fix_and_check_secrets.sh`
**Secret'ları kontrol eder ve gerekirse oluşturur.**
- Secret Manager'da secret varlığını kontrol eder
- Eksik secret'ları oluşturur
- Secret değerlerini doğrular

**Kullanım:**
```bash
bash deploy/fix_and_check_secrets.sh
```

### `setup_github_secrets.sh`
**GitHub Secrets'ları ayarlar.**
- Gerekli secret'ları listeler
- Secret oluşturma komutlarını gösterir

**Kullanım:**
```bash
bash deploy/setup_github_secrets.sh
```

### `generate_secret_key.py`
**Django SECRET_KEY oluşturur.**
- Güvenli rastgele SECRET_KEY üretir

**Kullanım:**
```bash
python deploy/generate_secret_key.py
```

## 🔧 Yardımcı Scriptler

### `fix_service_account_permissions.sh`
**Service account izinlerini düzeltir.**
- Gerekli IAM rollerini verir
- Service account'u yapılandırır

**Kullanım:**
```bash
bash deploy/fix_service_account_permissions.sh
```

### `fix_cloud_build_permissions.sh`
**Cloud Build izinlerini düzeltir.**
- Cloud Build API'lerini etkinleştirir
- Gerekli izinleri verir

**Kullanım:**
```bash
bash deploy/fix_cloud_build_permissions.sh
```

### `setup_database_env.sh`
**Database environment variables'ları ayarlar.**
- Cloud Run service'e database env vars ekler

**Kullanım:**
```bash
bash deploy/setup_database_env.sh
```

### `update_trigger_sql.sh`
**Cloud Build trigger'ını günceller.**
- Trigger yapılandırmasını günceller

**Kullanım:**
```bash
bash deploy/update_trigger_sql.sh
```

## 📚 Dokümantasyon

### Deployment Rehberleri

- **`DEPLOY_TO_PRODUCTION.md`** - Production deployment rehberi
- **`GITHUB_ACTIONS_SETUP.md`** - GitHub Actions kurulum rehberi
- **`CLOUD_SHELL_QUICK_DEPLOY.md`** - Cloud Shell hızlı deployment rehberi
- **`SETUP_AUTO_DEPLOYMENT.md`** - Otomatik deployment kurulumu
- **`PRODUCTION_50K_DEPLOYMENT.md`** - 50K kullanıcı için production deployment

### Database Rehberleri

- **`setup_database_connection.md`** - Database bağlantı kurulumu
- **`find_and_setup_secrets.md`** - Secret'ları bulma ve kurulum
- **`EXPORT_IMPORT_GUIDE.md`** - Database export/import rehberi
- **`DUMPDATA_GUIDE.md`** - Django dumpdata rehberi
- **`FIXTURE_DEPLOYMENT_GUIDE.md`** - Fixture deployment rehberi

### Diğer Rehberler

- **`DEPLOY_ALTERNATIVES.md`** - Alternatif deployment yöntemleri
- **`QUOTA_INCREASE_GUIDE.md`** - Quota artırma rehberi
- **`QUICK_START_50K.md`** - 50K kullanıcı için hızlı başlangıç
- **`SITE_HEALTH_CHECK_GUIDE.md`** - Site health check rehberi

## 🐳 Docker ve Container

### `entrypoint.sh`
**Container başlangıç scripti.**
- Database bağlantı testi
- Static dosyaları toplar (collectstatic)
- Migration'ları çalıştırır
- Gunicorn'u başlatır

**NOT:** Bu dosya Dockerfile tarafından kullanılır, manuel çalıştırılmaz.

## 📊 Test ve Monitoring

### `test_health_urls.py`
**Health check URL'lerini test eder.**
- Çeşitli health endpoint'lerini test eder
- Response time ölçer

**Kullanım:**
```bash
python deploy/test_health_urls.py
```

### `load_test_k6.js`
**K6 load test scripti.**
- Yük testi yapar
- Performance metrikleri toplar

**Kullanım:**
```bash
k6 run deploy/load_test_k6.js
```

## ⚙️ Yapılandırma Dosyaları

### `cloud_run/cloudbuild.yaml`
**Cloud Build yapılandırma dosyası.**
- Docker image build süreci
- Artifact Registry push
- Cloud Run deployment

### `production_50k_users.yaml`
**50K kullanıcı için production yapılandırması.**
- Resource limits
- Scaling ayarları
- Environment variables

## 🎯 Hızlı Başlangıç

### İlk Deployment
1. `bash deploy/manual_deploy_cloud_shell.sh` çalıştırın
2. Secret'ları girin
3. Deployment tamamlanmasını bekleyin

### Sorun Giderme
1. `bash deploy/check_deployment_status.sh` - Genel durum kontrolü
2. `bash deploy/check_500_error.sh` - Hata analizi
3. `bash deploy/check_database_connection.sh` - Database kontrolü
4. `bash deploy/get_recent_logs.sh` - Log analizi

### Migration Çalıştırma
```bash
bash deploy/check_and_fix_migrations.sh
```

## ⚠️ Önemli Notlar

1. **Secret'lar:** Asla hardcoded secret kullanmayın! Scriptlerde secret'lar interaktif olarak alınır veya Secret Manager'dan çekilir.

2. **Environment Variables:** Production'da `DJANGO_DEBUG=0` olmalıdır.

3. **Database:** Migration'lar entrypoint.sh tarafından otomatik çalıştırılır. Manuel çalıştırmak için `check_and_fix_migrations.sh` kullanın.

4. **Loglar:** Tüm loglar Cloud Logging'de görüntülenebilir. `get_recent_logs.sh` ile hızlı erişim sağlayın.

5. **Rollback:** Sorun durumunda önceki revision'a dönmek için:
```bash
gcloud run services update-traffic finasis-prod \
  --region=europe-west1 \
  --to-revisions=PREVIOUS_REVISION_NAME=100
```

## 📞 Destek

Sorun yaşarsanız:
1. İlgili check scriptini çalıştırın
2. Logları kontrol edin
3. Dokümantasyonu inceleyin
4. GitHub Issues'da arama yapın

