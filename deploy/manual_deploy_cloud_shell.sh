#!/bin/bash
# Cloud Shell'de Manuel Deployment Script
# Kullanım: bash deploy/manual_deploy_cloud_shell.sh

set -euo pipefail

# ============================================
# AYARLAR
# ============================================
PROJECT_ID="finasis-478502"
SERVICE_NAME="finasis-prod"
REGION="europe-west1"
REPOSITORY="finasis-app"
IMAGE_NAME="finasis-api"
SERVICE_ACCOUNT="github-actions-deploy@finasis-478502.iam.gserviceaccount.com"

# ============================================
# SECRET'LARI AYARLAYIN
# ============================================
# Bu değerleri kendi secret'larınızla değiştirin
# Secret Manager'dan alabilirsiniz veya direkt buraya yazabilirsiniz
echo "🔐 Secret'ları ayarlayın:"
read -sp "DJANGO_SECRET_KEY: " DJANGO_SECRET_KEY
echo ""
read -sp "DJANGO_DB_PASSWORD: " DJANGO_DB_PASSWORD
echo ""

if [ -z "$DJANGO_SECRET_KEY" ] || [ -z "$DJANGO_DB_PASSWORD" ]; then
  echo "❌ ERROR: DJANGO_SECRET_KEY ve DJANGO_DB_PASSWORD zorunludur!"
  exit 1
fi

echo "✅ Secret'lar ayarlandı (length: SECRET_KEY=${#DJANGO_SECRET_KEY} chars, DB_PASSWORD=${#DJANGO_DB_PASSWORD} chars)"

# ============================================
# PROJE AYARLARI
# ============================================
echo ""
echo "🔧 Proje ayarları yapılıyor..."
gcloud config set project "$PROJECT_ID"

# ============================================
# REPO KONTROLÜ
# ============================================
echo ""
echo "📂 Repo kontrolü..."
if [ ! -d "FinAsis" ]; then
  echo "📥 Repo clone ediliyor..."
  git clone https://github.com/abdullah-aktas/FinAsis.git
fi

cd FinAsis
git pull origin main

# ============================================
# DOCKER IMAGE BUILD VE PUSH
# ============================================
echo ""
echo "🐳 Docker image build ediliyor..."
COMMIT_SHA=$(git rev-parse --short HEAD)
IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${COMMIT_SHA}"

# Docker authentication
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# Build ve push
echo "🔨 Building image: $IMAGE_TAG"
gcloud builds submit --tag "$IMAGE_TAG" --project="$PROJECT_ID"

echo "✅ Image build edildi ve push edildi: $IMAGE_TAG"

# ============================================
# ENVIRONMENT VARIABLES HAZIRLAMA
# ============================================
echo ""
echo "🔧 Environment variables hazırlanıyor..."

ENV_VARS="MPLCONFIGDIR=/tmp/matplotlib-cache,PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1,DJANGO_DB_ENGINE=django.db.backends.postgresql,DJANGO_DB_NAME=finasis,DJANGO_DB_USER=finasis-app,DJANGO_DB_HOST=/cloudsql/finasis-478502:europe-west1:finasis-db,CLOUD_SQL_CONNECTION_NAME=finasis-478502:europe-west1:finasis-db,DJANGO_DEBUG=0"

# SECRET_KEY ve DB_PASSWORD'i ekle
ENV_VARS="$ENV_VARS,DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY"
ENV_VARS="$ENV_VARS,DJANGO_DB_PASSWORD=$DJANGO_DB_PASSWORD"

# ============================================
# CLOUD RUN DEPLOYMENT
# ============================================
echo ""
echo "🚀 Cloud Run'a deploy ediliyor..."

gcloud run deploy "$SERVICE_NAME" \
  --image="$IMAGE_TAG" \
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
  --service-account="$SERVICE_ACCOUNT" \
  --add-cloudsql-instances=finasis-478502:europe-west1:finasis-db \
  --cpu-boost \
  --cpu-throttling \
  --set-env-vars="$ENV_VARS" \
  --project="$PROJECT_ID"

# ============================================
# CLOUD_RUN_HOST GÜNCELLEMESİ
# ============================================
echo ""
echo "🌐 Service URL alınıyor..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format="value(status.url)")

CLOUD_RUN_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||')

echo "🔧 CLOUD_RUN_HOST güncelleniyor: $CLOUD_RUN_HOST"
gcloud run services update "$SERVICE_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --update-env-vars="CLOUD_RUN_HOST=$CLOUD_RUN_HOST"

# ============================================
# SONUÇ
# ============================================
echo ""
echo "=========================================="
echo "✅ Deployment tamamlandı!"
echo "=========================================="
echo "🌐 Servis URL: $SERVICE_URL"
echo "📋 Revision: $(gcloud run revisions list --service=$SERVICE_NAME --region=$REGION --project=$PROJECT_ID --limit=1 --format='value(name)')"
echo ""
echo "📊 Logları kontrol etmek için:"
echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --limit=50"
echo ""
echo "🔍 Health check:"
echo "   curl $SERVICE_URL/health/"
echo "=========================================="

