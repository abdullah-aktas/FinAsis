#!/bin/bash
# ALLOWED_HOSTS Düzeltme Scripti (Final - Virgül Sorunu Çözüldü)
# Bu script --set-env-vars kullanarak tüm env vars'ları set eder

set -e

PROJECT_ID="${PROJECT_ID:-finasis-478502}"
REGION="${REGION:-europe-west1}"
SERVICE_NAME="${SERVICE_NAME:-finasis-prod}"

echo "🔧 ALLOWED_HOSTS Düzeltiyoruz (Final)..."
echo "========================================"
echo ""

# Projeyi ayarla
gcloud config set project "$PROJECT_ID"

# Servis URL'sini al
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" 2>/dev/null || echo "")

if [ -z "$SERVICE_URL" ]; then
    echo "❌ Servis bulunamadı: $SERVICE_NAME"
    exit 1
fi

echo "✅ Servis URL: $SERVICE_URL"
SERVICE_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')
echo "   Host: $SERVICE_HOST"
echo ""

# Mevcut environment variables'ı al (JSON formatında)
echo "📋 Mevcut environment variables alınıyor..."
ENV_JSON=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="json" 2>/dev/null | \
    jq -r '.spec.template.spec.containers[0].env[]? | "\(.name)=\(.value)"' 2>/dev/null || echo "")

# Geçici dosya oluştur
ENV_FILE=$(mktemp)

# Mevcut env vars'ları dosyaya yaz (ALLOWED_HOSTS hariç)
if [ -n "$ENV_JSON" ]; then
    echo "$ENV_JSON" | grep -v "^DJANGO_ALLOWED_HOSTS=" > "$ENV_FILE" || true
else
    touch "$ENV_FILE"
fi

# Yeni ALLOWED_HOSTS değerini oluştur
CURRENT_ALLOWED_HOSTS=$(echo "$ENV_JSON" | grep "^DJANGO_ALLOWED_HOSTS=" | cut -d'=' -f2- || echo "")
if [ -z "$CURRENT_ALLOWED_HOSTS" ]; then
    NEW_ALLOWED_HOSTS="finasis.com.tr,www.finasis.com.tr,$SERVICE_HOST"
else
    if echo "$CURRENT_ALLOWED_HOSTS" | grep -q "$SERVICE_HOST"; then
        NEW_ALLOWED_HOSTS="$CURRENT_ALLOWED_HOSTS"
        echo "ℹ️  $SERVICE_HOST zaten ALLOWED_HOSTS'te mevcut"
    else
        NEW_ALLOWED_HOSTS="$CURRENT_ALLOWED_HOSTS,$SERVICE_HOST"
    fi
fi

# ALLOWED_HOSTS'i dosyaya ekle/güncelle
echo "DJANGO_ALLOWED_HOSTS=$NEW_ALLOWED_HOSTS" >> "$ENV_FILE"

# Diğer önemli env vars'ları ekle (yoksa)
if ! grep -q "^DJANGO_DEBUG=" "$ENV_FILE"; then
    echo "DJANGO_DEBUG=False" >> "$ENV_FILE"
fi
if ! grep -q "^MPLCONFIGDIR=" "$ENV_FILE"; then
    echo "MPLCONFIGDIR=/tmp/matplotlib-cache" >> "$ENV_FILE"
fi
if ! grep -q "^PYTHONUNBUFFERED=" "$ENV_FILE"; then
    echo "PYTHONUNBUFFERED=1" >> "$ENV_FILE"
fi
if ! grep -q "^PYTHONDONTWRITEBYTECODE=" "$ENV_FILE"; then
    echo "PYTHONDONTWRITEBYTECODE=1" >> "$ENV_FILE"
fi

echo "📝 Yeni ALLOWED_HOSTS: $NEW_ALLOWED_HOSTS"
echo ""

# Environment variables'ı KEY=VALUE,KEY2=VALUE2 formatına çevir
ENV_VARS_STRING=$(cat "$ENV_FILE" | tr '\n' ',' | sed 's/,$//')

echo "🔄 Environment variables güncelleniyor..."

# --set-env-vars kullan (tüm env vars'ları set eder)
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --set-env-vars="$ENV_VARS_STRING" \
    --quiet

# Geçici dosyayı sil
rm -f "$ENV_FILE"

echo ""
echo "✅ ALLOWED_HOSTS güncellendi!"
echo ""
echo "🧪 Health check yapılıyor..."
sleep 5

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    --max-time 10 \
    "$SERVICE_URL" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Servis artık çalışıyor! (HTTP $HTTP_CODE)"
else
    echo "⚠️  Servis hala sorunlu (HTTP $HTTP_CODE)"
    echo "   Logları kontrol edin:"
    echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=20"
fi
echo ""

