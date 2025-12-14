#!/bin/bash
# Cloud Build NOT_FOUND hatası için kapsamlı düzeltme scripti
# Cloud Shell'de çalıştırın: bash scripts/fix-cloud-build-notfound-comprehensive.sh

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
REPOSITORY="finasis-app"

echo "🔧 Cloud Build NOT_FOUND hatası kapsamlı düzeltme başlatılıyor..."
echo ""

# 1. Proje bilgilerini al
echo "📊 Proje bilgileri alınıyor..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
BUCKET_NAME="${PROJECT_ID}_cloudbuild"

echo "   Project ID: $PROJECT_ID"
echo "   Project Number: $PROJECT_NUMBER"
echo "   Cloud Build Service Account: $CB_SA"
echo "   Storage Bucket: $BUCKET_NAME"
echo ""

# 2. Tüm gerekli API'leri etkinleştir
echo "📡 Tüm gerekli API'ler etkinleştiriliyor..."
APIS=(
  "cloudbuild.googleapis.com"
  "artifactregistry.googleapis.com"
  "run.googleapis.com"
  "storage-api.googleapis.com"
  "storage-component.googleapis.com"
  "serviceusage.googleapis.com"
  "cloudresourcemanager.googleapis.com"
  "iam.googleapis.com"
  "logging.googleapis.com"
  "monitoring.googleapis.com"
)

for api in "${APIS[@]}"; do
  echo "   Enabling $api..."
  gcloud services enable $api --project=$PROJECT_ID || echo "   ⚠️  $api zaten etkin veya etkinleştirilemedi"
done

echo ""
echo "⏳ API'lerin tam etkinleşmesi için 30 saniye bekleniyor..."
sleep 30

# 3. API'lerin etkin olduğunu kontrol et
echo ""
echo "🔍 API durumu kontrol ediliyor..."
ENABLED_APIS=$(gcloud services list --enabled --project=$PROJECT_ID --format="value(name)")

MISSING_APIS=()
for api in "${APIS[@]}"; do
  if echo "$ENABLED_APIS" | grep -q "$api"; then
    echo "   ✅ $api etkin"
  else
    echo "   ❌ $api etkin değil!"
    MISSING_APIS+=("$api")
  fi
done

