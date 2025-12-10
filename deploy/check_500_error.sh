#!/bin/bash
# HTTP 500 Hatası Kontrol Scripti
# Cloud Shell'de çalıştırın

set -euo pipefail

PROJECT_ID="finasis-478502"
SERVICE_NAME="finasis-prod"
REGION="europe-west1"

echo "=========================================="
echo "🔍 HTTP 500 Hatası Detaylı Kontrol"
echo "=========================================="
echo ""

# 1. Son loglar (500, Exception, Traceback, ERROR)
echo "📋 Son Loglar (500/Exception/Traceback/ERROR):"
echo "   (Son 100 log satırı)"
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
  --limit=100 \
  --project=$PROJECT_ID \
  --format="value(textPayload,jsonPayload.message)" 2>/dev/null | \
  grep -iE "(500|exception|traceback|error|failed|operationalerror|improperlyconfigured)" | \
  head -30 || echo "   (İlgili log bulunamadı)"
echo ""

# 2. Son revision
echo "📋 Son Revision:"
LATEST_REVISION=$(gcloud run revisions list \
    --service=$SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --limit=1 \
    --format="value(name)" 2>/dev/null || echo "")

if [ -n "$LATEST_REVISION" ]; then
    echo "   ✅ $LATEST_REVISION"
    
    # Revision durumu
    REVISION_STATUS=$(gcloud run revisions describe $LATEST_REVISION \
        --region=$REGION \
        --project=$PROJECT_ID \
        --format="value(status.conditions[0].status)" 2>/dev/null || echo "")
    echo "   📊 Durum: $REVISION_STATUS"
else
    echo "   ❌ Revision bulunamadı"
fi
echo ""

# 3. Environment Variables (Database ve kritik ayarlar)
echo "🔧 Kritik Environment Variables:"
ENV_JSON=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="json" 2>/dev/null || echo "{}")

echo "$ENV_JSON" | jq -r '.spec.template.spec.containers[0].env[]? | select(.name | test("DJANGO_|CLOUD_|DATABASE")) | "   \(.name)=\(.value)"' 2>/dev/null || echo "   (jq yok, JSON parse edilemedi)"
echo ""

# 4. Cloud SQL Bağlantı Kontrolü
echo "🔌 Cloud SQL Bağlantı Kontrolü:"
CLOUD_SQL_INSTANCES=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(spec.template.spec.containers[0].cloudSqlInstances)" 2>/dev/null || echo "")

if [ -n "$CLOUD_SQL_INSTANCES" ]; then
    echo "   ✅ Cloud SQL instance bağlı: $CLOUD_SQL_INSTANCES"
else
    echo "   ❌ Cloud SQL instance bağlı değil!"
fi
echo ""

# 5. Health vs Ana Sayfa Karşılaştırması
echo "🧪 Endpoint Testleri:"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo "   🌐 Servis URL: $SERVICE_URL"
    echo ""
    
    # Health endpoint
    echo "   📊 Health Endpoint:"
    HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health/" 2>/dev/null || echo "000")
    if [ "$HEALTH_CODE" = "200" ]; then
        echo "      ✅ HTTP $HEALTH_CODE OK"
    else
        echo "      ❌ HTTP $HEALTH_CODE"
    fi
    
    # Ana sayfa
    echo "   📊 Ana Sayfa (/):"
    HOME_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/" 2>/dev/null || echo "000")
    if [ "$HOME_CODE" = "200" ]; then
        echo "      ✅ HTTP $HOME_CODE OK"
    else
        echo "      ❌ HTTP $HOME_CODE"
    fi
fi
echo ""

# 6. Öneriler
echo "=========================================="
echo "💡 Öneriler:"
echo "=========================================="
echo ""
if [ "$HOME_CODE" = "500" ]; then
    echo "1. Logları detaylı inceleyin (yukarıdaki çıktıya bakın)"
    echo "2. Database migration'ları kontrol edin:"
    echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --limit=50 | grep -i migration"
    echo "3. Static files kontrol edin:"
    echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --limit=50 | grep -i static"
    echo "4. Template hatalarını kontrol edin:"
    echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --limit=50 | grep -i template"
else
    echo "✅ HTTP $HOME_CODE - Sorun çözülmüş olabilir!"
fi
echo ""

