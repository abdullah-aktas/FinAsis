#!/bin/bash
# Cloud Build NOT_FOUND hatası için düzeltme scripti
# Cloud Shell'de çalıştırın: bash scripts/fix-cloud-build-notfound.sh

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"

echo "🔧 Cloud Build NOT_FOUND hatası düzeltiliyor..."
echo ""

# 1. Tüm gerekli API'leri etkinleştir
echo "📡 Tüm gerekli API'ler etkinleştiriliyor..."
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable artifactregistry.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable storage-api.googleapis.com --project=$PROJECT_ID
gcloud services enable storage-component.googleapis.com --project=$PROJECT_ID
gcloud services enable serviceusage.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudresourcemanager.googleapis.com --project=$PROJECT_ID
gcloud services enable iam.googleapis.com --project=$PROJECT_ID

echo ""
echo "⏳ API'lerin tam etkinleşmesi için 15 saniye bekleniyor..."
sleep 15

# 2. API'lerin etkin olduğunu kontrol et
echo ""
echo "🔍 API durumu kontrol ediliyor..."
ENABLED_APIS=$(gcloud services list --enabled --project=$PROJECT_ID --filter="name:cloudbuild.googleapis.com OR name:artifactregistry.googleapis.com OR name:run.googleapis.com" --format="value(name)")

if echo "$ENABLED_APIS" | grep -q cloudbuild; then
  echo "✅ Cloud Build API etkin"
else
  echo "❌ Cloud Build API hala etkin değil!"
  echo "   Lütfen Cloud Build Console'dan manuel olarak etkinleştirin:"
  echo "   https://console.cloud.google.com/cloud-build?project=$PROJECT_ID"
  exit 1
fi

# 3. Cloud Build service account'unu kontrol et
echo ""
echo "🔍 Cloud Build service account kontrol ediliyor..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
echo "   Service Account: $CB_SA"

# 4. IAM rollerini kontrol et
echo ""
echo "🔍 IAM rolleri kontrol ediliyor..."
IAM_ROLES=$(gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$CB_SA" \
  --format="value(bindings.role)" 2>/dev/null || echo "")

if [ -z "$IAM_ROLES" ]; then
  echo "⚠️  IAM rolleri bulunamadı, atanıyor..."
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CB_SA" \
    --role="roles/artifactregistry.writer" \
    --condition=None || true
  
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CB_SA" \
    --role="roles/run.admin" \
    --condition=None || true
  
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CB_SA" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None || true
else
  echo "✅ IAM rolleri mevcut"
fi

# 5. Cloud Build storage bucket kontrolü
echo ""
echo "🔍 Cloud Build storage bucket kontrol ediliyor..."
BUCKET_NAME="${PROJECT_ID}_cloudbuild"
if gsutil ls -b gs://$BUCKET_NAME &>/dev/null; then
  echo "✅ Cloud Build storage bucket mevcut"
else
  echo "⚠️  Cloud Build storage bucket oluşturuluyor..."
  gsutil mb -l $REGION gs://$BUCKET_NAME || echo "⚠️  Bucket oluşturulamadı (zaten mevcut olabilir)"
fi

# 6. Artifact Registry repository kontrolü
echo ""
echo "🔍 Artifact Registry repository kontrol ediliyor..."
REPOSITORY="finasis-app"
if gcloud artifacts repositories describe $REPOSITORY \
  --location=$REGION \
  --project=$PROJECT_ID &>/dev/null; then
  echo "✅ Artifact Registry repository mevcut"
else
  echo "⚠️  Artifact Registry repository oluşturuluyor..."
  gcloud artifacts repositories create $REPOSITORY \
    --repository-format=docker \
    --location=$REGION \
    --project=$PROJECT_ID \
    --description="FinAsis Docker images" || echo "⚠️  Repository oluşturulamadı (zaten mevcut olabilir)"
fi

# 7. Son kontrol - Cloud Build listesi
echo ""
echo "🔍 Cloud Build servisinin erişilebilirliği test ediliyor..."
if gcloud builds list --project=$PROJECT_ID --limit=1 &>/dev/null; then
  echo "✅ Cloud Build servisi erişilebilir!"
else
  echo "❌ Cloud Build servisi hala erişilemiyor"
  echo ""
  echo "💡 Öneriler:"
  echo "   1. Cloud Build Console'dan manuel olarak bir build başlatmayı deneyin:"
  echo "      https://console.cloud.google.com/cloud-build?project=$PROJECT_ID"
  echo "   2. Birkaç dakika bekleyin ve tekrar deneyin"
  echo "   3. GitHub Actions kullanın (daha güvenilir):"
  echo "      https://github.com/abdullah-aktas/FinAsis/actions"
  exit 1
fi

echo ""
echo "✅ Düzeltme tamamlandı!"
echo ""
echo "🚀 Şimdi Cloud Build ile deploy edebilirsiniz:"
echo "   cd ~/FinAsis && gcloud builds submit --config=deploy/cloud_run/cloudbuild.yaml --project=$PROJECT_ID --region=$REGION ."

