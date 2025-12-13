#!/bin/bash
# Cloud Build ile hızlı deployment scripti
# Cloud Shell'de çalıştırın: bash scripts/deploy-cloud-build.sh

set -e

echo "🚀 Cloud Build ile deployment başlatılıyor..."

PROJECT_ID="finasis-478502"
REGION="europe-west1"
REPOSITORY="finasis-app"
SERVICE="finasis-api"
CLOUD_RUN_SERVICE="finasis-prod"
IMAGE_TAG="latest"

# Proje dizinine geç
cd ~/FinAsis || { echo "❌ FinAsis dizini bulunamadı!"; exit 1; }

# Git durumunu kontrol et
echo "📊 Git durumu kontrol ediliyor..."
git status

# Son değişiklikleri al (opsiyonel)
read -p "Son değişiklikleri pull etmek ister misiniz? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git pull origin main
fi

# Cloud Build'i tetikle
echo "🔨 Cloud Build başlatılıyor..."
gcloud builds submit \
    --config=deploy/cloud_run/cloudbuild.yaml \
    --substitutions=_IMAGE_TAG=${IMAGE_TAG} \
    --project=${PROJECT_ID} \
    --region=${REGION}

echo "✅ Deployment tamamlandı!"

# Servis URL'ini göster
SERVICE_URL=$(gcloud run services describe ${CLOUD_RUN_SERVICE} \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --format="value(status.url)")

echo "🌐 Servis URL: ${SERVICE_URL}"
echo "🏥 Health check: ${SERVICE_URL}/health/"

