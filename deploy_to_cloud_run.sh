#!/bin/bash
# FinAsis Cloud Run Deploy Script (Cloud SQL ile)
# Cloud Shell'de çalıştırın

set -e  # Hata durumunda dur

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
REPOSITORY="finasis-app"
IMAGE_NAME="finasis-api"
IMAGE_TAG="latest"

echo "🚀 FinAsis Cloud Run Deploy Başlatılıyor..."
echo "=========================================="

# Projeyi ayarla
gcloud config set project "$PROJECT_ID"

# Cloud SQL instance adını bul (önce listeleyelim)
echo "🔍 Cloud SQL instance'ları listeleniyor..."
gcloud sql instances list

echo ""
echo "⚠️  Yukarıdaki listeden Cloud SQL instance adınızı girin:"
echo "   Örnek format: PROJECT_ID:REGION:INSTANCE_NAME"
echo "   Örnek: finasis-478502:europe-west1:finasis-db"
read -p "Cloud SQL Connection Name: " CLOUD_SQL_INSTANCE

if [ -z "$CLOUD_SQL_INSTANCE" ]; then
  echo "❌ Cloud SQL instance adı girilmedi. Deploy iptal ediliyor."
  exit 1
fi

# Artifact Registry repository'sinin var olduğundan emin ol
echo ""
echo "📦 Artifact Registry repository kontrol ediliyor..."
if ! gcloud artifacts repositories describe "$REPOSITORY" --location="$REGION" &>/dev/null; then
  echo "⚠️  Repository bulunamadı, oluşturuluyor..."
  gcloud artifacts repositories create "$REPOSITORY" \
    --repository-format=docker \
    --location="$REGION" \
    --description="FinAsis application container images"
fi

# Docker authentication
echo ""
echo "🔐 Docker authentication yapılıyor..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# Image full path
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

# Eğer Cloud Shell'de repo yoksa clone et
if [ ! -d "FinAsis" ]; then
  echo ""
  echo "📥 Repository clone ediliyor..."
  git clone https://github.com/abdullah-aktas/FinAsis.git
  cd FinAsis
else
  echo ""
  echo "📥 Repository güncelleniyor..."
  cd FinAsis
  git pull origin main
fi

# Docker image build
echo ""
echo "🔨 Docker image build ediliyor (bu işlem biraz zaman alabilir)..."
docker build -t "$IMAGE_URI" .

# Image push
echo ""
echo "📤 Image Artifact Registry'ye push ediliyor..."
docker push "$IMAGE_URI"

# Cloud Run URL'ini al (deploy öncesi mevcut servisten)
echo ""
echo "🔍 Mevcut Cloud Run URL'i alınıyor..."
EXISTING_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --platform=managed \
  --region="$REGION" \
  --format='value(status.url)' 2>/dev/null || echo "")

# Cloud Run deploy (Cloud SQL ile)
echo ""
echo "🚀 Cloud Run'a deploy ediliyor (Cloud SQL bağlantısı ile)..."
gcloud run deploy "$SERVICE_NAME" \
  --image="$IMAGE_URI" \
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
  --add-cloudsql-instances="$CLOUD_SQL_INSTANCE" \
  --set-env-vars="MPLCONFIGDIR=/tmp/matplotlib-cache,PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_INSTANCE,DJANGO_DEBUG=False,CLOUD_RUN_URL=$EXISTING_URL"

# Deploy sonrası yeni URL'i al ve güncelle
echo ""
echo "🔄 Yeni Cloud Run URL'i alınıyor ve environment variable güncelleniyor..."
NEW_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --platform=managed \
  --region="$REGION" \
  --format='value(status.url)')

if [ "$NEW_URL" != "$EXISTING_URL" ] && [ -n "$NEW_URL" ]; then
  echo "📝 Yeni URL bulundu, environment variable güncelleniyor: $NEW_URL"
  gcloud run services update "$SERVICE_NAME" \
    --platform=managed \
    --region="$REGION" \
    --update-env-vars="CLOUD_RUN_URL=$NEW_URL,CLOUD_RUN_HOST=$(echo $NEW_URL | sed 's|https\?://||' | sed 's|/.*||')"
fi

# Deploy sonrası URL kontrolü
echo ""
echo "✅ Deploy tamamlandı!"
echo "=========================================="
URL=$(gcloud run services describe "$SERVICE_NAME" \
  --platform=managed \
  --region="$REGION" \
  --format='value(status.url)')
echo "🌐 Canlı URL: $URL"
echo ""
echo "📊 Servis durumu:"
gcloud run services describe "$SERVICE_NAME" \
  --platform=managed \
  --region="$REGION" \
  --format='table(status.url,status.latestReadyRevisionName,status.conditions[0].status,spec.template.spec.containers[0].image)'

