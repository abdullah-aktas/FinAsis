#!/bin/bash
# Cloud Shell'de manuel Cloud Run deployment scripti
# Kullanım: bash scripts/deploy-cloud-run-manual.sh

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
REPOSITORY="finasis-app"
IMAGE_NAME="finasis-api"

echo "🚀 Cloud Run Manuel Deployment Başlatılıyor..."
echo ""

# 1. Proje ve region kontrolü
echo "📋 Proje Bilgileri:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: $SERVICE_NAME"
echo ""

# 2. Project number'ı al
echo "🔍 Project number alınıyor..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
echo "   Project Number: $PROJECT_NUMBER"
echo ""

# 3. Mevcut service URL'ini al (varsa)
echo "🔍 Mevcut service kontrol ediliyor..."
EXISTING_HOST=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(status.url)" 2>/dev/null | sed 's|https\?://||' || echo "")

if [ -n "$EXISTING_HOST" ]; then
  echo "   ✅ Mevcut service bulundu: $EXISTING_HOST"
else
  echo "   ℹ️  Service henüz oluşturulmamış"
fi
echo ""

# 4. En son image'ı bul
echo "🔍 En son Docker image aranıyor..."
LATEST_IMAGE=$(gcloud artifacts docker images list \
  ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME} \
  --project=$PROJECT_ID \
  --format="value(package)" \
  --sort-by=~CREATE_TIME \
  --limit=1 2>/dev/null || echo "")

if [ -z "$LATEST_IMAGE" ]; then
  echo "   ⚠️  Image bulunamadı, son commit SHA kullanılacak"
  IMAGE_TAG=$(git rev-parse --short HEAD 2>/dev/null || echo "latest")
  DEPLOY_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"
else
  DEPLOY_IMAGE="$LATEST_IMAGE"
fi

echo "   📦 Image: $DEPLOY_IMAGE"
echo ""

# 5. Environment variables hazırla
echo "🔧 Environment variables hazırlanıyor..."

# Secret'ları kullanıcıdan al
if [ -z "${DJANGO_SECRET_KEY:-}" ]; then
  echo "   ⚠️  DJANGO_SECRET_KEY bulunamadı"
  read -sp "   🔑 DJANGO_SECRET_KEY girin: " DJANGO_SECRET_KEY
  echo ""
fi

if [ -z "${DJANGO_DB_PASSWORD:-}" ]; then
  echo "   ⚠️  DJANGO_DB_PASSWORD bulunamadı"
  read -sp "   🔑 DJANGO_DB_PASSWORD girin: " DJANGO_DB_PASSWORD
  echo ""
fi

# Service account'u al (idempotent - hata durumunda fallback)
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
    echo "   ✅ Default compute service account kullanılıyor: $SERVICE_ACCOUNT"
  else
    # Service account yoksa, Cloud Run default'unu kullan (boş bırak)
    echo "   ⚠️  Default compute service account mevcut değil, Cloud Run default kullanılacak"
    SERVICE_ACCOUNT=""
  fi
else
  echo "   ✅ Mevcut service account kullanılıyor: $SERVICE_ACCOUNT"
fi
echo ""

# Environment variables string'i oluştur
ENV_VARS="MPLCONFIGDIR=/tmp/matplotlib-cache,PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1"
ENV_VARS="$ENV_VARS,DJANGO_DB_ENGINE=django.db.backends.postgresql"
ENV_VARS="$ENV_VARS,DJANGO_DB_NAME=finasis"
ENV_VARS="$ENV_VARS,DJANGO_DB_USER=finasis-app"
ENV_VARS="$ENV_VARS,DJANGO_DB_HOST=/cloudsql/finasis-478502:europe-west1:finasis-db"
ENV_VARS="$ENV_VARS,CLOUD_SQL_CONNECTION_NAME=finasis-478502:europe-west1:finasis-db"
ENV_VARS="$ENV_VARS,DJANGO_DEBUG=0"
ENV_VARS="$ENV_VARS,RUN_DB_MIGRATIONS=true"
ENV_VARS="$ENV_VARS,GOOGLE_CLOUD_PROJECT_NUMBER=$PROJECT_NUMBER"
ENV_VARS="$ENV_VARS,DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY"
ENV_VARS="$ENV_VARS,DJANGO_DB_PASSWORD=$DJANGO_DB_PASSWORD"

if [ -n "$EXISTING_HOST" ]; then
  ENV_VARS="$ENV_VARS,CLOUD_RUN_HOST=$EXISTING_HOST"
  echo "   ✅ CLOUD_RUN_HOST eklendi: $EXISTING_HOST"
fi

echo ""

# 6. Deployment
echo "🚀 Cloud Run'a deploy ediliyor..."
echo "   Image: $DEPLOY_IMAGE"
echo "   Service: $SERVICE_NAME"
echo "   Region: $REGION"
echo ""

gcloud run deploy $SERVICE_NAME \
  --image="$DEPLOY_IMAGE" \
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

# 7. Service URL'ini göster
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

