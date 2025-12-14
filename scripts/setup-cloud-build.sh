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

# Cloud Build servis hesabını al
CB_SA=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")@cloudbuild.gserviceaccount.com
echo "🔐 Cloud Build servis hesabı: $CB_SA"

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

