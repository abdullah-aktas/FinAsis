#!/bin/bash
# finasis.com.tr Sürekli Monitoring Script
# Belirli aralıklarla site durumunu kontrol eder

set -euo pipefail

SITE_URL="${SITE_URL:-https://finasis.com.tr}"
CHECK_INTERVAL="${CHECK_INTERVAL:-60}"  # Saniye cinsinden (varsayılan: 60)
MAX_CHECKS="${MAX_CHECKS:-}"  # Boşsa sınırsız

echo "🔍 finasis.com.tr Sürekli Monitoring"
echo "===================================="
echo "Site URL: $SITE_URL"
echo "Kontrol Aralığı: ${CHECK_INTERVAL} saniye"
if [ -n "$MAX_CHECKS" ]; then
    echo "Maksimum Kontrol: $MAX_CHECKS"
else
    echo "Maksimum Kontrol: Sınırsız (Ctrl+C ile durdurun)"
fi
echo ""

check_count=0

while true; do
    check_count=$((check_count + 1))
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] Kontrol #$check_count"
    echo "-----------------------------------"
    
    # Health check
    HTTP_CODE=$(curl -s -o /tmp/health_check.json -w "%{http_code}" \
        --max-time 10 \
        "${SITE_URL}/health/" 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        if command -v jq &> /dev/null; then
            STATUS=$(jq -r '.status' /tmp/health_check.json 2>/dev/null || echo "unknown")
            DB_TIME=$(jq -r '.checks.database.response_time_ms' /tmp/health_check.json 2>/dev/null || echo "N/A")
            echo "✅ Durum: $STATUS | DB: ${DB_TIME}ms"
        else
            echo "✅ HTTP $HTTP_CODE"
        fi
    else
        echo "❌ HTTP $HTTP_CODE - Site sorunlu!"
        echo "   Detaylar için: ./deploy/check_site_health.sh"
    fi
    
    echo ""
    
    # Maksimum kontrol sayısı kontrolü
    if [ -n "$MAX_CHECKS" ] && [ "$check_count" -ge "$MAX_CHECKS" ]; then
        echo "✅ Maksimum kontrol sayısına ulaşıldı. Çıkılıyor..."
        break
    fi
    
    # Bekle
    sleep "$CHECK_INTERVAL"
done

