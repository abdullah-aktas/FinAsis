#!/bin/bash
# HTTP 400 Hatası İçin Detaylı Kontrol
# Cloud Shell'de çalıştırın

set -euo pipefail

PROJECT_ID="finasis-478502"
SERVICE_NAME="finasis-prod"
REGION="europe-west1"

echo "=========================================="
echo "🔍 HTTP 400 Hatası Detaylı Kontrol"
echo "=========================================="
echo ""

# 1. Servis URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(status.url)" 2>/dev/null || echo "")

echo "🌐 Servis URL: $SERVICE_URL"
echo ""

# 2. Son Revision
echo "📋 Son Revision:"
LATEST_REVISION=$(gcloud run revisions list \
    --service=$SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --limit=1 \
    --format="value(name)" 2>/dev/null || echo "")

if [ -n "$LATEST_REVISION" ]; then
    echo "   ✅ $LATEST_REVISION"
else
    echo "   ❌ Revision bulunamadı"
fi
echo ""

# 3. Environment Variables (CSRF ve Database)
echo "🔧 Kritik Environment Variables:"
ENV_JSON=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="json" 2>/dev/null || echo "{}")

echo "$ENV_JSON" | jq -r '.spec.template.spec.containers[0].env[]? | select(.name | test("DJANGO_|CSRF|ALLOWED")) | "   \(.name)=\(.value)"' 2>/dev/null || echo "   (jq yok, JSON parse edilemedi)"
echo ""

# 4. Son Loglar (Django hataları)
echo "📋 Son Loglar (Django/CSRF/400 hataları):"
echo "   (Son 50 log satırı, 400/CSRF/DisallowedHost ile ilgili)"
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
    --limit=50 \
    --project=$PROJECT_ID \
    --format="value(textPayload,jsonPayload.message)" 2>/dev/null | \
    grep -iE "(400|bad.request|csrf|disallowedhost|allowed.host|middleware)" || echo "   (İlgili log bulunamadı)"
echo ""

# 5. Health Endpoint Testi (Detaylı)
echo "🧪 Health Endpoint Testi:"
echo "   GET $SERVICE_URL/health/"
echo ""

HEALTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}\nTIME:%{time_total}" "$SERVICE_URL/health/" 2>/dev/null || echo "")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
RESPONSE_TIME=$(echo "$HEALTH_RESPONSE" | grep "TIME:" | cut -d: -f2)
BODY=$(echo "$HEALTH_RESPONSE" | sed '/HTTP_CODE:/d' | sed '/TIME:/d')

echo "   HTTP Status: $HTTP_CODE"
echo "   Response Time: ${RESPONSE_TIME}s"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ HTTP 200 OK"
    if command -v jq &> /dev/null; then
        echo "   📋 JSON Response:"
        echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
    else
        echo "   📋 Response:"
        echo "$BODY" | head -20
    fi
elif [ "$HTTP_CODE" = "400" ]; then
    echo "   ❌ HTTP 400 Bad Request"
    echo "   📋 Response Body:"
    echo "$BODY"
    echo ""
    echo "   💡 Olası nedenler:"
    echo "      1. CSRF middleware sorunu"
    echo "      2. ALLOWED_HOSTS sorunu"
    echo "      3. Middleware exception"
    echo "      4. Request format sorunu"
elif [ "$HTTP_CODE" = "503" ]; then
    echo "   ❌ HTTP 503 Service Unavailable"
    echo "   💡 Database bağlantı sorunu olabilir"
else
    echo "   ⚠️  HTTP $HTTP_CODE"
    echo "   📋 Response:"
    echo "$BODY" | head -10
fi
echo ""

# 6. Cloud SQL Bağlantı Kontrolü
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

# 7. Öneriler
echo "=========================================="
echo "💡 Öneriler:"
echo "=========================================="
echo ""
if [ "$HTTP_CODE" = "400" ]; then
    echo "1. CSRF sorunu olabilir - views_health.py'de @csrf_exempt var mı kontrol edin"
    echo "2. ALLOWED_HOSTS'ta Cloud Run hostname'i var mı kontrol edin"
    echo "3. Son deployment'ta yeni kodlar deploy edildi mi kontrol edin"
    echo "4. Logları detaylı inceleyin:"
    echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=100 --project=$PROJECT_ID"
else
    echo "✅ HTTP $HTTP_CODE - Sorun çözülmüş olabilir!"
fi
echo ""

