#!/bin/bash
# Cloud Shell'de production deployment scripti
# Kullanım: bash scripts/deploy-production-cloud-shell.sh

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
REPOSITORY="finasis-app"
IMAGE_NAME="finasis-api"

echo "🚀 Production Deployment Başlatılıyor..."
echo ""

# 1. Gerekli API'leri etkinleştir
echo "📡 Gerekli API'ler etkinleştiriliyor..."
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID || echo "⚠️  Cloud Build API zaten etkin"
gcloud services enable artifactregistry.googleapis.com --project=$PROJECT_ID || echo "⚠️  Artifact Registry API zaten etkin"
gcloud services enable storage-api.googleapis.com --project=$PROJECT_ID || echo "⚠️  Storage API zaten etkin"
gcloud services enable storage-component.googleapis.com --project=$PROJECT_ID || echo "⚠️  Storage Component API zaten etkin"

echo "⏳ API'lerin etkinleşmesi için 20 saniye bekleniyor..."
sleep 20

# 1.1. Project number ve Cloud Build service account
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
echo "🔐 Cloud Build Service Account: $CB_SA"

# 1.2. Cloud Build storage bucket kontrolü
echo "🪣 Cloud Build storage bucket kontrol ediliyor..."
BUCKET_NAME="${PROJECT_ID}_cloudbuild"
if ! gsutil ls -b gs://$BUCKET_NAME &>/dev/null; then
  echo "🪣 Cloud Build storage bucket oluşturuluyor..."
  gsutil mb -l $REGION gs://$BUCKET_NAME || echo "⚠️  Bucket zaten mevcut veya oluşturulamadı"
  # Bucket'a Cloud Build servis hesabına yetki ver
  gsutil iam ch serviceAccount:$CB_SA:roles/storage.admin gs://$BUCKET_NAME || true
  echo "✅ Cloud Build storage bucket hazır"
else
  echo "✅ Cloud Build storage bucket mevcut"
fi

# 1.3. Artifact Registry repository kontrolü
echo "📦 Artifact Registry repository kontrol ediliyor..."
if ! gcloud artifacts repositories describe $REPOSITORY \
  --location=$REGION \
  --project=$PROJECT_ID &>/dev/null; then
  echo "📦 Artifact Registry repository oluşturuluyor..."
  gcloud artifacts repositories create $REPOSITORY \
    --repository-format=docker \
    --location=$REGION \
    --project=$PROJECT_ID \
    --description="FinAsis Docker images" || echo "⚠️  Repository zaten mevcut veya oluşturulamadı"
  echo "✅ Artifact Registry repository hazır"
else
  echo "✅ Artifact Registry repository mevcut"
fi

