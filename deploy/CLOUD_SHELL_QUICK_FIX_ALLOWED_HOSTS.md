# 🔧 ALLOWED_HOSTS Hızlı Düzeltme - Cloud Shell

## ⚡ Tek Komut Çözümü

Cloud Shell'de şu komutları çalıştırın:

```bash
# Script'i oluştur ve çalıştır
cat > fix_allowed_hosts.sh << 'EOF'
#!/bin/bash
SERVICE_NAME="finasis-prod"
REGION="europe-west1"
PROJECT_ID=$(gcloud config get-value project)

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID")
CLOUD_RUN_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')

# jq yüklü mü kontrol et
if ! command -v jq &> /dev/null; then
    sudo apt-get update -qq && sudo apt-get install -y jq > /dev/null 2>&1
fi

# Mevcut env vars'ı al
ENV_JSON=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="json" \
    --project="$PROJECT_ID")

# Geçici dosya
ENV_FILE=$(mktemp)
echo "$ENV_JSON" | jq -r '.spec.template.spec.containers[0].env[]? | "\(.name)=\(.value)"' > "$ENV_FILE"

# ALLOWED_HOSTS güncelle
ALLOWED_HOSTS="127.0.0.1,localhost,finasis.com.tr,www.finasis.com.tr,$CLOUD_RUN_HOST"
if grep -q "^DJANGO_ALLOWED_HOSTS=" "$ENV_FILE"; then
    sed -i "s|^DJANGO_ALLOWED_HOSTS=.*|DJANGO_ALLOWED_HOSTS=$ALLOWED_HOSTS|" "$ENV_FILE"
else
    echo "DJANGO_ALLOWED_HOSTS=$ALLOWED_HOSTS" >> "$ENV_FILE"
fi

# CLOUD_RUN_HOST ekle
if ! grep -q "^CLOUD_RUN_HOST=" "$ENV_FILE"; then
    echo "CLOUD_RUN_HOST=$CLOUD_RUN_HOST" >> "$ENV_FILE"
fi

# Güncelle
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --env-vars-file="$ENV_FILE" \
    --project="$PROJECT_ID"

rm -f "$ENV_FILE"
echo "✅ ALLOWED_HOSTS güncellendi: $ALLOWED_HOSTS"
EOF

chmod +x fix_allowed_hosts.sh
./fix_allowed_hosts.sh
```

## 🎯 50K Users Deployment

Eğer 50K users için deployment yapmak istiyorsanız:

```bash
# Script'i oluştur
cat > deploy_50k.sh << 'EOF'
#!/bin/bash
# [deploy/CLOUD_SHELL_DEPLOY_50K.sh içeriğini buraya yapıştırın]
EOF

chmod +x deploy_50k.sh
./deploy_50k.sh
```

Veya doğrudan komutları çalıştırın:

```bash
# 50K users için servisi güncelle
gcloud run services update finasis-prod \
    --region=europe-west1 \
    --memory=4Gi \
    --cpu=4 \
    --timeout=300 \
    --concurrency=100 \
    --min-instances=10 \
    --max-instances=500 \
    --cpu-boost \
    --project=$(gcloud config get-value project)
```

## 📝 Notlar

- `--env-vars-file` kullanarak virgül sorununu çözüyoruz
- `jq` gerekli (otomatik yüklenir)
- Mevcut environment variables korunur

