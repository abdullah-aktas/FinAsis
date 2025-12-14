#!/bin/bash
# Cloud Build setup script
# Cloud Shell'de çalıştırın: bash scripts/setup-cloud-build.sh

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
REPOSITORY="finasis-app"

echo "🔧 Cloud Build setup başlatılıyor..."

# Proje ID'sini ayarla
gcloud config set project $PROJECT_ID

# Gerekli API'leri etkinleştir
echo "📡 Gerekli API'ler etkinleştiriliyor..."
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable artifactregistry.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable storage-api.googleapis.com --project=$PROJECT_ID
gcloud services enable storage-component.googleapis.com --project=$PROJECT_ID

# Cloud Build için Cloud Storage bucket'ını kontrol et ve oluştur
echo "🪣 Cloud Build storage bucket kontrol ediliyor..."
BUCKET_NAME="${PROJECT_ID}_cloudbuild"
if ! gsutil ls -b gs://$BUCKET_NAME &>/dev/null; then
  echo "🪣 Cloud Build storage bucket oluşturuluyor..."
  gsutil mb -l $REGION gs://$BUCKET_NAME || echo "⚠️  Bucket zaten mevcut veya oluşturulamadı"
  # Bucket'a Cloud Build servis hesabına yetki ver
  gsutil iam ch serviceAccount:$CB_SA:roles/storage.admin gs://$BUCKET_NAME || true
  echo "✅ Cloud Build storage bucket oluşturuldu"
else
  echo "✅ Cloud Build storage bucket zaten mevcut"
fi

# Cloud Build servis hesabını al
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
echo "🔐 Cloud Build servis hesabı: $CB_SA"

# Artifact Registry repository'sinin var olup olmadığını kontrol et
echo "📦 Artifact Registry repository kontrol ediliyor..."
if ! gcloud artifacts repositories describe $REPOSITORY \
  --location=$REGION \
  --project=$PROJECT_ID &>/dev/null; then
  echo "📦 Artifact Registry repository oluşturuluyor..."
  gcloud artifacts repositories create $REPOSITORY \
    --repository-format=docker \
    --location=$REGION \
    --project=$PROJECT_ID \
    --description="FinAsis Docker images"
  echo "✅ Artifact Registry repository oluşturuldu"
else
  echo "✅ Artifact Registry repository zaten mevcut"
fi

# Gerekli rollerin verilip verilmediğini kontrol et ve ver
echo "🔐 Cloud Build servis hesabına gerekli roller veriliyor..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$CB_SA" \
  --role="roles/artifactregistry.writer" \
  --condition=None || echo "⚠️  Artifact Registry Writer rolü zaten verilmiş"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$CB_SA" \
  --role="roles/run.admin" \
  --condition=None || echo "⚠️  Cloud Run Admin rolü zaten verilmiş"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$CB_SA" \
  --role="roles/iam.serviceAccountUser" \
  --condition=None || echo "⚠️  Service Account User rolü zaten verilmiş"

echo "✅ Setup tamamlandı!"
echo ""
echo "🚀 Artık Cloud Build ile deploy edebilirsiniz:"
echo "   cd ~/FinAsis && gcloud builds submit --config=deploy/cloud_run/cloudbuild.yaml --project=$PROJECT_ID --region=$REGION ."