# 1.4. Cloud Build service account IAM rolleri kontrolü
echo "🔐 Cloud Build service account IAM rolleri kontrol ediliyor..."
IAM_ROLES=$(gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$CB_SA" \
  --format="value(bindings.role)" 2>/dev/null || echo "")

if ! echo "$IAM_ROLES" | grep -q "artifactregistry.writer"; then
  echo "🔐 Artifact Registry Writer rolü veriliyor..."
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CB_SA" \
    --role="roles/artifactregistry.writer" \
    --condition=None || echo "⚠️  Rol zaten verilmiş"
fi

if ! echo "$IAM_ROLES" | grep -q "run.admin"; then
  echo "🔐 Cloud Run Admin rolü veriliyor..."
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CB_SA" \
    --role="roles/run.admin" \
    --condition=None || echo "⚠️  Rol zaten verilmiş"
fi

if ! echo "$IAM_ROLES" | grep -q "iam.serviceAccountUser"; then
  echo "🔐 Service Account User rolü veriliyor..."
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CB_SA" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None || echo "⚠️  Rol zaten verilmiş"
fi

echo ""

# 2. Git durumunu kontrol et
cd ~/FinAsis
echo "📊 Git durumu kontrol ediliyor..."
git status

# 3. Son commit SHA'sını al
COMMIT_SHA=$(git rev-parse --short HEAD)
IMAGE_TAG="${COMMIT_SHA}"
FULL_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo ""
echo "📦 Build bilgileri:"
echo "   Commit SHA: $COMMIT_SHA"
echo "   Image: $FULL_IMAGE"
echo ""

# 4. Docker build ve push
echo "🔨 Docker image build ediliyor ve push ediliyor..."
gcloud builds submit \
  --tag="$FULL_IMAGE" \
  --project=$PROJECT_ID \
  --region=$REGION

echo ""
echo "✅ Build tamamlandı!"
echo ""

# 5. Secret'ları al (Secret Manager'dan veya kullanıcıdan)
if [ -z "${DJANGO_SECRET_KEY:-}" ]; then
  echo "🔑 DJANGO_SECRET_KEY bulunamadı"
  read -sp "   DJANGO_SECRET_KEY girin: " DJANGO_SECRET_KEY
  echo ""
  export DJANGO_SECRET_KEY
fi

if [ -z "${DJANGO_DB_PASSWORD:-}" ]; then
  echo "🔑 DJANGO_DB_PASSWORD bulunamadı"
  read -sp "   DJANGO_DB_PASSWORD girin: " DJANGO_DB_PASSWORD
  echo ""
  export DJANGO_DB_PASSWORD
fi

# 7. Environment variables
ENV_VARS="MPLCONFIGDIR=/tmp/matplotlib-cache,PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1"
ENV_VARS="$ENV_VARS,DJANGO_DB_ENGINE=django.db.backends.postgresql"
ENV_VARS="$ENV_VARS,DJANGO_DB_NAME=finasis"
ENV_VARS="$ENV_VARS,DJANGO_DB_USER=finasis-app"
ENV_VARS="$ENV_VARS,DJANGO_DB_HOST=/cloudsql/finasis-478502:europe-west1:finasis-db"
ENV_VARS="$ENV_VARS,CLOUD_SQL_CONNECTION_NAME=finasis-478502:europe-west1:finasis-db"
ENV_VARS="$ENV_VARS,DJANGO_DEBUG=0,RUN_DB_MIGRATIONS=true"
ENV_VARS="$ENV_VARS,GOOGLE_CLOUD_PROJECT_NUMBER=$PROJECT_NUMBER"
ENV_VARS="$ENV_VARS,DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY"
ENV_VARS="$ENV_VARS,DJANGO_DB_PASSWORD=$DJANGO_DB_PASSWORD"

# 8. Mevcut host'u ekle
EXISTING_HOST=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(status.url)" 2>/dev/null | sed 's|https\?://||' || echo "")

if [ -n "$EXISTING_HOST" ]; then
  ENV_VARS="$ENV_VARS,CLOUD_RUN_HOST=$EXISTING_HOST"
  echo "✅ CLOUD_RUN_HOST eklendi: $EXISTING_HOST"
fi

echo ""

# 9. Service account'u al (idempotent - hata durumunda fallback)
echo "🔍 Service account kontrol ediliyor..."
SERVICE_ACCOUNT=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(spec.template.spec.serviceAccountName)" 2>/dev/null || echo "")

# Eğer service account yoksa, default compute service account'u kullan
if [ -z "$SERVICE_ACCOUNT" ]; then
  COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
  # Service account'un var olup olmadığını kontrol et
  if gcloud iam service-accounts describe "$COMPUTE_SA" --project=$PROJECT_ID &>/dev/null; then
    SERVICE_ACCOUNT="$COMPUTE_SA"
    echo "✅ Default compute service account kullanılıyor: $SERVICE_ACCOUNT"
  else
    # Service account yoksa, Cloud Run default'unu kullan (boş bırak)
    echo "⚠️  Default compute service account mevcut değil, Cloud Run default kullanılacak"
    SERVICE_ACCOUNT=""
  fi
else
  echo "✅ Mevcut service account kullanılıyor: $SERVICE_ACCOUNT"
fi

# 10. Deploy
echo "🚀 Cloud Run'a deploy ediliyor..."
gcloud run deploy $SERVICE_NAME \
  --image="$FULL_IMAGE" \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --execution-environment=gen2 \
  --memory=2Gi \
  --cpu=2 \
  --timeout=900 \
  --concurrency=40 \
  --min-instances=1 \
  --max-instances=10 \
  --service-account="$SERVICE_ACCOUNT" \
  --add-cloudsql-instances=finasis-478502:europe-west1:finasis-db \
  --cpu-boost \
  --cpu-throttling \
  --set-env-vars="$ENV_VARS" \
  --port=8080 \
  --project=$PROJECT_ID

echo ""
echo "✅ Deployment tamamlandı!"

# 11. Service URL'ini göster
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(status.url)")

echo ""
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "📋 Logları görmek için:"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --project=$PROJECT_ID --limit=50"
echo ""

