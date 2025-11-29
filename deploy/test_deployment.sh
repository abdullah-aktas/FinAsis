#!/bin/bash
# Deployment Test ve Doğrulama Scripti
# Bu script deployment'ın başarılı olup olmadığını kontrol eder

set -e

PROJECT_ID="${PROJECT_ID:-finasis-478502}"
REGION="${REGION:-europe-west1}"
SERVICE_NAME="${SERVICE_NAME:-finasis-prod}"

echo "🧪 Deployment Test ve Doğrulama"
echo "================================"
echo ""

# 1. Servis URL'sini al
echo "📋 1. Servis URL'sini Alıyorum..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" 2>/dev/null || echo "")

if [ -z "$SERVICE_URL" ]; then
    echo "❌ Servis bulunamadı: $SERVICE_NAME"
    exit 1
fi

echo "✅ Servis URL: $SERVICE_URL"
echo ""

# 2. Son revision'ı kontrol et
echo "📋 2. Son Revision Bilgileri"
echo "-------------------"
LATEST_REVISION=$(gcloud run revisions list \
    --service="$SERVICE_NAME" \
    --region="$REGION" \
    --limit=1 \
    --sort-by=~metadata.creationTimestamp \
    --format="value(metadata.name)" 2>/dev/null || echo "")

if [ -n "$LATEST_REVISION" ]; then
    echo "✅ Son Revision: $LATEST_REVISION"
    
    REVISION_IMAGE=$(gcloud run revisions describe "$LATEST_REVISION" \
        --region="$REGION" \
        --format="value(spec.containers[0].image)" 2>/dev/null || echo "")
    REVISION_CREATED=$(gcloud run revisions describe "$LATEST_REVISION" \
        --region="$REGION" \
        --format="value(metadata.creationTimestamp)" 2>/dev/null || echo "")
    REVISION_STATUS=$(gcloud run revisions describe "$LATEST_REVISION" \
        --region="$REGION" \
        --format="value(status.conditions[0].status)" 2>/dev/null || echo "")
    
    echo "   Image: $REVISION_IMAGE"
    echo "   Oluşturulma: $REVISION_CREATED"
    echo "   Durum: $REVISION_STATUS"
    
    # Image tag'ini kontrol et
    if echo "$REVISION_IMAGE" | grep -q ":latest"; then
        echo "   ⚠️  Image 'latest' tag'i kullanıyor (timestamp tag önerilir)"
    fi
else
    echo "❌ Revision bulunamadı"
    exit 1
fi
echo ""

# 3. Health Check
echo "📋 3. Health Check"
echo "-------------------"
echo "   Servis URL'sine istek gönderiliyor: $SERVICE_URL"
HTTP_CODE=$(curl -s -o /tmp/health_check_response.txt -w "%{http_code}" \
    --max-time 10 \
    "$SERVICE_URL" || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Servis yanıt veriyor (HTTP 200)"
elif [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Servis yönlendirme yapıyor (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "❌ Servis yanıt vermiyor (timeout veya bağlantı hatası)"
    exit 1
else
    echo "⚠️  Servis beklenmeyen yanıt veriyor (HTTP $HTTP_CODE)"
    echo "   Yanıt içeriği:"
    head -20 /tmp/health_check_response.txt 2>/dev/null || echo "   Yanıt okunamadı"
fi
echo ""

# 4. Log Kontrolü
echo "📋 4. Son Loglar"
echo "-------------------"
echo "   Son 10 log satırı:"
gcloud run services logs read "$SERVICE_NAME" \
    --region="$REGION" \
    --limit=10 \
    --format="table(timestamp,severity,textPayload)" 2>/dev/null || echo "   Log okunamadı"
echo ""

# 5. Environment Variables Kontrolü
echo "📋 5. Environment Variables"
echo "-------------------"
ENV_VARS=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(spec.template.spec.containers[0].env[].name)" 2>/dev/null || echo "")

if [ -n "$ENV_VARS" ]; then
    echo "✅ Environment variables mevcut:"
    echo "$ENV_VARS" | while read -r var; do
        if [ -n "$var" ]; then
            echo "   - $var"
        fi
    done
else
    echo "⚠️  Environment variables bulunamadı"
fi
echo ""

# 6. Build Durumu Kontrolü
echo "📋 6. Son Build Durumu"
echo "-------------------"
LAST_BUILD=$(gcloud builds list \
    --limit=1 \
    --sort-by=~createTime \
    --format="value(id,status,createTime)" 2>/dev/null || echo "")

if [ -n "$LAST_BUILD" ]; then
    BUILD_ID=$(echo "$LAST_BUILD" | cut -d' ' -f1)
    BUILD_STATUS=$(echo "$LAST_BUILD" | cut -d' ' -f2)
    BUILD_TIME=$(echo "$LAST_BUILD" | cut -d' ' -f3-)
    
    echo "   Son Build ID: $BUILD_ID"
    echo "   Durum: $BUILD_STATUS"
    echo "   Zaman: $BUILD_TIME"
    
    if [ "$BUILD_STATUS" = "SUCCESS" ]; then
        echo "   ✅ Build başarılı"
    elif [ "$BUILD_STATUS" = "FAILURE" ]; then
        echo "   ❌ Build başarısız"
        echo "   Detaylar için: gcloud builds log $BUILD_ID"
    else
        echo "   ⚠️  Build durumu: $BUILD_STATUS"
    fi
else
    echo "   ⚠️  Build bulunamadı"
fi
echo ""

# 7. Özet
echo "📋 7. Test Özeti"
echo "-------------------"
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    if [ "$REVISION_STATUS" = "True" ]; then
        echo "✅ Deployment başarılı görünüyor!"
        echo "   - Servis çalışıyor"
        echo "   - Revision aktif"
        echo "   - Health check başarılı"
    else
        echo "⚠️  Deployment tamamlanmış ancak revision durumu kontrol edilmeli"
    fi
else
    echo "❌ Deployment sorunlu görünüyor"
    echo "   - Servis yanıt vermiyor veya hata veriyor"
    echo "   - Logları kontrol edin: gcloud run services logs read $SERVICE_NAME --region=$REGION"
fi
echo ""

