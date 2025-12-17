#!/bin/bash
# Cloud Shell'de yeni build ve deployment scripti
# Kullanım: bash scripts/build-and-deploy-cloud-shell.sh

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
REPOSITORY="finasis-app"
IMAGE_NAME="finasis-api"

echo "🚀 Yeni Build ve Deployment Başlatılıyor..."
echo ""

# 1. Git durumunu kontrol et
cd ~/FinAsis
git pull origin main

# 2. Son commit SHA'sını al
COMMIT_SHA=$(git rev-parse --short HEAD)
IMAGE_TAG="${COMMIT_SHA}"
FULL_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "📦 Build bilgileri:"
echo "   Commit SHA: $COMMIT_SHA"
echo "   Image: $FULL_IMAGE"
echo ""

# 3. Docker build ve push
echo "🔨 Docker image build ediliyor..."
gcloud builds submit \
  --tag="$FULL_IMAGE" \
  --project=$PROJECT_ID \
  --region=$REGION

echo ""
echo "✅ Build tamamlandı!"
echo ""

# 4. Project number'ı al
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# 5. Secret'ları al (Secret Manager'dan veya kullanıcıdan)
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

# 6. Environment variables
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

# 7. Mevcut host'u ekle
EXISTING_HOST=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(status.url)" 2>/dev/null | sed 's|https\?://||' || echo "")

if [ -n "$EXISTING_HOST" ]; then
  ENV_VARS="$ENV_VARS,CLOUD_RUN_HOST=$EXISTING_HOST"
  echo "✅ CLOUD_RUN_HOST eklendi: $EXISTING_HOST"
fi

echo ""

# 8. Service account'u al (idempotent - hata durumunda fallback)
echo "🔍 Service account kontrol ediliyor..."
SERVICE_ACCOUNT=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(spec.template.spec.serviceAccountName)" 2>/dev/null || echo "")

# Eğer service account yoksa, default compute service account'u kullan
if [ -z "$SERVICE_ACCOUNT" ]; then
  COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
  # Service account'un var olup olmadığını kontrol et
  if gcloud iam service-accounts describe "$COMPUTE_SA" --project=$PROJECT_ID &>/dev/null; then
    SERVICE_ACCOUNT="$COMPUTE_SA"
    echo "✅ Default compute service account kullanılıyor: $SERVICE_ACCOUNT"
  else
    # Service account yoksa, Cloud Run default'unu kullan (boş bırak)
    echo "⚠️  Default compute service account mevcut değil, Cloud Run default kullanılacak"
    SERVICE_ACCOUNT=""
  fi
else
  echo "✅ Mevcut service account kullanılıyor: $SERVICE_ACCOUNT"
fi

# 9. Deploy
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

# 10. Service URL'ini göster
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

