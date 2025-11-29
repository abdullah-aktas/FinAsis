# GitHub Actions ve Cloud Shell Bağlantı Kurulumu

Bu doküman, GitHub Actions ile Cloud Shell bağlantısını kontrol etme ve deployment sorunlarını çözme rehberidir.

## 🔍 Sorun Tespiti

Yapılan değişiklikler sitede görünmüyorsa, aşağıdaki adımları takip edin:

### 1. Cloud Shell Bağlantı Kontrolü

Cloud Shell'de aşağıdaki scripti çalıştırın:

```bash
cd FinAsis
chmod +x deploy/check_cloud_shell_connection.sh
./deploy/check_cloud_shell_connection.sh
```

Bu script şunları kontrol eder:
- ✅ GCP proje ayarları
- ✅ Gerekli API'lerin aktifliği
- ✅ Cloud Run servis durumu
- ✅ Artifact Registry durumu
- ✅ Cloud Build son durumlar
- ✅ Cloud SQL bağlantıları
- ✅ Health check

### 2. Deployment Test

Deployment'ın başarılı olup olmadığını test edin:

```bash
chmod +x deploy/test_deployment.sh
./deploy/test_deployment.sh
```

## 🔧 GitHub Actions Secrets Ayarlama

GitHub Actions'un düzgün çalışması için aşağıdaki secrets'ları GitHub repository'nize eklemeniz gerekir:

### Gerekli Secrets

1. **GCP_PROJECT_ID**: GCP proje ID'si
   - Değer: `finasis-478502`

2. **GCP_SA_KEY**: Google Cloud Service Account JSON key
   - Google Cloud Console'dan bir service account oluşturun
   - Cloud Build ve Cloud Run için gerekli izinleri verin
   - JSON key'i indirin ve GitHub secrets'a ekleyin

3. **CLOUD_SQL_CONNECTION** (Opsiyonel): Cloud SQL connection name
   - Format: `PROJECT_ID:REGION:INSTANCE_NAME`
   - Örnek: `finasis-478502:europe-west1:finasis-db`

4. **CLOUD_RUN_ENV_VARS** (Opsiyonel): Environment variables
   - Format: `KEY1=VALUE1,KEY2=VALUE2`
   - Örnek: `DJANGO_DEBUG=False,DJANGO_ALLOWED_HOSTS=finasis.com.tr`

5. **CLOUD_RUN_SECRETS** (Opsiyonel): Secret Manager secrets
   - Format: `KEY1=SECRET_NAME:VERSION,KEY2=SECRET_NAME:VERSION`
   - Örnek: `DJANGO_SECRET_KEY=DJANGO_SECRET_KEY:latest`

### Secrets Ekleme Adımları

1. GitHub repository'nize gidin: `https://github.com/abdullah-aktas/FinAsis`
2. Settings > Secrets and variables > Actions
3. "New repository secret" butonuna tıklayın
4. Her secret için name ve value girin
5. "Add secret" butonuna tıklayın

## 🚀 Manuel Deployment (Cloud Shell)

GitHub Actions çalışmıyorsa, Cloud Shell'de manuel olarak deploy edebilirsiniz:

### Hızlı Deployment

```bash
# Cloud Shell'de
cd FinAsis
git pull origin main

# Cloud Build ile deploy
gcloud builds submit \
  --config=deploy/cloud_run/cloudbuild.yaml \
  --region=europe-west1 \
  --substitutions=_SERVICE=finasis-prod
```

### Cloud SQL ile Deployment

Eğer Cloud SQL bağlantısı gerekiyorsa:

```bash
# Cloud SQL connection name'i alın
CLOUD_SQL_CONNECTION=$(gcloud sql instances describe INSTANCE_NAME \
  --format="value(connectionName)")

# Deploy edin
gcloud builds submit \
  --config=deploy/cloud_run/cloudbuild.yaml \
  --region=europe-west1 \
  --substitutions=_SERVICE=finasis-prod,_CLOUD_SQL_CONNECTION=$CLOUD_SQL_CONNECTION
```

## 🔍 Sorun Giderme

### Problem: GitHub Actions çalışmıyor

**Kontrol listesi:**
1. ✅ Secrets doğru ayarlanmış mı?
2. ✅ Service account'un gerekli izinleri var mı?
3. ✅ Workflow dosyası doğru branch'te mi? (main)
4. ✅ GitHub Actions enabled mi? (Settings > Actions)

**Çözüm:**
- GitHub Actions sayfasından son çalıştırmaları kontrol edin
- Hata loglarını inceleyin
- Secrets'ları yeniden kontrol edin

### Problem: Build başarılı ama değişiklikler görünmüyor

**Kontrol listesi:**
1. ✅ Yeni revision oluşturuldu mu?
2. ✅ Yeni revision'a traffic yönlendirildi mi?
3. ✅ Image tag doğru mu? (latest yerine timestamp kullanılmalı)

**Çözüm:**
```bash
# Revision'ları kontrol edin
gcloud run revisions list \
  --service=finasis-prod \
  --region=europe-west1

# Son revision'ın image'ını kontrol edin
gcloud run revisions describe REVISION_NAME \
  --region=europe-west1 \
  --format="value(spec.containers[0].image)"

# Eğer yeni revision'a traffic yönlendirilmemişse:
gcloud run services update-traffic finasis-prod \
  --region=europe-west1 \
  --to-revisions=REVISION_NAME=100
```

### Problem: Cloud Shell'de bağlantı hatası

**Kontrol listesi:**
1. ✅ Doğru projede misiniz? (`gcloud config get-value project`)
2. ✅ Gerekli API'ler aktif mi?
3. ✅ Authentication yapıldı mı? (`gcloud auth list`)

**Çözüm:**
```bash
# Projeyi ayarlayın
gcloud config set project finasis-478502

# Gerekli API'leri etkinleştirin
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Authentication kontrolü
gcloud auth list
```

## 📊 Monitoring ve Loglar

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

### Real-time Log Monitoring

```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=finasis-prod" \
  --format="table(timestamp,severity,textPayload)"
```

## ✅ Deployment Kontrol Checklist

Her deployment sonrası şunları kontrol edin:

- [ ] Build başarılı mı? (`gcloud builds list`)
- [ ] Yeni revision oluşturuldu mu? (`gcloud run revisions list`)
- [ ] Servis çalışıyor mu? (`curl SERVICE_URL`)
- [ ] Loglar temiz mi? (`gcloud run services logs read`)
- [ ] Environment variables doğru mu? (`gcloud run services describe`)
- [ ] Health check başarılı mı? (`./deploy/test_deployment.sh`)

## 🆘 Acil Durum Rollback

Eğer deployment sonrası ciddi bir sorun varsa:

```bash
# Son çalışan revision'ı bulun
gcloud run revisions list \
  --service=finasis-prod \
  --region=europe-west1 \
  --sort-by=~metadata.creationTimestamp \
  --limit=2

# Önceki revision'a rollback yapın
gcloud run services update-traffic finasis-prod \
  --region=europe-west1 \
  --to-revisions=PREVIOUS_REVISION_NAME=100
```

## 📝 Notlar

- GitHub Actions workflow'u her `main` branch'e push'ta otomatik çalışır
- Sadece belirli dosya değişikliklerinde tetiklenir (`.py`, `.html`, `.js`, `.css`, `Dockerfile`, `requirements.txt`, `deploy/**`, `config/**`)
- Manuel tetikleme için GitHub Actions sayfasından "Run workflow" butonunu kullanabilirsiniz
- Cloud Build timeout'u 2400 saniye (40 dakika) olarak ayarlanmıştır

