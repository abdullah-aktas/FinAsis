# Cloud Build Service Account Yapılandırması

## Sorun

Cloud Build Console'da `211704933618-compute@developer.gserviceaccount.com` görünüyor ama bu service account mevcut değil.

## Çözüm

### Doğru Service Account

Cloud Build için **varsayılan service account** kullanılmalı:

```
211704933618@cloudbuild.gserviceaccount.com
```

**ÖNEMLİ:** `-compute@developer.gserviceaccount.com` değil, `@cloudbuild.gserviceaccount.com` olmalı!

### Service Account Kontrolü

Cloud Shell'de veya gcloud CLI ile:

```bash
# Project number'ı kontrol et
gcloud projects describe finasis-478502 --format="value(projectNumber)"

# Cloud Build service account'unu kontrol et
PROJECT_NUMBER=$(gcloud projects describe finasis-478502 --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
echo "Cloud Build Service Account: $CB_SA"

# Service account'un var olup olmadığını kontrol et
gcloud iam service-accounts describe $CB_SA --project=finasis-478502
```

### Cloud Build Console'da Ayarlama

1. [Cloud Build Settings](https://console.cloud.google.com/cloud-build/settings?project=finasis-478502) sayfasına gidin
2. **Service account** bölümünde:
   - **211704933618@cloudbuild.gserviceaccount.com** seçin
   - Veya **"Use default compute service account"** seçeneğini kaldırın ve **211704933618@cloudbuild.gserviceaccount.com** girin

### Service Account Oluşturma (Gerekirse)

Eğer Cloud Build service account'u yoksa (çok nadir), Cloud Build API'sini etkinleştirdiğinizde otomatik oluşturulur:

```bash
# Cloud Build API'yi etkinleştir
gcloud services enable cloudbuild.googleapis.com --project=finasis-478502

# Service account kontrol et (otomatik oluşturulmuş olmalı)
PROJECT_NUMBER=$(gcloud projects describe finasis-478502 --format="value(projectNumber)")
gcloud iam service-accounts describe ${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com --project=finasis-478502
```

### Otomatik Setup

`scripts/setup-cloud-build.sh` scriptini çalıştırarak otomatik olarak yapılandırabilirsiniz:

```bash
bash scripts/setup-cloud-build.sh
```

Bu script:

- Cloud Build API'yi etkinleştirir
- Cloud Build service account'unu kullanır
- Gerekli IAM rollerini atar

### IAM Rolleri

Cloud Build service account'u için gerekli roller:

```bash
PROJECT_NUMBER=$(gcloud projects describe finasis-478502 --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Artifact Registry Writer (Docker image push için)
gcloud projects add-iam-policy-binding finasis-478502 \
  --member="serviceAccount:$CB_SA" \
  --role="roles/artifactregistry.writer"

# Cloud Run Admin (Deploy için)
gcloud projects add-iam-policy-binding finasis-478502 \
  --member="serviceAccount:$CB_SA" \
  --role="roles/run.admin"

# Service Account User (Cloud Run service account'u kullanmak için)
gcloud projects add-iam-policy-binding finasis-478502 \
  --member="serviceAccount:$CB_SA" \
  --role="roles/iam.serviceAccountUser"
```

### GitHub Actions ile Fark

**Not:** GitHub Actions kullanıyorsanız, Cloud Build service account'u kullanmaz. GitHub Actions kendi authentication'ını kullanır (WIF - Workload Identity Federation). Cloud Build service account'u sadece `gcloud builds submit` komutuyla veya Cloud Build trigger'larıyla kullanılır.

## Kontrol Komutları

```bash
# Cloud Build service account'unu kontrol et
PROJECT_NUMBER=$(gcloud projects describe finasis-478502 --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Service account var mı?
gcloud iam service-accounts describe $CB_SA --project=finasis-478502

# IAM rollerini kontrol et
gcloud projects get-iam-policy finasis-478502 \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$CB_SA" \
  --format="table(bindings.role)"
```
