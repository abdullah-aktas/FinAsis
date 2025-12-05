#!/bin/bash
# Production'da health check endpoint'lerini test et

SITE_URL="https://finasis.com.tr"

echo "🔍 Production Health Check Test"
echo "================================"
echo "Site: $SITE_URL"
echo ""

# 1. Basit Health Check
echo "📋 1. Basit Health Check (/health/)"
echo "-----------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$SITE_URL/health/")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ HTTP $HTTP_CODE"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo "❌ HTTP $HTTP_CODE"
    echo "$BODY" | head -20
fi

echo ""
echo "📋 2. Detaylı Health Check (/health/detailed/)"
echo "-----------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$SITE_URL/health/detailed/")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ HTTP $HTTP_CODE"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo "❌ HTTP $HTTP_CODE"
    echo "$BODY" | head -20
fi

echo ""
echo "📋 3. Site Status (/health/status/)"
echo "-----------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$SITE_URL/health/status/")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ HTTP $HTTP_CODE"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo "❌ HTTP $HTTP_CODE"
    echo "$BODY" | head -20
fi

echo ""
echo "================================"
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Health check endpoint'leri çalışıyor!"
else
    echo "⚠️  Health check endpoint'leri henüz aktif değil veya sorun var."
    echo "   Cloud Run servisinin yeni versiyonunun deploy edilmesini bekleyin (2-5 dakika)."
fi

