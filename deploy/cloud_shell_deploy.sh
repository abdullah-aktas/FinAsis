#!/bin/bash
# Cloud Shell'den Deploy Script
# Bu script Cloud Shell'de çalıştırılmalıdır

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
REPOSITORY="finasis-app"

echo "🚀 FinAsis Production Deploy (Cloud Shell)"
echo "=========================================="
echo ""

# 1. Proje kontrolü
echo "📋 1. Proje Kontrolü"
echo "-------------------"
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo "⚠️  Proje değiştiriliyor: $CURRENT_PROJECT → $PROJECT_ID"
    gcloud config set project "$PROJECT_ID"
fi
echo "✅ Proje: $PROJECT_ID"
echo ""

# 2. Cloud Build API kontrolü ve etkinleştirme
echo "📋 2. Cloud Build API Kontrolü"
echo "------------------------------"
if ! gcloud services list --enabled --filter="name:cloudbuild.googleapis.com" --format="value(name)" | grep -q cloudbuild; then
    echo "⚠️  Cloud Build API etkin değil, etkinleştiriliyor..."
    gcloud services enable cloudbuild.googleapis.com
    echo "⏳ API etkinleştiriliyor, 30 saniye bekleniyor..."
    sleep 30
else
    echo "✅ Cloud Build API zaten etkin"
fi
echo ""

# 3. Cloud Run Admin API kontrolü
echo "📋 3. Cloud Run Admin API Kontrolü"
echo "----------------------------------"
if ! gcloud services list --enabled --filter="name:run.googleapis.com" --format="value(name)" | grep -q run; then
    echo "⚠️  Cloud Run Admin API etkin değil, etkinleştiriliyor..."
    gcloud services enable run.googleapis.com
    echo "⏳ API etkinleştiriliyor, 10 saniye bekleniyor..."
    sleep 10
else
    echo "✅ Cloud Run Admin API zaten etkin"
fi
echo ""

# 4. Artifact Registry API kontrolü
echo "📋 4. Artifact Registry API Kontrolü"
echo "-------------------------------------"
if ! gcloud services list --enabled --filter="name:artifactregistry.googleapis.com" --format="value(name)" | grep -q artifactregistry; then
    echo "⚠️  Artifact Registry API etkin değil, etkinleştiriliyor..."
    gcloud services enable artifactregistry.googleapis.com
    echo "⏳ API etkinleştiriliyor, 10 saniye bekleniyor..."
    sleep 10
else
    echo "✅ Artifact Registry API zaten etkin"
fi
echo ""

# 5. Cloud Build config kontrolü
echo "📋 5. Cloud Build Config Kontrolü"
echo "----------------------------------"
if [ ! -f "deploy/cloud_run/cloudbuild.yaml" ]; then
    echo "❌ deploy/cloud_run/cloudbuild.yaml bulunamadı!"
    echo "   Lütfen dosyanın varlığını kontrol edin."
    exit 1
fi
echo "✅ Cloud Build config mevcut: deploy/cloud_run/cloudbuild.yaml"
echo ""

# 6. Git durumu
echo "📋 6. Git Durumu"
echo "----------------"
git pull origin main || echo "⚠️  Git pull başarısız, devam ediliyor..."
LATEST_COMMIT=$(git rev-parse --short HEAD)
echo "✅ Son commit: $LATEST_COMMIT"
echo ""

# 7. Deploy başlatma
echo "📋 7. Cloud Build Deploy Başlatılıyor"
echo "-------------------------------------"
echo "   Bu işlem 10-15 dakika sürebilir..."
echo "   Lütfen bekleyin..."
echo ""

# Credential override'ı temizle (eğer varsa)
gcloud config unset auth/credential_file_override 2>/dev/null || true
unset GOOGLE_APPLICATION_CREDENTIALS 2>/dev/null || true

# Cloud Build submit
gcloud builds submit \
    --config=deploy/cloud_run/cloudbuild.yaml \
    --region="$REGION" \
    --substitutions="_SERVICE=${SERVICE_NAME},_REGION=${REGION},_REPOSITORY=${REPOSITORY}" \
    --project="$PROJECT_ID"

echo ""
echo "✅ Deploy tamamlandı!"
echo ""

# 8. Servis durumu
echo "📋 8. Servis Durumu"
echo "-------------------"
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo "✅ Servis URL: $SERVICE_URL"
    echo ""
    echo "🧪 Test Komutları:"
    echo "   curl $SERVICE_URL/health/"
    echo "   curl $SERVICE_URL/accounts/password_reset/"
else
    echo "⚠️  Servis URL alınamadı"
fi

echo ""
echo "✅ Deploy işlemi tamamlandı!"
echo "   Logları kontrol etmek için:"
echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=50"

