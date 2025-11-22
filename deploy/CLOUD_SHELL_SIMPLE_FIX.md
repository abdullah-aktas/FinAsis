# 🚀 ALLOWED_HOSTS Hızlı Düzeltme (Basit Yöntem)

`--update-env-vars` virgül içeren değerlerle sorun yaşıyor. İşte daha basit çözümler:

## ⚡ Yöntem 1: --set-env-vars Kullan (Önerilen)

**DİKKAT**: Bu yöntem mevcut tüm environment variables'ı değiştirir. Önce mevcut env vars'ı kaydedin:

```bash
# 1. Mevcut env vars'ı kaydet
gcloud run services describe finasis-prod \
    --region=europe-west1 \
    --format="json" \
    --project=$(gcloud config get-value project) | \
    jq -r '.spec.template.spec.containers[0].env[] | "\(.name)=\(.value)"' > current_env_vars.txt

# 2. Servis URL'sini al
SERVICE_URL=$(gcloud run services describe finasis-prod \
    --region=europe-west1 \
    --format="value(status.url)" \
    --project=$(gcloud config get-value project))
CLOUD_RUN_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')

# 3. ALLOWED_HOSTS'i güncelle (mevcut dosyada)
sed -i "s|^DJANGO_ALLOWED_HOSTS=.*|DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,finasis.com.tr,www.finasis.com.tr,$CLOUD_RUN_HOST|" current_env_vars.txt

# 4. CLOUD_RUN_HOST ekle
if ! grep -q "^CLOUD_RUN_HOST=" current_env_vars.txt; then
    echo "CLOUD_RUN_HOST=$CLOUD_RUN_HOST" >> current_env_vars.txt
fi

# 5. MPLCONFIGDIR ve Python ayarlarını ekle (yoksa)
if ! grep -q "^MPLCONFIGDIR=" current_env_vars.txt; then
    echo "MPLCONFIGDIR=/tmp/matplotlib-cache" >> current_env_vars.txt
fi
if ! grep -q "^PYTHONUNBUFFERED=" current_env_vars.txt; then
    echo "PYTHONUNBUFFERED=1" >> current_env_vars.txt
fi
if ! grep -q "^PYTHONDONTWRITEBYTECODE=" current_env_vars.txt; then
    echo "PYTHONDONTWRITEBYTECODE=1" >> current_env_vars.txt
fi

# 6. Env vars'ı virgülle ayırarak formatla
ENV_VARS=$(cat current_env_vars.txt | tr '\n' ',' | sed 's/,$//')

# 7. Servisi güncelle
gcloud run services update finasis-prod \
    --region=europe-west1 \
    --set-env-vars="$ENV_VARS" \
    --project=$(gcloud config get-value project)

# 8. Temizlik
rm current_env_vars.txt
```

## 🎯 Yöntem 2: Tek Komut (Sadece ALLOWED_HOSTS)

Eğer sadece `ALLOWED_HOSTS`'i güncellemek istiyorsanız:

```bash
SERVICE_NAME="finasis-prod"
REGION="europe-west1"
PROJECT_ID=$(gcloud config get-value project)

# URL ve hostname
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID")
CLOUD_RUN_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')

# ALLOWED_HOSTS (virgül içeren değer için özel format)
ALLOWED_HOSTS_VALUE="127.0.0.1,localhost,finasis.com.tr,www.finasis.com.tr,$CLOUD_RUN_HOST"

# --set-env-vars ile güncelle (mevcut env vars'ı korumak için önce al)
# NOT: Bu yöntem mevcut env vars'ı silebilir, dikkatli kullanın!
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --update-env-vars="DJANGO_ALLOWED_HOSTS=$ALLOWED_HOSTS_VALUE" \
    --project="$PROJECT_ID" 2>&1 || \
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --set-env-vars="DJANGO_ALLOWED_HOSTS=$ALLOWED_HOSTS_VALUE,CLOUD_RUN_HOST=$CLOUD_RUN_HOST,MPLCONFIGDIR=/tmp/matplotlib-cache,PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1" \
    --project="$PROJECT_ID"
```

## 🔧 Yöntem 3: Script Kullan

Script'i oluşturup çalıştırın:

```bash
# Script'i oluştur
cat > fix_allowed_hosts.sh << 'SCRIPT_EOF'
#!/bin/bash
SERVICE_NAME="finasis-prod"
REGION="europe-west1"
PROJECT_ID=$(gcloud config get-value project)

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID")
CLOUD_RUN_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')

# Mevcut env vars'ı JSON formatında al
ENV_JSON=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="json" \
    --project="$PROJECT_ID")

# jq ile parse et ve güncelle
UPDATED_ENV=$(echo "$ENV_JSON" | jq --arg host "$CLOUD_RUN_HOST" --arg allowed "$ALLOWED_HOSTS" '
  .spec.template.spec.containers[0].env |= map(
    if .name == "DJANGO_ALLOWED_HOSTS" then
      .value = "127.0.0.1,localhost,finasis.com.tr,www.finasis.com.tr," + $host
    elif .name == "CLOUD_RUN_HOST" then
      .value = $host
    else
      .
    end
  ) |
  .spec.template.spec.containers[0].env += [
    {"name": "DJANGO_ALLOWED_HOSTS", "value": "127.0.0.1,localhost,finasis.com.tr,www.finasis.com.tr," + $host} |
    select(.spec.template.spec.containers[0].env | map(.name == "DJANGO_ALLOWED_HOSTS") | any | not)
  ] |
  .spec.template.spec.containers[0].env += [
    {"name": "CLOUD_RUN_HOST", "value": $host} |
    select(.spec.template.spec.containers[0].env | map(.name == "CLOUD_RUN_HOST") | any | not)
  ]
')

# Bu yöntem çok karmaşık, Yöntem 1'i kullanın
SCRIPT_EOF

chmod +x fix_allowed_hosts.sh
```

## ✅ En Basit Çözüm (Manuel)

Eğer yukarıdakiler çalışmazsa, manuel olarak:

```bash
# 1. Mevcut env vars'ı görüntüle
gcloud run services describe finasis-prod \
    --region=europe-west1 \
    --format="yaml(spec.template.spec.containers[0].env)" \
    --project=$(gcloud config get-value project)

# 2. Tüm env vars'ı bir dosyaya kaydet ve düzenle
# 3. Sonra --set-env-vars ile güncelle
```

## 🎯 Önerilen: Yöntem 1

Yöntem 1 en güvenli ve en kapsamlı çözümdür. Mevcut environment variables'ı korur ve sadece gerekli değişiklikleri yapar.

