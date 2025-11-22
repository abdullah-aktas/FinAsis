# 🚀 Cloud Shell Hızlı Düzeltme

Cloud Shell'de proje dosyaları yoksa, doğrudan komutları çalıştırabilirsiniz.

## ⚡ Hızlı Çözüm (Proje Klonlanmamışsa)

### Adım 1: Script'i Oluşturun

Cloud Shell'de şu komutu çalıştırın:

```bash
cat > fix_cloud_run.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Ayarlar
PROJECT_ID=$(gcloud config get-value project)
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
MEMORY="2Gi"
CPU="2"
TIMEOUT="300"
MIN_INSTANCES="1"
MAX_INSTANCES="10"

echo "🔧 Cloud Run Servis Düzeltmeleri"
echo "Proje: $PROJECT_ID"
echo "Bölge: $REGION"
echo "Servis: $SERVICE_NAME"
echo ""

# Mevcut durumu kontrol et
echo "📊 Mevcut servis durumu:"
gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="table(
        metadata.name,
        status.url,
        spec.template.spec.containers[0].resources.limits.memory,
        spec.template.spec.containers[0].resources.limits.cpu
    )" 2>/dev/null || {
    echo "❌ Servis bulunamadı. Mevcut servisler:"
    gcloud run services list --region="$REGION" --format="table(metadata.name,status.url)"
    exit 1
}

echo ""
read -p "Devam etmek istiyor musunuz? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "İptal edildi"
    exit 0
fi

# Environment variables
ENV_VARS="MPLCONFIGDIR=/tmp/matplotlib-cache,PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1"

# Mevcut env vars'ı al
EXISTING_ENV=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(spec.template.spec.containers[0].env)" 2>/dev/null || echo "")

if [ -n "$EXISTING_ENV" ] && [ "$EXISTING_ENV" != "None" ] && [ "$EXISTING_ENV" != "" ]; then
    ENV_VARS="$EXISTING_ENV,$ENV_VARS"
fi

echo "🚀 Servis güncelleniyor..."
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --memory="$MEMORY" \
    --cpu="$CPU" \
    --timeout="$TIMEOUT" \
    --min-instances="$MIN_INSTANCES" \
    --max-instances="$MAX_INSTANCES" \
    --set-env-vars="$ENV_VARS" \
    --project="$PROJECT_ID"

echo ""
echo "✅ Servis başarıyla güncellendi!"
echo ""
echo "📊 Güncellenmiş bilgiler:"
gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="table(
        metadata.name,
        status.url,
        spec.template.spec.containers[0].resources.limits.memory,
        spec.template.spec.containers[0].resources.limits.cpu,
        spec.template.spec.timeoutSeconds
    )" \
    --project="$PROJECT_ID"
EOF

chmod +x fix_cloud_run.sh
```

### Adım 2: Script'i Çalıştırın

```bash
./fix_cloud_run.sh
```

## 🎯 Tek Komut Çözümü

Eğer script oluşturmak istemiyorsanız, doğrudan şu komutu çalıştırabilirsiniz:

```bash
# Ayarları değiştirin (gerekirse)
export SERVICE_NAME="finasis-prod"
export REGION="europe-west1"

# Servisi güncelleyin
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --min-instances=1 \
    --max-instances=10 \
    --set-env-vars="MPLCONFIGDIR=/tmp/matplotlib-cache,PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1" \
    --project=$(gcloud config get-value project)
```

## 🔍 Servis Adını Bulma

Eğer servis adını bilmiyorsanız:

```bash
# Tüm Cloud Run servislerini listele
gcloud run services list --region=europe-west1

# Veya tüm bölgelerde
gcloud run services list
```

## ✅ Doğrulama

Değişikliklerin uygulandığını kontrol edin:

```bash
# Servis bilgilerini görüntüle
gcloud run services describe finasis-prod \
    --region=europe-west1 \
    --format="yaml" \
    --project=$(gcloud config get-value project)

# Logları kontrol et
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=finasis-prod" \
    --project=$(gcloud config get-value project)
```

## 📝 Notlar

- Script, mevcut environment variables'ı korur
- Sadece yeni ayarları ekler/günceller
- Deployment birkaç dakika sürebilir
- İlk istekler hala yavaş olabilir (cold start)

