# Cloud Shell'de Hızlı Deployment

Bu rehber, Cloud Shell kullanarak değişiklikleri canlıya almak için gerekli adımları açıklar.

## 🚀 Hızlı Başlangıç (3 Adım)

### 1. Cloud Shell'i Açın
Google Cloud Console'dan Cloud Shell'i açın (sağ üst köşedeki terminal ikonu).

### 2. Repository'yi Clone Edin veya Güncelleyin

```bash
# Eğer daha önce clone etmediyseniz
git clone https://github.com/abdullah-aktas/FinAsis.git
cd FinAsis

# Veya mevcut repository'yi güncelleyin
cd FinAsis
git pull origin main
```

### 3. Deployment'ı Başlatın

**Seçenek A: Otomatik Script (Önerilen)**
```bash
chmod +x deploy/quick_deploy.sh
./deploy/quick_deploy.sh
```

**Seçenek B: Manuel Cloud Build**
```bash
gcloud builds submit \
  --config=deploy/cloud_run/cloudbuild.yaml \
  --region=europe-west1 \
  --substitutions=_SERVICE=finasis-prod
```

## 📋 Detaylı Adımlar

### Adım 1: Proje Kontrolü

```bash
# Mevcut projeyi kontrol edin
gcloud config get-value project

# Eğer yanlış projedeyseniz, değiştirin
gcloud config set project finasis-478502
```

### Adım 2: Gerekli API'lerin Aktif Olduğundan Emin Olun

```bash
# Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Cloud Run API
gcloud services enable run.googleapis.com

# Container Registry API
gcloud services enable containerregistry.googleapis.com
```

### Adım 3: Repository'yi Hazırlayın

```bash
# Repository'yi clone edin (ilk kez)
git clone https://github.com/abdullah-aktas/FinAsis.git
cd FinAsis

# Veya mevcut repository'yi güncelleyin
cd FinAsis
git pull origin main
```

### Adım 4: Deployment'ı Çalıştırın

**Yöntem 1: Otomatik Script (En Kolay)**

```bash
chmod +x deploy/quick_deploy.sh
./deploy/quick_deploy.sh
```

Script size şunları soracak:
- Deployment'a devam etmek istiyor musunuz? (y/N)
- Build'in tamamlanmasını beklemek istiyor musunuz? (y/N)

**Yöntem 2: Manuel Cloud Build**

```bash
gcloud builds submit \
  --config=deploy/cloud_run/cloudbuild.yaml \
  --region=europe-west1 \
  --substitutions=_SERVICE=finasis-prod
```

### Adım 5: Deployment Durumunu İzleyin

```bash
# Son build'i görüntüleyin
gcloud builds list --limit=5

# Belirli bir build'in loglarını görüntüleyin
gcloud builds log BUILD_ID

# Cloud Run servis durumunu kontrol edin
gcloud run services describe finasis-prod \
  --region=europe-west1 \
  --format="value(status.url)"
```

## ✅ Deployment Sonrası Kontroller

### 1. Servis URL'sini Alın

```bash
SERVICE_URL=$(gcloud run services describe finasis-prod \
  --region=europe-west1 \
  --format="value(status.url)")

echo "Servis URL: $SERVICE_URL"
```

### 2. Health Check Yapın

```bash
curl $SERVICE_URL
```

### 3. Logları Kontrol Edin

```bash
gcloud run services logs read finasis-prod \
  --region=europe-west1 \
  --limit=50
```

### 4. Revision'ları Kontrol Edin

```bash
gcloud run revisions list \
  --service=finasis-prod \
  --region=europe-west1
```

## 🔧 Sorun Giderme

### Build Başarısız Olursa

```bash
# Son build'in loglarını görüntüleyin
gcloud builds list --limit=1
gcloud builds log $(gcloud builds list --limit=1 --format="value(id)")
```

### Deployment Başarısız Olursa

```bash
# Mevcut revision'ları listeleyin
gcloud run revisions list --service=finasis-prod --region=europe-west1

# Önceki revision'a rollback yapın
gcloud run services update-traffic finasis-prod \
  --region=europe-west1 \
  --to-revisions=PREVIOUS_REVISION=100
```

### Environment Variables Kontrolü

```bash
# Mevcut env vars'ları görüntüleyin
gcloud run services describe finasis-prod \
  --region=europe-west1 \
  --format="value(spec.template.spec.containers[0].env)"
```

## 🎯 Hızlı Komutlar Özeti

```bash
# 1. Repository güncelle
cd FinAsis && git pull origin main

# 2. Deploy et
gcloud builds submit --config=deploy/cloud_run/cloudbuild.yaml --region=europe-west1

# 3. URL'yi al
gcloud run services describe finasis-prod --region=europe-west1 --format="value(status.url)"

# 4. Logları görüntüle
gcloud run services logs read finasis-prod --region=europe-west1 --limit=20
```

## 📝 Notlar

1. **İlk Deployment**: İlk kez deploy ediyorsanız, Cloud Run servisinin oluşturulması biraz zaman alabilir.

2. **Build Süresi**: Normal bir build 5-10 dakika sürebilir. İlk build daha uzun sürebilir.

3. **Zero-Downtime**: Cloud Run yeni revision'ı deploy ederken eski revision çalışmaya devam eder, bu yüzden sıfır downtime vardır.

4. **Rollback**: Her deployment yeni bir revision oluşturur. Sorun olursa önceki revision'a kolayca dönebilirsiniz.

## 🚨 Acil Durum Rollback

Eğer deployment sonrası ciddi bir sorun varsa:

```bash
# Son çalışan revision'ı bulun
gcloud run revisions list \
  --service=finasis-prod \
  --region=europe-west1 \
  --sort-by=~metadata.creationTimestamp \
  --limit=2

# İkinci revision'a (önceki çalışan) %100 traffic verin
gcloud run services update-traffic finasis-prod \
  --region=europe-west1 \
  --to-revisions=REVISION_NAME=100
```

