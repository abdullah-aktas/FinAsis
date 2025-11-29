#!/bin/bash
# Başarısız Build Loglarını Kontrol Etme Scripti

set -e

PROJECT_ID="${PROJECT_ID:-finasis-478502}"

echo "📋 Başarısız Build Loglarını Kontrol Ediyoruz..."
echo "================================================"
echo ""

# Son başarısız build'i bul
FAILED_BUILD=$(gcloud builds list \
    --limit=1 \
    --filter="status=FAILURE" \
    --sort-by=~createTime \
    --format="value(id)" 2>/dev/null || echo "")

if [ -z "$FAILED_BUILD" ]; then
    echo "✅ Başarısız build bulunamadı"
    exit 0
fi

echo "📋 Başarısız Build ID: $FAILED_BUILD"
echo ""

# Build detaylarını göster
echo "📋 Build Detayları:"
gcloud builds describe "$FAILED_BUILD" \
    --format="table(id,status,createTime,logUrl)" 2>/dev/null || echo "Build detayları alınamadı"
echo ""

# Build loglarını göster (--limit parametresi yok, bu yüzden stream ediyoruz)
echo "📋 Build Logları (son 100 satır):"
echo "--------------------------------"
gcloud builds log "$FAILED_BUILD" 2>/dev/null | tail -100 || {
    echo "Log okunamadı. Log URL'sini kullanarak manuel kontrol edin:"
    LOG_URL=$(gcloud builds describe "$FAILED_BUILD" --format="value(logUrl)" 2>/dev/null || echo "")
    if [ -n "$LOG_URL" ]; then
        echo "   $LOG_URL"
    fi
}
echo ""