if [ ${#MISSING_APIS[@]} -gt 0 ]; then
  echo ""
  echo "⚠️  Bazı API'ler etkin değil. Lütfen Cloud Console'dan manuel olarak etkinleştirin:"
  echo "   https://console.cloud.google.com/apis/library?project=$PROJECT_ID"
  echo ""
  echo "   Eksik API'ler:"
  for api in "${MISSING_APIS[@]}"; do
    echo "   - $api"
  done
  echo ""
  echo "   Veya komutla:"
  for api in "${MISSING_APIS[@]}"; do
    echo "   gcloud services enable $api --project=$PROJECT_ID"
  done
fi

# 4. Cloud Build service account kontrolü
echo ""
echo "🔍 Cloud Build service account kontrol ediliyor..."
if gcloud iam service-accounts describe $CB_SA --project=$PROJECT_ID &>/dev/null; then
  echo "   ✅ Cloud Build service account mevcut: $CB_SA"
else
  echo "   ⚠️  Cloud Build service account bulunamadı"
  echo "   Cloud Build API'si etkinleştirildiğinde otomatik oluşturulmalı"
  echo "   Birkaç dakika bekleyip tekrar deneyin"
fi

# 5. IAM rollerini kontrol et ve ata
echo ""
echo "🔍 IAM rolleri kontrol ediliyor..."
IAM_ROLES=$(gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$CB_SA" \
  --format="value(bindings.role)" 2>/dev/null || echo "")

REQUIRED_ROLES=(
  "roles/artifactregistry.writer"
  "roles/run.admin"
  "roles/iam.serviceAccountUser"
)

MISSING_ROLES=()
for role in "${REQUIRED_ROLES[@]}"; do
  if echo "$IAM_ROLES" | grep -q "$role"; then
    echo "   ✅ $role"
  else
    echo "   ❌ $role (eksik, atanıyor...)"
    gcloud projects add-iam-policy-binding $PROJECT_ID \
      --member="serviceAccount:$CB_SA" \
      --role="$role" \
      --condition=None || echo "   ⚠️  Rol atanamadı"
    MISSING_ROLES+=("$role")
  fi
done

# 6. Cloud Build storage bucket kontrolü
echo ""
echo "🔍 Cloud Build storage bucket kontrol ediliyor..."
if gsutil ls -b gs://$BUCKET_NAME &>/dev/null; then
  echo "   ✅ Cloud Build storage bucket mevcut: gs://$BUCKET_NAME"
  
  # Bucket permissions kontrolü
  echo "   🔍 Bucket permissions kontrol ediliyor..."
  gsutil iam ch serviceAccount:$CB_SA:roles/storage.admin gs://$BUCKET_NAME || echo "   ⚠️  Permission atanamadı (zaten mevcut olabilir)"
else
  echo "   ⚠️  Cloud Build storage bucket oluşturuluyor..."
  gsutil mb -l $REGION gs://$BUCKET_NAME || echo "   ⚠️  Bucket oluşturulamadı (zaten mevcut olabilir)"
  gsutil iam ch serviceAccount:$CB_SA:roles/storage.admin gs://$BUCKET_NAME || echo "   ⚠️  Permission atanamadı"
fi

# 7. Artifact Registry repository kontrolü
echo ""
echo "🔍 Artifact Registry repository kontrol ediliyor..."
if gcloud artifacts repositories describe $REPOSITORY \
  --location=$REGION \
  --project=$PROJECT_ID &>/dev/null; then
  echo "   ✅ Artifact Registry repository mevcut: $REPOSITORY"
else
  echo "   ⚠️  Artifact Registry repository oluşturuluyor..."
  gcloud artifacts repositories create $REPOSITORY \
    --repository-format=docker \
    --location=$REGION \
    --project=$PROJECT_ID \
    --description="FinAsis Docker images" || echo "   ⚠️  Repository oluşturulamadı (zaten mevcut olabilir)"
fi

# 8. Cloud Build servisinin erişilebilirliğini test et
echo ""
echo "🔍 Cloud Build servisinin erişilebilirliği test ediliyor..."
if gcloud builds list --project=$PROJECT_ID --limit=1 &>/dev/null; then
  echo "   ✅ Cloud Build servisi erişilebilir!"
else
  echo "   ❌ Cloud Build servisi hala erişilemiyor"
  echo ""
  echo "   💡 Bu durumda şunları deneyin:"
  echo "   1. Cloud Build Console'dan manuel olarak bir build başlatın:"
  echo "      https://console.cloud.google.com/cloud-build?project=$PROJECT_ID"
  echo "   2. Cloud Build Settings sayfasına gidin ve service account'u kontrol edin:"
  echo "      https://console.cloud.google.com/cloud-build/settings?project=$PROJECT_ID"
  echo "      Service account: $CB_SA olmalı"
  echo "   3. Birkaç dakika bekleyin (API propagation için)"
  echo "   4. Cloud Shell'i yeniden başlatın"
  echo "   5. GitHub Actions kullanın (daha güvenilir):"
  echo "      https://github.com/abdullah-aktas/FinAsis/actions"
  exit 1
fi

# 9. Cloud Build Console ayarları kontrolü
echo ""
echo "📝 Cloud Build Console Ayarları:"
echo "   1. https://console.cloud.google.com/cloud-build/settings?project=$PROJECT_ID"
echo "   2. 'Service account' alanına şunu girin: $CB_SA"
echo "   3. Veya 'Use default compute service account' seçeneğini kaldırın"
echo ""

# 10. Son test - basit bir build denemesi
echo ""
echo "🧪 Basit bir Cloud Build testi yapılıyor..."
TEST_BUILD_ID=$(gcloud builds submit --config=/dev/null --no-source --project=$PROJECT_ID 2>&1 | grep -oP 'ID: \K[^\s]+' || echo "")

if [ -n "$TEST_BUILD_ID" ]; then
  echo "   ✅ Test build başlatıldı: $TEST_BUILD_ID"
  echo "   Build durumunu kontrol edin:"
  echo "   gcloud builds describe $TEST_BUILD_ID --project=$PROJECT_ID"
else
  echo "   ⚠️  Test build başlatılamadı (bu normal olabilir)"
fi

echo ""
echo "✅ Kapsamlı düzeltme tamamlandı!"
echo ""
echo "🚀 Şimdi Cloud Build ile deploy edebilirsiniz:"
echo "   cd ~/FinAsis && gcloud builds submit --config=deploy/cloud_run/cloudbuild.yaml --project=$PROJECT_ID --region=$REGION ."
echo ""
echo "💡 Eğer hala 'NOT_FOUND' hatası alıyorsanız:"
echo "   1. Cloud Build Console'dan manuel olarak bir build başlatmayı deneyin"
echo "   2. Birkaç dakika bekleyin (API propagation için)"
echo "   3. Cloud Shell'i yeniden başlatın"
echo "   4. GitHub Actions kullanın (daha güvenilir)"

