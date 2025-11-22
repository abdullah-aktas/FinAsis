#!/bin/bash
# =============================================================================
# ALLOWED_HOSTS Düzeltme - Cloud Shell için Final Çözüm
# Virgül içeren değerler için env-vars-file kullanır
# =============================================================================

set -euo pipefail

SERVICE_NAME="${SERVICE_NAME:-finasis-prod}"
REGION="${REGION:-europe-west1}"
PROJECT_ID=$(gcloud config get-value project)

echo "🔧 ALLOWED_HOSTS Düzeltme"
echo "Proje: $PROJECT_ID"
echo "Servis: $SERVICE_NAME"
echo ""

# Servis URL'sini al
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID")

CLOUD_RUN_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')

echo "Servis URL: $SERVICE_URL"
echo "Hostname: $CLOUD_RUN_HOST"
echo ""

# Mevcut env vars'ı JSON formatında al
ENV_JSON=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="json" \
    --project="$PROJECT_ID")

# jq yüklü mü kontrol et
if ! command -v jq &> /dev/null; then
    echo "jq yükleniyor..."
    sudo apt-get update -qq && sudo apt-get install -y jq > /dev/null 2>&1
fi

# Geçici dosya oluştur
ENV_FILE=$(mktemp)

# Mevcut env vars'ı dosyaya yaz (KEY=VALUE formatında)
echo "$ENV_JSON" | jq -r '.spec.template.spec.containers[0].env[]? | "\(.name)=\(.value)"' > "$ENV_FILE"

# ALLOWED_HOSTS'i güncelle veya ekle
ALLOWED_HOSTS="127.0.0.1,localhost,finasis.com.tr,www.finasis.com.tr,$CLOUD_RUN_HOST"

if grep -q "^DJANGO_ALLOWED_HOSTS=" "$ENV_FILE"; then
    # Mevcut ALLOWED_HOSTS'i güncelle
    sed -i "s|^DJANGO_ALLOWED_HOSTS=.*|DJANGO_ALLOWED_HOSTS=$ALLOWED_HOSTS|" "$ENV_FILE"
    echo "✅ ALLOWED_HOSTS güncellendi"
else
    # Yeni ALLOWED_HOSTS ekle
    echo "DJANGO_ALLOWED_HOSTS=$ALLOWED_HOSTS" >> "$ENV_FILE"
    echo "✅ ALLOWED_HOSTS eklendi"
fi

# CLOUD_RUN_HOST ekle/güncelle
if grep -q "^CLOUD_RUN_HOST=" "$ENV_FILE"; then
    sed -i "s|^CLOUD_RUN_HOST=.*|CLOUD_RUN_HOST=$CLOUD_RUN_HOST|" "$ENV_FILE"
else
    echo "CLOUD_RUN_HOST=$CLOUD_RUN_HOST" >> "$ENV_FILE"
fi

# MPLCONFIGDIR ve Python ayarlarını ekle (yoksa)
if ! grep -q "^MPLCONFIGDIR=" "$ENV_FILE"; then
    echo "MPLCONFIGDIR=/tmp/matplotlib-cache" >> "$ENV_FILE"
fi
if ! grep -q "^PYTHONUNBUFFERED=" "$ENV_FILE"; then
    echo "PYTHONUNBUFFERED=1" >> "$ENV_FILE"
fi
if ! grep -q "^PYTHONDONTWRITEBYTECODE=" "$ENV_FILE"; then
    echo "PYTHONDONTWRITEBYTECODE=1" >> "$ENV_FILE"
fi

echo ""
echo "📋 Güncellenmiş environment variables:"
cat "$ENV_FILE"
echo ""

# --env-vars-file kullan (virgül sorununu çözer)
echo "🚀 Servis güncelleniyor..."
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --env-vars-file="$ENV_FILE" \
    --project="$PROJECT_ID"

# Temizlik
rm -f "$ENV_FILE"

echo ""
echo "✅ ALLOWED_HOSTS başarıyla güncellendi!"
echo ""
echo "📊 Doğrulama:"
gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DJANGO_ALLOWED_HOSTS')].value)" \
    --project="$PROJECT_ID"

