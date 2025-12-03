#!/bin/bash
# finasis.com.tr Site Health Check Script
# Cloud Shell veya lokal ortamda çalıştırılabilir

set -euo pipefail

SITE_URL="${SITE_URL:-https://finasis.com.tr}"
TIMEOUT=10

echo "🔍 finasis.com.tr Site Health Check"
echo "===================================="
echo "Site URL: $SITE_URL"
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Basit Health Check
echo "📋 1. Basit Health Check"
echo "-------------------"
HEALTH_URL="${SITE_URL}/health/"
HTTP_CODE=$(curl -s -o /tmp/health_response.json -w "%{http_code}" \
    --max-time $TIMEOUT \
    "$HEALTH_URL" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Health check başarılı (HTTP $HTTP_CODE)${NC}"
    
    # JSON response'u parse et
    if command -v jq &> /dev/null; then
        STATUS=$(jq -r '.status' /tmp/health_response.json 2>/dev/null || echo "unknown")
        echo "   Durum: $STATUS"
        
        DB_STATUS=$(jq -r '.checks.database.status' /tmp/health_response.json 2>/dev/null || echo "unknown")
        DB_TIME=$(jq -r '.checks.database.response_time_ms' /tmp/health_response.json 2>/dev/null || echo "N/A")
        echo "   Database: $DB_STATUS (${DB_TIME}ms)"
        
        CACHE_STATUS=$(jq -r '.checks.cache.status' /tmp/health_response.json 2>/dev/null || echo "unknown")
        echo "   Cache: $CACHE_STATUS"
    else
        echo "   Response:"
        cat /tmp/health_response.json | head -20
    fi
elif [ "$HTTP_CODE" = "000" ]; then
    echo -e "${RED}❌ Site yanıt vermiyor (timeout veya bağlantı hatası)${NC}"
    exit 1
else
    echo -e "${YELLOW}⚠️  Beklenmeyen yanıt (HTTP $HTTP_CODE)${NC}"
    cat /tmp/health_response.json | head -20
fi
echo ""

# 2. Detaylı Health Check
echo "📋 2. Detaylı Health Check"
echo "-------------------"
DETAILED_URL="${SITE_URL}/health/detailed/"
HTTP_CODE=$(curl -s -o /tmp/health_detailed.json -w "%{http_code}" \
    --max-time $TIMEOUT \
    "$DETAILED_URL" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Detaylı health check başarılı${NC}"
    
    if command -v jq &> /dev/null; then
        STATUS=$(jq -r '.status' /tmp/health_detailed.json 2>/dev/null || echo "unknown")
        echo "   Genel Durum: $STATUS"
        
        echo ""
        echo "   Database Detayları:"
        jq -r '.checks.database | "     - Durum: \(.status)\n     - Yanıt Süresi: \(.response_time_ms)ms\n     - Vendor: \(.vendor)\n     - Aktif Bağlantılar: \(.active_connections // "N/A")"' /tmp/health_detailed.json 2>/dev/null || echo "     Parse edilemedi"
        
        echo ""
        echo "   Cache Detayları:"
        jq -r '.checks.cache | "     - Durum: \(.status)\n     - Yanıt Süresi: \(.response_time_ms)ms"' /tmp/health_detailed.json 2>/dev/null || echo "     Parse edilemedi"
        
        echo ""
        echo "   Sistem Bilgileri:"
        RECENT_ERRORS=$(jq -r '.system_info.recent_errors_5min // "N/A"' /tmp/health_detailed.json 2>/dev/null)
        ACTIVE_SESSIONS=$(jq -r '.system_info.active_sessions // "N/A"' /tmp/health_detailed.json 2>/dev/null)
        echo "     - Son 5 dakikadaki hatalar: $RECENT_ERRORS"
        echo "     - Aktif oturumlar: $ACTIVE_SESSIONS"
    else
        echo "   Response:"
        cat /tmp/health_detailed.json | head -30
    fi
else
    echo -e "${YELLOW}⚠️  Detaylı health check başarısız (HTTP $HTTP_CODE)${NC}"
fi
echo ""

# 3. Site Status
echo "📋 3. Site Status"
echo "-------------------"
STATUS_URL="${SITE_URL}/health/status/"
HTTP_CODE=$(curl -s -o /tmp/status_response.json -w "%{http_code}" \
    --max-time $TIMEOUT \
    "$STATUS_URL" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Site status alındı${NC}"
    
    if command -v jq &> /dev/null; then
        STATUS=$(jq -r '.status' /tmp/status_response.json 2>/dev/null || echo "unknown")
        echo "   Genel Durum: $STATUS"
        
        echo ""
        echo "   Modül Durumları:"
        jq -r '.modules[] | "     - \(.name) (\(.code)): \(.status)"' /tmp/status_response.json 2>/dev/null || echo "     Parse edilemedi"
    else
        echo "   Response:"
        cat /tmp/status_response.json | head -20
    fi
else
    echo -e "${YELLOW}⚠️  Site status alınamadı (HTTP $HTTP_CODE)${NC}"
fi
echo ""

# 4. Ana Sayfa Kontrolü
echo "📋 4. Ana Sayfa Kontrolü"
echo "-------------------"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    --max-time $TIMEOUT \
    "$SITE_URL" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Ana sayfa erişilebilir (HTTP $HTTP_CODE)${NC}"
elif [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "${GREEN}✅ Ana sayfa yönlendirme yapıyor (HTTP $HTTP_CODE)${NC}"
elif [ "$HTTP_CODE" = "000" ]; then
    echo -e "${RED}❌ Ana sayfa yanıt vermiyor${NC}"
else
    echo -e "${YELLOW}⚠️  Ana sayfa beklenmeyen yanıt (HTTP $HTTP_CODE)${NC}"
fi
echo ""

# 5. Özet
echo "📊 Özet"
echo "-------------------"
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "${GREEN}✅ Site genel olarak çalışıyor görünüyor${NC}"
    echo ""
    echo "💡 Health check endpoint'leri:"
    echo "   - Basit: ${SITE_URL}/health/"
    echo "   - Detaylı: ${SITE_URL}/health/detailed/"
    echo "   - Status: ${SITE_URL}/health/status/"
else
    echo -e "${RED}❌ Site sorunlu görünüyor!${NC}"
    echo ""
    echo "🔧 Kontrol edilmesi gerekenler:"
    echo "   1. Cloud Run servisinin çalıştığından emin olun"
    echo "   2. Logları kontrol edin: gcloud run services logs read finasis-prod --region=europe-west1"
    echo "   3. Environment variables'ları kontrol edin"
    exit 1
fi

# Temizlik
rm -f /tmp/health_response.json /tmp/health_detailed.json /tmp/status_response.json

