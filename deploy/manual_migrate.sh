#!/bin/bash
# Manuel Migration Çalıştırma (Cloud Run container'ına bağlanarak)
# Cloud Shell'de çalıştırın

set -euo pipefail

PROJECT_ID="finasis-478502"
SERVICE_NAME="finasis-prod"
REGION="europe-west1"

echo "=========================================="
echo "🔄 Manuel Database Migration"
echo "=========================================="
echo ""

# Mevcut environment variables'ı al
echo "🔍 Mevcut environment variables alınıyor..."
ENV_VARS=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="json" | jq -r '.spec.template.spec.containers[0].env[]? | "\(.name)=\(.value)"' | tr '\n' ',' | sed 's/,$//')

echo "✅ Environment variables alındı"
echo ""

# Cloud Run container'ında migration çalıştır
echo "🔄 Migration çalıştırılıyor..."
echo ""

# Cloud Run exec kullanarak migration çalıştır
gcloud run services update $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --update-env-vars="RUN_DB_MIGRATIONS=true" \
  --no-traffic

# Yeni revision'ı test et
echo "🧪 Yeni revision test ediliyor..."
sleep 5

# Migration'ları kontrol et
echo "📋 Migration durumu kontrol ediliyor..."
gcloud run services logs read $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --limit=20 | grep -iE "(migration|migrate|billing_module)" || echo "   (Migration log bulunamadı)"

echo ""
echo "✅ Migration tamamlandı!"
echo ""
echo "💡 Şimdi traffic'i geri yönlendirin:"
echo "   gcloud run services update $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --to-latest"

