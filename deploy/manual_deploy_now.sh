#!/bin/bash
# Manuel Deploy Script - Google Cloud Shell için
# Bu script'i Cloud Shell'de çalıştırın

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
REPOSITORY="finasis-app"

echo "🚀 FinAsis Production Deploy"
echo "============================"
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

# 2. Git durumu kontrolü
echo "📋 2. Git Durumu"
echo "----------------"
if [ ! -d ".git" ]; then
    echo "⚠️  Git repository bulunamadı. Clone ediliyor..."
    cd ~
    if [ -d "FinAsis" ]; then
        cd FinAsis
        git pull origin main
    else
        git clone https://github.com/abdullah-aktas/FinAsis.git
        cd FinAsis
    fi
else
    echo "✅ Git repository mevcut"
    git pull origin main || echo "⚠️  Git pull başarısız, devam ediliyor..."
fi
echo ""

# 3. Cloud Build API kontrolü
echo "📋 3. Cloud Build API Kontrolü"
echo "------------------------------"
if ! gcloud services list --enabled --filter="name:cloudbuild.googleapis.com" --format="value(name)" | grep -q cloudbuild; then
    echo "⚠️  Cloud Build API etkin değil, etkinleştiriliyor..."
    gcloud services enable cloudbuild.googleapis.com
    echo "⏳ API etkinleştiriliyor, 30 saniye bekleniyor..."
    sleep 30
fi
echo "✅ Cloud Build API etkin"
echo ""

# 4. Cloud Build config kontrolü
echo "📋 4. Cloud Build Config Kontrolü"
echo "----------------------------------"
if [ ! -f "deploy/cloud_run/cloudbuild.yaml" ]; then
    echo "❌ deploy/cloud_run/cloudbuild.yaml bulunamadı!"
    echo "   Lütfen dosyanın varlığını kontrol edin."
    exit 1
fi
echo "✅ Cloud Build config mevcut"
echo ""

# 5. Deploy başlatma
echo "📋 5. Cloud Build Deploy Başlatılıyor"
echo "-------------------------------------"
echo "   Bu işlem 10-15 dakika sürebilir..."
echo "   Lütfen bekleyin..."
echo ""

gcloud builds submit \
    --config=deploy/cloud_run/cloudbuild.yaml \
    --region="$REGION" \
    --substitutions="_SERVICE=${SERVICE_NAME},_REGION=${REGION},_REPOSITORY=${REPOSITORY}" \
    --project="$PROJECT_ID"

echo ""
echo "✅ Deploy tamamlandı!"
echo ""
echo "📋 6. Servis Durumu"
echo "-------------------"
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo "✅ Servis URL: $SERVICE_URL"
    echo ""
    echo "🧪 Health Check Test:"
    echo "   curl $SERVICE_URL/health/"
    echo ""
    echo "🧪 Password Reset Test:"
    echo "   curl $SERVICE_URL/accounts/password_reset/"
else
    echo "⚠️  Servis URL alınamadı"
fi

echo ""
echo "✅ Deploy işlemi tamamlandı!"
echo "   Logları kontrol etmek için:"
echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=50"

