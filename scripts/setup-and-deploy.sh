#!/bin/bash
# Cloud Shell'de tam setup ve deployment scripti
# Kullanım: bash scripts/setup-and-deploy.sh

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
REPOSITORY="finasis-app"
IMAGE_NAME="finasis-api"

echo "🚀 Tam Setup ve Deployment Başlatılıyor..."
echo ""

# 1. Cloud Build API'sini etkinleştir
echo "📡 Cloud Build API etkinleştiriliyor..."
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID

echo "⏳ API'nin etkinleşmesi için 15 saniye bekleniyor..."
sleep 15

# 2. Git pull
cd ~/FinAsis
echo "📥 Git pull yapılıyor..."
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
echo "🔨 Docker image build ediliyor ve push ediliyor..."
gcloud builds submit \
  --tag="$FULL_IMAGE" \
  --project=$PROJECT_ID \
  --region=$REGION

echo ""
echo "✅ Build tamamlandı!"
echo ""

# 5. Project number'ı al
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# 6. Secret'ları al (Secret Manager'dan veya kullanıcıdan)
if [ -z "${DJANGO_SECRET_KEY:-}" ]; then
  echo "🔑 DJANGO_SECRET_KEY bulunamadı"
  read -sp "   DJANGO_SECRET_KEY girin: " DJANGO_SECRET_KEY
  echo ""
  export DJANGO_SECRET_KEY
fi

if [ -z "${DJANGO_DB_PASSWORD:-}" ]; then
  echo "🔑 DJANGO_DB_PASSWORD bulunamadı"
  read -sp "   DJANGO_DB_PASSWORD girin: " DJANGO_DB_PASSWORD
  echo ""
  export DJANGO_DB_PASSWORD
fi

# 7. Environment variables
ENV_VARS="MPLCONFIGDIR=/tmp/matplotlib-cache,PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1"
ENV_VARS="$ENV_VARS,DJANGO_DB_ENGINE=django.db.backends.postgresql"
ENV_VARS="$ENV_VARS,DJANGO_DB_NAME=finasis"
ENV_VARS="$ENV_VARS,DJANGO_DB_USER=finasis-app"
ENV_VARS="$ENV_VARS,DJANGO_DB_HOST=/cloudsql/finasis-478502:europe-west1:finasis-db"
ENV_VARS="$ENV_VARS,CLOUD_SQL_CONNECTION_NAME=finasis-478502:europe-west1:finasis-db"
ENV_VARS="$ENV_VARS,DJANGO_DEBUG=0,RUN_DB_MIGRATIONS=true"
ENV_VARS="$ENV_VARS,GOOGLE_CLOUD_PROJECT_NUMBER=$PROJECT_NUMBER"
ENV_VARS="$ENV_VARS,DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY"
ENV_VARS="$ENV_VARS,DJANGO_DB_PASSWORD=$DJANGO_DB_PASSWORD"

# 8. Mevcut host'u ekle
EXISTING_HOST=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(status.url)" 2>/dev/null | sed 's|https\?://||' || echo "")

if [ -n "$EXISTING_HOST" ]; then
  ENV_VARS="$ENV_VARS,CLOUD_RUN_HOST=$EXISTING_HOST"
  echo "✅ CLOUD_RUN_HOST eklendi: $EXISTING_HOST"
fi

echo ""

# 9. Service account'u al
SERVICE_ACCOUNT=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(spec.template.spec.serviceAccountName)" 2>/dev/null || \
  echo "${PROJECT_NUMBER}-compute@developer.gserviceaccount.com")

# 10. Deploy
echo "🚀 Cloud Run'a deploy ediliyor..."
gcloud run deploy $SERVICE_NAME \
  --image="$FULL_IMAGE" \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --execution-environment=gen2 \
  --memory=2Gi \
  --cpu=2 \
  --timeout=900 \
  --concurrency=40 \
  --min-instances=1 \
  --max-instances=10 \
  --service-account="$SERVICE_ACCOUNT" \
  --add-cloudsql-instances=finasis-478502:europe-west1:finasis-db \
  --cpu-boost \
  --cpu-throttling \
  --set-env-vars="$ENV_VARS" \
  --port=8080 \
  --project=$PROJECT_ID

echo ""
echo "✅ Deployment tamamlandı!"

# 11. Service URL'ini göster
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(status.url)")

echo ""
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "📋 Logları görmek için:"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --project=$PROJECT_ID --limit=50"
echo ""

