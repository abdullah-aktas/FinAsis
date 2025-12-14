# Cloud Build Console Manuel Kurulum Rehberi

## NOT_FOUND Hatası İçin Manuel Kontrol

Eğer `gcloud builds submit` komutu "NOT_FOUND: Requested entity was not found" hatası veriyorsa, Cloud Build Console'dan manuel kontrol yapın.

## Adım 1: Cloud Build API'sini Kontrol Et

1. [Cloud Build Dashboard](https://console.cloud.google.com/cloud-build?project=finasis-478502) sayfasına gidin
2. Eğer "Enable Cloud Build API" butonu görünüyorsa, tıklayın
3. API'nin etkinleşmesi için 2-3 dakika bekleyin

## Adım 2: Cloud Build Settings'i Kontrol Et

1. [Cloud Build Settings](https://console.cloud.google.com/cloud-build/settings?project=finasis-478502) sayfasına gidin
2. **Service account** bölümünü bulun
3. **ÖNEMLİ:** Service account şu formatta olmalı:
   ```
   211704933618@cloudbuild.gserviceaccount.com
   ```
   **DEĞİL:** `211704933618-compute@developer.gserviceaccount.com`

4. Eğer yanlış service account görünüyorsa:
   - "Use default compute service account" seçeneğini **kaldırın**
   - Doğru service account'u girin: `211704933618@cloudbuild.gserviceaccount.com`
   - "Save" butonuna tıklayın

## Adım 3: Manuel Build Başlatma Testi

1. [Cloud Build Dashboard](https://console.cloud.google.com/cloud-build?project=finasis-478502) sayfasına gidin
2. "Create Build" veya "Trigger" butonuna tıklayın
3. "Build configuration" seçeneğini seçin
4. "Cloud Build configuration file (yaml or json)" seçeneğini seçin
5. Repository'den `deploy/cloud_run/cloudbuild.yaml` dosyasını seçin
6. "Start" butonuna tıklayın
7. Build'in başladığını kontrol edin

## Adım 4: Service Account IAM Rolleri Kontrolü

1. [IAM & Admin > IAM](https://console.cloud.google.com/iam-admin/iam?project=finasis-478502) sayfasına gidin
2. `211704933618@cloudbuild.gserviceaccount.com` service account'unu arayın
3. Aşağıdaki rollerin atanmış olduğunu kontrol edin:
   - **Artifact Registry Writer** (`roles/artifactregistry.writer`)
   - **Cloud Run Admin** (`roles/run.admin`)
   - **Service Account User** (`roles/iam.serviceAccountUser`)

4. Eğer roller eksikse:
   - Service account'un yanındaki "Edit" (kalem) ikonuna tıklayın
   - "Add Another Role" butonuna tıklayın
   - Eksik rolleri ekleyin
   - "Save" butonuna tıklayın

## Adım 5: Artifact Registry Repository Kontrolü

1. [Artifact Registry](https://console.cloud.google.com/artifacts?project=finasis-478502) sayfasına gidin
2. `finasis-app` repository'sinin mevcut olduğunu kontrol edin
3. Eğer yoksa:
   - "Create Repository" butonuna tıklayın
   - Repository name: `finasis-app`
   - Format: **Docker**
   - Location: `europe-west1`
   - "Create" butonuna tıklayın

## Adım 6: Cloud Build Storage Bucket Kontrolü

1. [Cloud Storage](https://console.cloud.google.com/storage/browser?project=finasis-478502) sayfasına gidin
2. `finasis-478502_cloudbuild` bucket'ının mevcut olduğunu kontrol edin
3. Eğer yoksa:
   - "Create Bucket" butonuna tıklayın
   - Bucket name: `finasis-478502_cloudbuild`
   - Location: `europe-west1`
   - "Create" butonuna tıklayın

## Sorun Devam Ederse

1. **API Propagation Bekleyin:** API'lerin tam etkinleşmesi için 5-10 dakika bekleyin
2. **Cloud Shell'i Yeniden Başlatın:** Cloud Shell'i kapatıp açın
3. **Authentication Kontrolü:** `gcloud auth application-default login` komutunu çalıştırın
4. **GitHub Actions Kullanın:** Cloud Build'de sorun yaşıyorsanız, GitHub Actions zaten çalışıyor ve daha güvenilir:
   - [GitHub Actions](https://github.com/abdullah-aktas/FinAsis/actions) sayfasından manuel olarak tetikleyin
   - Veya `main` branch'e push yapın (otomatik tetiklenir)

## Hızlı Kontrol Komutları

Cloud Shell'de:

```bash
PROJECT_ID="finasis-478502"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Service account kontrolü
echo "Cloud Build Service Account: $CB_SA"

# IAM rolleri kontrolü
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$CB_SA" \
  --format="table(bindings.role)"

# API durumu kontrolü
gcloud services list --enabled --project=$PROJECT_ID \
  --filter="name:cloudbuild.googleapis.com OR name:artifactregistry.googleapis.com OR name:run.googleapis.com"

# Cloud Build erişilebilirlik testi
gcloud builds list --project=$PROJECT_ID --limit=1
```

