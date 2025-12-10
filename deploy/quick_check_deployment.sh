#!/bin/bash
# Hızlı deployment durumu kontrolü - Git pull gerektirmez
# Cloud Shell'de direkt çalıştırılabilir

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
  --limit=1 2>/dev/null || echo "")

if [ -z "$LATEST_REVISION" ]; then
  echo "   ❌ Revision bulunamadı!"
  exit 1
fi

echo "   ✅ Son revision: $LATEST_REVISION"
echo ""

# 2. Environment variables kontrolü (SECRET_KEY ve DB_PASSWORD)
echo "🔧 2. Environment variables kontrolü:"
ENV_VARS=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(spec.template.spec.containers[0].env)" 2>/dev/null || echo "")

if echo "$ENV_VARS" | grep -q "DJANGO_SECRET_KEY"; then
  SECRET_KEY_LEN=$(echo "$ENV_VARS" | grep "DJANGO_SECRET_KEY" | sed 's/.*value=\([^,}]*\).*/\1/' | wc -c || echo "0")
  if [ "$SECRET_KEY_LEN" -gt 10 ]; then
    echo "   ✅ DJANGO_SECRET_KEY: Set edilmiş (${SECRET_KEY_LEN} karakter)"
  else
    echo "   ⚠️  DJANGO_SECRET_KEY: Boş veya çok kısa"
  fi
else
  echo "   ❌ DJANGO_SECRET_KEY: Bulunamadı!"
fi

if echo "$ENV_VARS" | grep -q "DJANGO_DB_PASSWORD"; then
  echo "   ✅ DJANGO_DB_PASSWORD: Set edilmiş"
else
  echo "   ❌ DJANGO_DB_PASSWORD: Bulunamadı!"
fi
echo ""

# 3. Son loglar (hata ve başlangıç)
echo "📋 3. Son loglar (SIGTERM, ERROR, Exception, Gunicorn başlangıcı):"
echo ""
gcloud run services logs read $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --limit=100 \
  --format="value(textPayload)" 2>/dev/null | \
  grep -E "(SIGTERM|ERROR|Exception|Traceback|Starting Gunicorn|FinAsis API server|SECRET_KEY|PORT is set)" | \
  head -30 || echo "   ⚠️  Loglar alınamadı"
echo ""

# 4. Servis URL ve health check
echo "🌐 4. Servis URL ve Health Check:"
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
echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --limit=200 | grep -E '(ERROR|Exception|Traceback)'"

