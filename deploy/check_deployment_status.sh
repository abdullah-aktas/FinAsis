#!/bin/bash
# Deployment durumunu kontrol et
# Cloud Shell'de çalıştırın: bash deploy/check_deployment_status.sh

set -euo pipefail

PROJECT_ID="finasis-478502"
SERVICE_NAME="finasis-prod"
REGION="europe-west1"

echo "🔍 Deployment Durumu Kontrolü"
echo "=============================="
echo ""

# 1. Son revision'ı al
echo "📋 1. Son revision bilgisi:"
LATEST_REVISION=$(gcloud run revisions list \
  --service=$SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(name)" \
  --limit=1)

if [ -z "$LATEST_REVISION" ]; then
  echo "   ❌ Revision bulunamadı!"
  exit 1
fi

echo "   ✅ Son revision: $LATEST_REVISION"
echo ""

# 2. Revision durumu
echo "📊 2. Revision durumu:"
gcloud run revisions describe "$LATEST_REVISION" \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="table(status.conditions[0].type,status.conditions[0].status,status.conditions[0].message)" || true
echo ""

# 3. Environment variables kontrolü
echo "🔧 3. Environment variables kontrolü:"
gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(spec.template.spec.containers[0].env)" | grep -E "(DJANGO_SECRET_KEY|DJANGO_DB_PASSWORD)" | head -2 || echo "   ⚠️  SECRET_KEY veya DB_PASSWORD bulunamadı"
echo ""

# 4. Son loglar (son 50 satır)
echo "📋 4. Son loglar (son 50 satır):"
echo "   (SIGTERM, ERROR, Exception, Traceback aranıyor...)"
echo ""
gcloud run services logs read $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --limit=50 \
  --format="table(timestamp,severity,textPayload)" 2>/dev/null | head -60 || echo "   ⚠️  Loglar alınamadı"
echo ""

# 5. Hata logları
echo "❌ 5. Hata logları (ERROR ve CRITICAL):"
gcloud run services logs read $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --limit=100 \
  --format="value(textPayload)" 2>/dev/null | grep -E "(ERROR|CRITICAL|Exception|Traceback|SIGTERM)" | head -20 || echo "   ✅ Hata logu bulunamadı"
echo ""

# 6. Servis URL ve health check
echo "🌐 6. Servis URL:"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
  echo "   URL: $SERVICE_URL"
  echo ""
  echo "   🏥 Health check:"
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$SERVICE_URL" 2>/dev/null || echo "000")
  if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "   ✅ HTTP $HTTP_CODE - Servis çalışıyor!"
  else
    echo "   ⚠️  HTTP $HTTP_CODE - Servis yanıt vermiyor veya hata var"
  fi
else
  echo "   ❌ Servis URL alınamadı!"
fi

echo ""
echo "=============================="
echo "✅ Kontrol tamamlandı"
echo ""
echo "💡 Daha fazla log için:"
echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --limit=200"

