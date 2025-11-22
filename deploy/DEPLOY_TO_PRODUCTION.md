# Canlıya Deployment Rehberi

Bu doküman, yapılan değişiklikleri production ortamına nasıl yansıtacağınızı açıklar.

## Yöntem 1: Cloud Build ile Otomatik Deployment (Önerilen)

### Adım 1: Cloud Build Trigger Oluşturma

Eğer henüz oluşturulmadıysa, GitHub push'ları için otomatik trigger oluşturun:

```bash
gcloud builds triggers create github \
  --name="finasis-prod-deploy" \
  --repo-name="FinAsis" \
  --repo-owner="abdullah-aktas" \
  --branch-pattern="^main$" \
  --build-config="deploy/cloud_run/cloudbuild.yaml" \
  --region="europe-west1"
```

### Adım 2: Manuel Cloud Build Çalıştırma

GitHub'a push yaptıktan sonra, Cloud Build'i manuel olarak tetikleyebilirsiniz:

```bash
# Cloud Shell'de veya local'de
gcloud builds submit \
  --config=deploy/cloud_run/cloudbuild.yaml \
  --substitutions=_SERVICE=finasis-prod,_REGION=europe-west1
```

## Yöntem 2: Cloud Shell ile Hızlı Deployment

### Adım 1: Cloud Shell'i Açın

Google Cloud Console'dan Cloud Shell'i açın.

### Adım 2: Repository'yi Clone Edin

```bash
git clone https://github.com/abdullah-aktas/FinAsis.git
cd FinAsis
```

### Adım 3: Cloud Build'i Çalıştırın

```bash
gcloud builds submit \
  --config=deploy/cloud_run/cloudbuild.yaml \
  --region=europe-west1 \
  --substitutions=_SERVICE=finasis-prod
```

## Yöntem 3: Manuel Docker Build ve Deploy

### Adım 1: Docker Image Build

```bash
# Local'de veya Cloud Shell'de
docker build -t gcr.io/PROJECT_ID/finasis-app/finasis-api:latest .
```

### Adım 2: Image'ı Push Edin

```bash
docker push gcr.io/PROJECT_ID/finasis-app/finasis-api:latest
```

### Adım 3: Cloud Run'ı Güncelleyin

```bash
gcloud run deploy finasis-prod \
  --image=gcr.io/PROJECT_ID/finasis-app/finasis-api:latest \
  --region=europe-west1 \
  --platform=managed \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --concurrency=40 \
  --min-instances=1 \
  --max-instances=10
```

## Yöntem 4: Sadece Kod Değişiklikleri (Hızlı)

Eğer sadece Python kod değişiklikleri varsa ve Dockerfile değişmediyse:

```bash
# Cloud Shell'de
cd FinAsis
git pull origin main

# Yeni image build ve deploy
gcloud builds submit --config=deploy/cloud_run/cloudbuild.yaml
```

## Deployment Sonrası Kontroller

### 1. Servis Durumunu Kontrol Edin

```bash
gcloud run services describe finasis-prod \
  --region=europe-west1 \
  --format="value(status.url)"
```

### 2. Logları İnceleyin

```bash
gcloud run services logs read finasis-prod \
  --region=europe-west1 \
  --limit=50
```

### 3. Health Check

```bash
curl https://finasis-prod-XXXXX.europe-west1.run.app/
```

## Önemli Notlar

1. **Database Migrations**: Cloud Build otomatik olarak migrations çalıştırır, ancak production'da manuel kontrol önerilir:
   ```bash
   gcloud run jobs create migrate-job \
     --image=gcr.io/PROJECT_ID/finasis-app/finasis-api:latest \
     --command="python" \
     --args="manage.py,migrate" \
     --region=europe-west1
   ```

2. **Static Files**: `collectstatic` Cloud Build'de otomatik çalışır.

3. **Environment Variables**: Gerekli env vars'ları Cloud Run'da ayarlayın:
   ```bash
   gcloud run services update finasis-prod \
     --region=europe-west1 \
     --update-env-vars="DJANGO_SETTINGS_MODULE=config.settings.production"
   ```

4. **Rollback**: Sorun olursa önceki revision'a dönebilirsiniz:
   ```bash
   gcloud run services update-traffic finasis-prod \
     --region=europe-west1 \
     --to-revisions=PREVIOUS_REVISION=100
   ```

## Hızlı Deployment Script

Tüm adımları otomatikleştiren script:

```bash
#!/bin/bash
# deploy/quick_deploy.sh

PROJECT_ID=$(gcloud config get-value project)
REGION="europe-west1"
SERVICE="finasis-prod"

echo "🚀 Deployment başlıyor..."

# Build ve deploy
gcloud builds submit \
  --config=deploy/cloud_run/cloudbuild.yaml \
  --region=$REGION \
  --substitutions=_SERVICE=$SERVICE

echo "✅ Deployment tamamlandı!"
echo "🌐 Servis URL: $(gcloud run services describe $SERVICE --region=$REGION --format='value(status.url)')"
```

## Sorun Giderme

### Deployment Başarısız Olursa

1. Build loglarını kontrol edin:
   ```bash
   gcloud builds list --limit=5
   gcloud builds log BUILD_ID
   ```

2. Cloud Run revision'larını kontrol edin:
   ```bash
   gcloud run revisions list --service=finasis-prod --region=europe-west1
   ```

3. Rollback yapın:
   ```bash
   gcloud run services update-traffic finasis-prod \
     --region=europe-west1 \
     --to-revisions=PREVIOUS_REVISION=100
   ```

