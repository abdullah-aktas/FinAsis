#!/bin/bash
# Mevcut Cloud Run servisini güncelle - ALLOWED_HOSTS ve DEBUG düzeltmesi

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"

echo "🔧 Cloud Run servisi güncelleniyor..."

# Projeyi ayarla
gcloud config set project "$PROJECT_ID"

# Mevcut Cloud Run URL'ini al
CURRENT_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --platform=managed \
  --region="$REGION" \
  --format='value(status.url)')

echo "📋 Mevcut URL: $CURRENT_URL"

# Host adını çıkar (https:// kısmını kaldır)
CURRENT_HOST=$(echo "$CURRENT_URL" | sed 's|https\?://||' | sed 's|/.*||')
echo "📋 Host adı: $CURRENT_HOST"

# Cloud SQL instance adını bul
echo ""
echo "🔍 Cloud SQL instance'ları listeleniyor..."
gcloud sql instances list

echo ""
echo "⚠️  Cloud SQL instance adınızı girin (PROJECT_ID:REGION:INSTANCE_NAME formatında):"
read -p "Cloud SQL Connection Name: " CLOUD_SQL_INSTANCE

if [ -z "$CLOUD_SQL_INSTANCE" ]; then
  echo "❌ Cloud SQL instance adı girilmedi. Devam ediliyor (Cloud SQL olmadan)..."
  CLOUD_SQL_ARG=""
else
  CLOUD_SQL_ARG="--add-cloudsql-instances=$CLOUD_SQL_INSTANCE"
fi

# Mevcut environment variables'ı al
echo ""
echo "📥 Mevcut environment variables alınıyor..."
CURRENT_ENV=$(gcloud run services describe "$SERVICE_NAME" \
  --platform=managed \
  --region="$REGION" \
  --format='value(spec.template.spec.containers[0].env[].name,spec.template.spec.containers[0].env[].value)' | \
  grep -v "^$" | paste - - | awk '{print $1"="substr($0,index($0,$2))}')

# Yeni environment variables
NEW_ENV_VARS="MPLCONFIGDIR=/tmp/matplotlib-cache,PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_INSTANCE,DJANGO_DEBUG=False,CLOUD_RUN_URL=$CURRENT_URL,CLOUD_RUN_HOST=$CURRENT_HOST"

# Cloud Run servisini güncelle
echo ""
echo "🚀 Cloud Run servisi güncelleniyor..."
gcloud run services update "$SERVICE_NAME" \
  --platform=managed \
  --region="$REGION" \
  --set-env-vars="$NEW_ENV_VARS" \
  $CLOUD_SQL_ARG

echo ""
echo "✅ Güncelleme tamamlandı!"
echo "🌐 URL: $CURRENT_URL"
echo ""
echo "📊 Servis durumu:"
gcloud run services describe "$SERVICE_NAME" \
  --platform=managed \
  --region="$REGION" \
  --format='table(status.url,status.latestReadyRevisionName,status.conditions[0].status)'

