#!/bin/bash
# HTTP 400 Hatasını Düzeltme Scripti
# Bu script ALLOWED_HOSTS sorununu çözer

set -e

PROJECT_ID="${PROJECT_ID:-finasis-478502}"
REGION="${REGION:-europe-west1}"
SERVICE_NAME="${SERVICE_NAME:-finasis-prod}"

echo "🔧 HTTP 400 Hatasını Düzeltiyoruz..."
echo "===================================="
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

# Mevcut ALLOWED_HOSTS'i kontrol et
CURRENT_ALLOWED_HOSTS=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DJANGO_ALLOWED_HOSTS')].value)" 2>/dev/null || echo "")

echo "📋 Mevcut ALLOWED_HOSTS: ${CURRENT_ALLOWED_HOSTS:-AYARLANMAMIŞ}"
echo ""

# Yeni ALLOWED_HOSTS değerini oluştur
if [ -z "$CURRENT_ALLOWED_HOSTS" ]; then
    NEW_ALLOWED_HOSTS="finasis.com.tr,www.finasis.com.tr,$SERVICE_HOST"
else
    # Mevcut değerlere yeni host'u ekle (eğer yoksa)
    if echo "$CURRENT_ALLOWED_HOSTS" | grep -q "$SERVICE_HOST"; then
        NEW_ALLOWED_HOSTS="$CURRENT_ALLOWED_HOSTS"
        echo "ℹ️  $SERVICE_HOST zaten ALLOWED_HOSTS'te mevcut"
    else
        NEW_ALLOWED_HOSTS="$CURRENT_ALLOWED_HOSTS,$SERVICE_HOST"
    fi
fi

echo "📝 Yeni ALLOWED_HOSTS: $NEW_ALLOWED_HOSTS"
echo ""

# Onay iste
read -p "ALLOWED_HOSTS'i güncellemek istiyor musunuz? (y/N): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ İşlem iptal edildi"
    exit 0
fi

# Environment variables'ı doğru formatta oluştur (KEY=VALUE,KEY2=VALUE2)
# Virgül içeren değerler için tırnak kullanmıyoruz, sadece escape ediyoruz
ENV_VARS_UPDATE="DJANGO_ALLOWED_HOSTS=$NEW_ALLOWED_HOSTS"
ENV_VARS_UPDATE="$ENV_VARS_UPDATE,DJANGO_DEBUG=False"
ENV_VARS_UPDATE="$ENV_VARS_UPDATE,MPLCONFIGDIR=/tmp/matplotlib-cache"
ENV_VARS_UPDATE="$ENV_VARS_UPDATE,PYTHONUNBUFFERED=1"
ENV_VARS_UPDATE="$ENV_VARS_UPDATE,PYTHONDONTWRITEBYTECODE=1"

echo "🔄 Environment variables güncelleniyor..."

# Cloud Run servisini güncelle (--update-env-vars ile, tırnak içinde)
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --update-env-vars="$ENV_VARS_UPDATE" \
    --quiet

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
