#!/bin/bash
# Hızlı düzeltme - ALLOWED_HOSTS ve DEBUG için
# Cloud Shell'de çalıştır

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
CLOUD_SQL_INSTANCE="finasis-478502:europe-west1:finasis-db"

echo "🔧 Cloud Run servisi hızlı düzeltme yapılıyor..."

gcloud config set project "$PROJECT_ID"

# Mevcut Cloud Run URL'ini al
CURRENT_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --platform=managed \
  --region="$REGION" \
  --format='value(status.url)')

CURRENT_HOST=$(echo "$CURRENT_URL" | sed 's|https\?://||' | sed 's|/.*||')

echo "📋 Mevcut URL: $CURRENT_URL"
echo "📋 Host: $CURRENT_HOST"

# Mevcut environment variables'ı al
CURRENT_ENV_RAW=$(gcloud run services describe "$SERVICE_NAME" \
  --platform=managed \
  --region="$REGION" \
  --format='json' | jq -r '.spec.template.spec.containers[0].env[] | "\(.name)=\(.value // "")"' 2>/dev/null || echo "")

# Yeni environment variables
NEW_ENV_VARS="MPLCONFIGDIR=/tmp/matplotlib-cache,PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_INSTANCE,DJANGO_DEBUG=False,CLOUD_RUN_URL=$CURRENT_URL,CLOUD_RUN_HOST=$CURRENT_HOST,DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,finasis.com.tr,www.finasis.com.tr,$CURRENT_HOST"

echo ""
echo "🚀 Cloud Run servisi güncelleniyor..."

# Önce Cloud SQL connection'ı kontrol et
EXISTING_CLOUDSQL=$(gcloud run services describe "$SERVICE_NAME" \
  --platform=managed \
  --region="$REGION" \
  --format='value(spec.template.metadata.annotations."run.googleapis.com/cloudsql-instances")' 2>/dev/null || echo "")

if [ -z "$EXISTING_CLOUDSQL" ]; then
  echo "📝 Cloud SQL bağlantısı ekleniyor..."
  gcloud run services update "$SERVICE_NAME" \
    --platform=managed \
    --region="$REGION" \
    --add-cloudsql-instances="$CLOUD_SQL_INSTANCE" \
    --set-env-vars="$NEW_ENV_VARS"
else
  echo "📝 Environment variables güncelleniyor..."
  gcloud run services update "$SERVICE_NAME" \
    --platform=managed \
    --region="$REGION" \
    --set-env-vars="$NEW_ENV_VARS"
fi

echo ""
echo "✅ Güncelleme tamamlandı!"
echo "🌐 URL: $CURRENT_URL"
echo ""
echo "📊 Servis durumu:"
gcloud run services describe "$SERVICE_NAME" \
  --platform=managed \
  --region="$REGION" \
  --format='table(status.url,status.latestReadyRevisionName,status.conditions[0].status)'

