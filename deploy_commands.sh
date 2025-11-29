#!/bin/bash
# FinAsis Cloud Run Deploy Script
# Cloud Shell'de çalıştırın

set -e  # Hata durumunda dur

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
REPOSITORY="finasis-app"
IMAGE_NAME="finasis-api"
IMAGE_TAG="latest"

echo "🚀 FinAsis Cloud Run Deploy Başlatılıyor..."
echo "=========================================="

# Projeyi ayarla
gcloud config set project "$PROJECT_ID"

# Artifact Registry repository'sinin var olduğundan emin ol
echo "📦 Artifact Registry repository kontrol ediliyor..."
if ! gcloud artifacts repositories describe "$REPOSITORY" --location="$REGION" &>/dev/null; then
  echo "⚠️  Repository bulunamadı, oluşturuluyor..."
  gcloud artifacts repositories create "$REPOSITORY" \
    --repository-format=docker \
    --location="$REGION" \
    --description="FinAsis application container images"
fi

# Docker authentication
echo "🔐 Docker authentication yapılıyor..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# Image full path
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

# Eğer Cloud Shell'de repo yoksa clone et
if [ ! -d "FinAsis" ]; then
  echo "📥 Repository clone ediliyor..."
  git clone https://github.com/abdullah-aktas/FinAsis.git
  cd FinAsis
else
  echo "📥 Repository güncelleniyor..."
  cd FinAsis
  git pull origin main
fi

# Docker image build
echo "🔨 Docker image build ediliyor..."
docker build -t "$IMAGE_URI" .

# Image push
echo "📤 Image Artifact Registry'ye push ediliyor..."
docker push "$IMAGE_URI"

# Cloud Run deploy
echo "🚀 Cloud Run'a deploy ediliyor..."
gcloud run deploy "$SERVICE_NAME" \
  --image="$IMAGE_URI" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --execution-environment=gen2 \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --concurrency=40 \
  --min-instances=1 \
  --max-instances=10 \
  --set-env-vars="MPLCONFIGDIR=/tmp/matplotlib-cache,PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1"

# Deploy sonrası URL kontrolü
echo ""
echo "✅ Deploy tamamlandı!"
echo "=========================================="
URL=$(gcloud run services describe "$SERVICE_NAME" \
  --platform=managed \
  --region="$REGION" \
  --format='value(status.url)')
echo "🌐 Canlı URL: $URL"
echo ""
echo "📊 Servis durumu kontrol ediliyor..."
gcloud run services describe "$SERVICE_NAME" \
  --platform=managed \
  --region="$REGION" \
  --format='table(status.url,status.latestReadyRevisionName,status.conditions[0].status)'

