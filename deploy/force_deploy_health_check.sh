#!/bin/bash
# Health check endpoint'lerini force deploy et

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
REPOSITORY="finasis-app"

echo "🚀 Health Check Endpoint'leri Force Deploy"
echo "==========================================="
echo ""

# 1. GitHub Actions'ı manuel tetikle (eğer mümkünse)
echo "📋 1. GitHub Actions Manuel Tetikleme"
echo "-------------------------------------"
echo "GitHub Actions'ı manuel tetiklemek için:"
echo "1. https://github.com/abdullah-aktas/FinAsis/actions adresine gidin"
echo "2. 'Deploy to Cloud Run' workflow'unu bulun"
echo "3. Sağ üstteki 'Run workflow' butonuna tıklayın"
echo "4. Branch: main seçin"
echo "5. 'Run workflow' butonuna tıklayın"
echo ""
read -p "GitHub Actions'ı tetiklediniz mi? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "✅ GitHub Actions tetiklendi, deploy bekleniyor..."
    echo "   Deploy tamamlanması 5-10 dakika sürebilir."
    echo ""
    echo "   Deploy durumunu kontrol etmek için:"
    echo "   https://github.com/abdullah-aktas/FinAsis/actions"
    exit 0
fi

# 2. Cloud Build ile direkt deploy
echo "📋 2. Cloud Build ile Deploy"
echo "-------------------------------------"
echo "Cloud Build API kontrol ediliyor..."

if ! gcloud services list --enabled --filter="name:cloudbuild.googleapis.com" --format="value(name)" | grep -q cloudbuild; then
    echo "⚠️  Cloud Build API etkin değil, etkinleştiriliyor..."
    gcloud services enable cloudbuild.googleapis.com
    echo "⏳ API etkinleştiriliyor, 30 saniye bekleniyor..."
    sleep 30
fi

echo "✅ Cloud Build API etkin"
echo ""
echo "🔨 Cloud Build başlatılıyor..."
echo "   Bu işlem 10-15 dakika sürebilir..."

# Cloud Build submit
if gcloud builds submit \
    --config=deploy/cloud_run/cloudbuild.yaml \
    --region="$REGION" \
    --substitutions="_SERVICE=${SERVICE_NAME},_REGION=${REGION},_REPOSITORY=${REPOSITORY},_IMAGE_TAG=latest" \
    --project="$PROJECT_ID" 2>&1 | tee /tmp/cloudbuild_force.log; then
    echo ""
    echo "✅ Cloud Build başarılı!"
    echo ""
    echo "⏳ Cloud Run servisinin güncellenmesini bekleyin (2-3 dakika)..."
    sleep 120
    echo ""
    echo "🔍 Health check endpoint'lerini test edin:"
    echo "   curl https://finasis.com.tr/health/"
else
    echo ""
    echo "❌ Cloud Build başarısız oldu."
    echo ""
    echo "Alternatif çözümler:"
    echo "1. GitHub Actions'ı manuel tetikleyin (önerilen)"
    echo "2. Cloud Console'dan Cloud Build trigger oluşturun"
    echo ""
    echo "Detaylı log: /tmp/cloudbuild_force.log"
    exit 1
fi

