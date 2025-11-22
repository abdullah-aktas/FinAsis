# 🔧 ALLOWED_HOSTS Hızlı Düzeltme

Cloud Run URL'si `ALLOWED_HOSTS` listesinde olmadığı için `DisallowedHost` hatası alıyorsunuz.

## ⚡ Hızlı Çözüm (Cloud Shell)

### Adım 1: Servis URL'sini Bulun

```bash
# Servis URL'sini alın
SERVICE_URL=$(gcloud run services describe finasis-prod \
    --region=europe-west1 \
    --format="value(status.url)" \
    --project=$(gcloud config get-value project))

echo "Servis URL: $SERVICE_URL"

# Hostname'i çıkarın
CLOUD_RUN_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')
echo "Hostname: $CLOUD_RUN_HOST"
```

### Adım 2: ALLOWED_HOSTS'i Güncelleyin

```bash
# Mevcut ALLOWED_HOSTS'i alın
CURRENT_HOSTS=$(gcloud run services describe finasis-prod \
    --region=europe-west1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DJANGO_ALLOWED_HOSTS')].value)" \
    --project=$(gcloud config get-value project) || echo "")

# Yeni ALLOWED_HOSTS'i oluşturun
if [ -n "$CURRENT_HOSTS" ] && [ "$CURRENT_HOSTS" != "None" ]; then
    NEW_HOSTS="$CURRENT_HOSTS,$CLOUD_RUN_HOST"
else
    NEW_HOSTS="127.0.0.1,localhost,finasis.com.tr,www.finasis.com.tr,$CLOUD_RUN_HOST"
fi

echo "Yeni ALLOWED_HOSTS: $NEW_HOSTS"

# Servisi güncelleyin
gcloud run services update finasis-prod \
    --region=europe-west1 \
    --update-env-vars="DJANGO_ALLOWED_HOSTS=$NEW_HOSTS" \
    --project=$(gcloud config get-value project)
```

## 🎯 Tek Komut Çözümü

```bash
# Tek komutla düzeltme
SERVICE_NAME="finasis-prod"
REGION="europe-west1"
PROJECT_ID=$(gcloud config get-value project)

# URL ve hostname'i al
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID")
CLOUD_RUN_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')

# Mevcut hosts
CURRENT_HOSTS=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DJANGO_ALLOWED_HOSTS')].value)" \
    --project="$PROJECT_ID" 2>/dev/null || echo "")

# Yeni hosts
if [ -n "$CURRENT_HOSTS" ] && [ "$CURRENT_HOSTS" != "None" ]; then
    NEW_HOSTS="$CURRENT_HOSTS,$CLOUD_RUN_HOST"
else
    NEW_HOSTS="127.0.0.1,localhost,finasis.com.tr,www.finasis.com.tr,$CLOUD_RUN_HOST"
fi

# Güncelle
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --update-env-vars="DJANGO_ALLOWED_HOSTS=$NEW_HOSTS" \
    --project="$PROJECT_ID"

echo "✅ ALLOWED_HOSTS güncellendi: $NEW_HOSTS"
```

## 📝 Manuel Environment Variable Ekleme

Eğer yukarıdaki komutlar çalışmazsa, manuel olarak ekleyin:

```bash
gcloud run services update finasis-prod \
    --region=europe-west1 \
    --update-env-vars="DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,finasis.com.tr,www.finasis.com.tr,finasis-prod-211704933618.europe-west1.run.app" \
    --project=$(gcloud config get-value project)
```

## ✅ Doğrulama

Güncellemeden sonra kontrol edin:

```bash
# Environment variables'ı kontrol et
gcloud run services describe finasis-prod \
    --region=europe-west1 \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DJANGO_ALLOWED_HOSTS')].value)" \
    --project=$(gcloud config get-value project)

# Servisi test et
curl -I https://finasis-prod-211704933618.europe-west1.run.app/
```

## 🔍 Sorun Devam Ederse

1. **Tüm environment variables'ı kontrol edin**:
   ```bash
   gcloud run services describe finasis-prod \
       --region=europe-west1 \
       --format="yaml(spec.template.spec.containers[0].env)" \
       --project=$(gcloud config get-value project)
   ```

2. **Logları kontrol edin**:
   ```bash
   gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=finasis-prod" \
       --project=$(gcloud config get-value project)
   ```

3. **Servisi yeniden başlatın** (gerekirse):
   ```bash
   gcloud run services update finasis-prod \
       --region=europe-west1 \
       --project=$(gcloud config get-value project)
   ```

## 📌 Notlar

- Cloud Run URL'si genellikle `*.run.app` formatındadır
- Her deployment'ta URL değişebilir, bu yüzden environment variable kullanmak önemlidir
- Production'da `DEBUG=False` olmalı (şu anda `DEBUG=True` görünüyor)
- `CSRF_TRUSTED_ORIGINS`'e de Cloud Run URL'sini eklemeniz gerekebilir

