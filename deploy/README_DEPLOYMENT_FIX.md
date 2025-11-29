# Deployment Sorunları ve Çözümler

## 🎯 Sorun: Yapılan Değişiklikler Sitede Görünmüyor

Bu doküman, GitHub Actions ve Cloud Shell bağlantısını kontrol etme ve deployment sorunlarını çözme rehberidir.

## ✅ Yapılan İyileştirmeler

### 1. GitHub Actions Workflow Güncellemesi

`.github/workflows/deploy.yml` dosyası güncellendi:
- ✅ Cloud SQL connection parametresi eklendi
- ✅ Environment variables parametresi eklendi
- ✅ Secrets parametresi eklendi
- ✅ Region ve repository parametreleri eklendi

### 2. Yeni Kontrol Scriptleri

**`deploy/check_cloud_shell_connection.sh`**
- Cloud Shell bağlantısını kontrol eder
- Gerekli API'lerin aktifliğini kontrol eder
- Cloud Run servis durumunu gösterir
- Artifact Registry durumunu kontrol eder
- Cloud Build son durumlarını listeler

**`deploy/test_deployment.sh`**
- Deployment'ın başarılı olup olmadığını test eder
- Health check yapar
- Logları kontrol eder
- Environment variables'ı kontrol eder
- Build durumunu kontrol eder

## 🚀 Hızlı Başlangıç

### Adım 1: Cloud Shell'de Bağlantıyı Kontrol Edin

```bash
# Cloud Shell'i açın (Google Cloud Console'dan)
cd FinAsis
git pull origin main

# Bağlantı kontrolü
bash deploy/check_cloud_shell_connection.sh
```

### Adım 2: Deployment Durumunu Test Edin

```bash
# Deployment testi
bash deploy/test_deployment.sh
```

### Adım 3: Gerekirse Manuel Deploy Edin

```bash
# Manuel deployment
gcloud builds submit \
  --config=deploy/cloud_run/cloudbuild.yaml \
  --region=europe-west1 \
  --substitutions=_SERVICE=finasis-prod
```

## 🔧 GitHub Actions Secrets Ayarlama

GitHub Actions'un çalışması için aşağıdaki secrets'ları GitHub'a eklemeniz gerekir:

### Zorunlu Secrets

1. **GCP_PROJECT_ID**
   - Değer: `finasis-478502`

2. **GCP_SA_KEY**
   - Google Cloud Service Account JSON key
   - Cloud Build ve Cloud Run için izinleri olmalı

### Opsiyonel Secrets (Önerilir)

3. **CLOUD_SQL_CONNECTION**
   - Format: `PROJECT_ID:REGION:INSTANCE_NAME`
   - Örnek: `finasis-478502:europe-west1:finasis-db`

4. **CLOUD_RUN_ENV_VARS**
   - Format: `KEY1=VALUE1,KEY2=VALUE2`
   - Örnek: `DJANGO_DEBUG=False,DJANGO_ALLOWED_HOSTS=finasis.com.tr`

5. **CLOUD_RUN_SECRETS**
   - Format: `KEY1=SECRET_NAME:VERSION,KEY2=SECRET_NAME:VERSION`
   - Örnek: `DJANGO_SECRET_KEY=DJANGO_SECRET_KEY:latest`

### Secrets Ekleme

1. GitHub repository: `https://github.com/abdullah-aktas/FinAsis`
2. Settings > Secrets and variables > Actions
3. "New repository secret" ile her secret'ı ekleyin

## 🔍 Sorun Giderme

### Problem 1: GitHub Actions Çalışmıyor

**Kontrol:**
- Secrets doğru ayarlanmış mı?
- Service account'un izinleri var mı?
- Workflow dosyası main branch'te mi?

**Çözüm:**
```bash
# GitHub Actions sayfasından son çalıştırmaları kontrol edin
# Hata loglarını inceleyin
```

### Problem 2: Build Başarılı Ama Değişiklikler Görünmüyor

**Kontrol:**
```bash
# Revision'ları kontrol edin
gcloud run revisions list \
  --service=finasis-prod \
  --region=europe-west1

# Son revision'ın image'ını kontrol edin
gcloud run revisions describe REVISION_NAME \
  --region=europe-west1 \
  --format="value(spec.containers[0].image)"
```

**Çözüm:**
- Yeni revision oluşturuldu mu kontrol edin
- Traffic yönlendirmesi doğru mu kontrol edin
- Image tag'i doğru mu kontrol edin

### Problem 3: Cloud Shell Bağlantı Hatası

**Kontrol:**
```bash
# Proje kontrolü
gcloud config get-value project

# API kontrolü
gcloud services list --enabled | grep cloudbuild
gcloud services list --enabled | grep run
```

**Çözüm:**
```bash
# Projeyi ayarlayın
gcloud config set project finasis-478502

# API'leri etkinleştirin
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

## 📊 Monitoring

### Logları Görüntüleme

```bash
# Cloud Run logları
gcloud run services logs read finasis-prod \
  --region=europe-west1 \
  --limit=50

# Cloud Build logları
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

### Real-time Monitoring

```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=finasis-prod"
```

## ✅ Deployment Checklist

Her deployment sonrası:

- [ ] Build başarılı mı?
- [ ] Yeni revision oluşturuldu mu?
- [ ] Servis çalışıyor mu?
- [ ] Loglar temiz mi?
- [ ] Health check başarılı mı?

## 🆘 Acil Rollback

```bash
# Önceki revision'a dön
gcloud run services update-traffic finasis-prod \
  --region=europe-west1 \
  --to-revisions=PREVIOUS_REVISION_NAME=100
```

## 📝 Detaylı Dokümantasyon

Daha fazla bilgi için:
- `deploy/GITHUB_ACTIONS_SETUP.md` - GitHub Actions kurulum rehberi
- `deploy/CLOUD_SHELL_QUICK_DEPLOY.md` - Cloud Shell deployment rehberi
- `deploy/DEPLOY_TO_PRODUCTION.md` - Production deployment rehberi

