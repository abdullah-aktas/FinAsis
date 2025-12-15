#!/bin/bash
# Cloud Shell'de hızlı build scripti
# Kullanım: bash scripts/quick-build-cloud-shell.sh

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
REPOSITORY="finasis-app"
IMAGE_NAME="finasis-api"

echo "🚀 Cloud Build API kontrolü ve build başlatılıyor..."
echo ""

# 1. Cloud Build API'sini etkinleştir
echo "📡 Cloud Build API etkinleştiriliyor..."
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID

echo "⏳ API'nin etkinleşmesi için 10 saniye bekleniyor..."
sleep 10

# 2. Git pull
cd ~/FinAsis
git pull origin main

# 3. Commit SHA'sını al
COMMIT_SHA=$(git rev-parse --short HEAD)
IMAGE_TAG="${COMMIT_SHA}"
FULL_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo ""
echo "📦 Build bilgileri:"
echo "   Commit SHA: $COMMIT_SHA"
echo "   Image: $FULL_IMAGE"
echo ""

# 4. Cloud Build submit
echo "🔨 Docker image build ediliyor..."
gcloud builds submit \
  --tag="$FULL_IMAGE" \
  --project=$PROJECT_ID \
  --region=$REGION

echo ""
echo "✅ Build tamamlandı!"
echo "📦 Image: $FULL_IMAGE"
echo ""
echo "💡 Şimdi deploy için:"
echo "   bash scripts/deploy-cloud-run-manual.sh"
echo ""

