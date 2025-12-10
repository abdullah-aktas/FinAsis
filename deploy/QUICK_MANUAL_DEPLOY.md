# Cloud Shell'de Hızlı Manuel Deployment

GitHub Actions deployment başarısız oluyorsa, Cloud Shell'de manuel olarak deploy edebilirsiniz.

## 🚀 Hızlı Deployment (Önerilen)

```bash
# 1. Cloud Shell'i açın ve projeyi clone edin
cd ~
if [ ! -d "FinAsis" ]; then
  git clone https://github.com/abdullah-aktas/FinAsis.git
fi
cd FinAsis
git pull origin main

# 2. Deployment scriptini çalıştırın
bash deploy/manual_deploy_cloud_shell.sh
```

Script size secret'ları soracak:
- `DJANGO_SECRET_KEY` - GitHub Secrets'dan alın
- `DJANGO_DB_PASSWORD` - GitHub Secrets'dan alın

## 📋 Alternatif: Adım Adım Manuel Deployment

Eğer script çalışmazsa, adım adım yapabilirsiniz:

```bash
# 1. Proje ayarları
PROJECT_ID="finasis-478502"
SERVICE_NAME="finasis-prod"
REGION="europe-west1"
REPOSITORY="finasis-app"
IMAGE_NAME="finasis-api"
SERVICE_ACCOUNT="github-actions-deploy@finasis-478502.iam.gserviceaccount.com"

gcloud config set project "$PROJECT_ID"

# 2. Repo'yu güncelleyin
cd ~/FinAsis
git pull origin main

# 3. Secret'ları ayarlayın (GitHub Secrets'dan alın)
export DJANGO_SECRET_KEY="your-secret-key-here"
export DJANGO_DB_PASSWORD="your-db-password-here"

# 4. Docker image build ve push
COMMIT_SHA=$(git rev-parse --short HEAD)
IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${COMMIT_SHA}"

gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
gcloud builds submit --tag "$IMAGE_TAG" --project="$PROJECT_ID"

# 5. Environment variables hazırlama
ENV_VARS="MPLCONFIGDIR=/tmp/matplotlib-cache,PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1,DJANGO_DB_ENGINE=django.db.backends.postgresql,DJANGO_DB_NAME=finasis,DJANGO_DB_USER=finasis-app,DJANGO_DB_HOST=/cloudsql/finasis-478502:europe-west1:finasis-db,CLOUD_SQL_CONNECTION_NAME=finasis-478502:europe-west1:finasis-db,DJANGO_DEBUG=0"
ENV_VARS="$ENV_VARS,DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY"
ENV_VARS="$ENV_VARS,DJANGO_DB_PASSWORD=$DJANGO_DB_PASSWORD"

# 6. Cloud Run deployment
gcloud run deploy "$SERVICE_NAME" \
  --image="$IMAGE_TAG" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --execution-environment=gen2 \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --concurrency=40 \
  --min-instances=1 \
  --max-instances=10 \
  --service-account="$SERVICE_ACCOUNT" \
  --add-cloudsql-instances=finasis-478502:europe-west1:finasis-db \
  --cpu-boost \
  --cpu-throttling \
  --set-env-vars="$ENV_VARS" \
  --project="$PROJECT_ID"

# 7. CLOUD_RUN_HOST güncelleme
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format="value(status.url)")

CLOUD_RUN_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||')

gcloud run services update "$SERVICE_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --update-env-vars="CLOUD_RUN_HOST=$CLOUD_RUN_HOST"

# 8. Sonuç
echo "✅ Deployment tamamlandı!"
echo "🌐 Servis URL: $SERVICE_URL"
```

## 🔍 Deployment Sonrası Kontrol

```bash
# Logları kontrol edin
bash deploy/check_deployment_status.sh

# Health check
SERVICE_URL=$(gcloud run services describe finasis-prod --region=europe-west1 --project=finasis-478502 --format="value(status.url)")
curl "$SERVICE_URL/health/"
```

## ⚠️ Sorun Giderme

### Container başlamıyorsa:
1. Logları kontrol edin: `bash deploy/get_recent_logs.sh`
2. Entrypoint çıktılarını kontrol edin: `bash deploy/check_deployment_status.sh`
3. Database bağlantısını kontrol edin: `bash deploy/check_database_connection.sh`

### Migration sorunları:
1. Migration'ları kontrol edin: `bash deploy/check_and_fix_migrations.sh`
2. Logları kontrol edin: `gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=finasis-prod" --limit=100 --project=finasis-478502 --format="value(textPayload)" | grep -i migration`

### Secret sorunları:
1. Secret'ları kontrol edin: `bash deploy/fix_and_check_secrets.sh`
2. GitHub Secrets'dan secret'ları alın ve export edin

