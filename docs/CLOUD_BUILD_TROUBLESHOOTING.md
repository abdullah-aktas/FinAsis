# Cloud Build Troubleshooting

## Hata: "NOT_FOUND: Requested entity was not found"

Bu hata genellikle Cloud Build API'sinin tam olarak etkinleştirilmemiş olmasından kaynaklanır.

### Çözüm 1: Kapsamlı Düzeltme Scriptini Çalıştırın (ÖNERİLEN)

Cloud Shell'de:

```bash
cd ~/FinAsis
git pull origin main
bash scripts/fix-cloud-build-notfound-comprehensive.sh
```

Bu script:
- Tüm gerekli API'leri etkinleştirir
- API'lerin etkinleşmesi için bekler (30 saniye)
- IAM rollerini kontrol eder ve atar
- Cloud Build storage bucket'ı kontrol eder
- Artifact Registry repository'yi kontrol eder
- Cloud Build servisinin erişilebilirliğini test eder

### Çözüm 2: Setup Scriptini Çalıştırın

Cloud Shell'de:

```bash
cd ~/FinAsis
bash scripts/setup-cloud-build.sh
```

### Çözüm 2: Manuel Kontrol ve Düzeltme

```bash
PROJECT_ID="finasis-478502"
REGION="europe-west1"

# 1. Tüm gerekli API'leri etkinleştir
echo "📡 API'ler etkinleştiriliyor..."
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable artifactregistry.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable storage-api.googleapis.com --project=$PROJECT_ID
gcloud services enable storage-component.googleapis.com --project=$PROJECT_ID

# 2. API'lerin etkin olduğunu kontrol et
echo "🔍 API durumu kontrol ediliyor..."
gcloud services list --enabled --project=$PROJECT_ID --filter="name:cloudbuild.googleapis.com OR name:artifactregistry.googleapis.com OR name:run.googleapis.com"

# 3. Birkaç saniye bekle (API'lerin tam etkinleşmesi için)
echo "⏳ API'lerin etkinleşmesi için 10 saniye bekleniyor..."
sleep 10

# 4. Tekrar dene
echo "🚀 Cloud Build test ediliyor..."
gcloud builds submit --config=deploy/cloud_run/cloudbuild.yaml --project=$PROJECT_ID --region=$REGION .
```

### Çözüm 3: Cloud Build Service Account Kontrolü

```bash
# Service account'un rollerini kontrol et
PROJECT_NUMBER=$(gcloud projects describe finasis-478502 --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

echo "Cloud Build Service Account: $CB_SA"

# Rolleri kontrol et
gcloud projects get-iam-policy finasis-478502 \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$CB_SA" \
  --format="table(bindings.role)"
```

### Çözüm 4: Cloud Build Console'dan Kontrol

1. [Cloud Build Dashboard](https://console.cloud.google.com/cloud-build?project=finasis-478502) sayfasına gidin
2. Eğer "Enable Cloud Build API" butonu görünüyorsa, tıklayın
3. Birkaç dakika bekleyin
4. Tekrar deneyin

### Çözüm 5: Service Usage API Kontrolü

Bazen Service Usage API'si de gerekir:

```bash
gcloud services enable serviceusage.googleapis.com --project=finasis-478502
```

## Alternatif: GitHub Actions Kullanın

Cloud Build'de sorun yaşıyorsanız, GitHub Actions zaten çalışıyor ve daha güvenilir:

1. GitHub Actions workflow'u otomatik çalışır (main branch'e push)
2. Veya manuel olarak [GitHub Actions](https://github.com/abdullah-aktas/FinAsis/actions) sayfasından tetikleyin

## Hata Devam Ederse

1. Cloud Build API'sinin tam etkinleşmesi için 5-10 dakika bekleyin
2. Cloud Shell'i yeniden başlatın
3. `gcloud auth application-default login` komutunu çalıştırın
4. Tekrar deneyin

