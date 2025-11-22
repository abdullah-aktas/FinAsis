#!/bin/bash
# =============================================================================
# ALLOWED_HOSTS Düzeltme Script'i (Cloud Shell için)
# Virgül içeren değerler için doğru syntax kullanır
# =============================================================================

set -euo pipefail

# Ayarlar
SERVICE_NAME="${SERVICE_NAME:-finasis-prod}"
REGION="${REGION:-europe-west1}"
PROJECT_ID=$(gcloud config get-value project)

echo "🔧 ALLOWED_HOSTS Düzeltme"
echo "Proje: $PROJECT_ID"
echo "Servis: $SERVICE_NAME"
echo "Bölge: $REGION"
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

# Mevcut tüm environment variables'ı al
echo "📋 Mevcut environment variables alınıyor..."
ALL_ENV_VARS=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="json" \
    --project="$PROJECT_ID" | \
    jq -r '.spec.template.spec.containers[0].env[] | "\(.name)=\(.value)"' 2>/dev/null || echo "")

# Mevcut ALLOWED_HOSTS'i bul
CURRENT_HOSTS=""
if [ -n "$ALL_ENV_VARS" ]; then
    CURRENT_HOSTS=$(echo "$ALL_ENV_VARS" | grep "^DJANGO_ALLOWED_HOSTS=" | cut -d'=' -f2- || echo "")
fi

# Yeni ALLOWED_HOSTS'i oluştur
if [ -n "$CURRENT_HOSTS" ] && [ "$CURRENT_HOSTS" != "None" ] && [ "$CURRENT_HOSTS" != "" ]; then
    if [[ ! "$CURRENT_HOSTS" == *"$CLOUD_RUN_HOST"* ]]; then
        NEW_HOSTS="$CURRENT_HOSTS,$CLOUD_RUN_HOST"
    else
        NEW_HOSTS="$CURRENT_HOSTS"
        echo "ℹ️  Cloud Run host zaten ALLOWED_HOSTS'te mevcut"
    fi
else
    NEW_HOSTS="127.0.0.1,localhost,finasis.com.tr,www.finasis.com.tr,$CLOUD_RUN_HOST"
fi

echo "Yeni ALLOWED_HOSTS: $NEW_HOSTS"
echo ""

# Mevcut env vars'ı koru ve ALLOWED_HOSTS'i güncelle
# Önce mevcut env vars'ı bir dosyaya yaz
TEMP_ENV_FILE=$(mktemp)
if [ -n "$ALL_ENV_VARS" ]; then
    echo "$ALL_ENV_VARS" > "$TEMP_ENV_FILE"
    # ALLOWED_HOSTS'i güncelle veya ekle
    if grep -q "^DJANGO_ALLOWED_HOSTS=" "$TEMP_ENV_FILE"; then
        sed -i "s|^DJANGO_ALLOWED_HOSTS=.*|DJANGO_ALLOWED_HOSTS=$NEW_HOSTS|" "$TEMP_ENV_FILE"
    else
        echo "DJANGO_ALLOWED_HOSTS=$NEW_HOSTS" >> "$TEMP_ENV_FILE"
    fi
    # CLOUD_RUN_HOST'u ekle/güncelle
    if grep -q "^CLOUD_RUN_HOST=" "$TEMP_ENV_FILE"; then
        sed -i "s|^CLOUD_RUN_HOST=.*|CLOUD_RUN_HOST=$CLOUD_RUN_HOST|" "$TEMP_ENV_FILE"
    else
        echo "CLOUD_RUN_HOST=$CLOUD_RUN_HOST" >> "$TEMP_ENV_FILE"
    fi
else
    # Hiç env var yoksa yeni oluştur
    cat > "$TEMP_ENV_FILE" << EOF
DJANGO_ALLOWED_HOSTS=$NEW_HOSTS
CLOUD_RUN_HOST=$CLOUD_RUN_HOST
MPLCONFIGDIR=/tmp/matplotlib-cache
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
EOF
fi

# Env vars'ı formatla (KEY=VALUE,KEY2=VALUE2 formatına çevir)
ENV_VARS_STRING=$(cat "$TEMP_ENV_FILE" | tr '\n' ',' | sed 's/,$//')

echo "🚀 Servis güncelleniyor..."
echo ""

# --set-env-vars kullan (virgül içeren değerler için doğru format)
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --set-env-vars="$ENV_VARS_STRING" \
    --project="$PROJECT_ID"

# Geçici dosyayı temizle
rm -f "$TEMP_ENV_FILE"

echo ""
echo "✅ ALLOWED_HOSTS başarıyla güncellendi!"
echo ""
echo "📊 Güncellenmiş ALLOWED_HOSTS:"
gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DJANGO_ALLOWED_HOSTS')].value)" \
    --project="$PROJECT_ID"

