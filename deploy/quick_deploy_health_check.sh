#!/bin/bash
# Health check endpoint'lerini deploy etmek için hızlı script
# Cloud Build API sorunu varsa alternatif yöntemler dener

set -e

cd ~/FinAsis || exit 1

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
REPOSITORY="finasis-app"

echo "🚀 Health Check Endpoint'leri Deploy"
echo "======================================"
echo ""

# 1. Cloud Build API kontrolü
echo "📋 1. Cloud Build API kontrolü..."
if ! gcloud services list --enabled --filter="name:cloudbuild.googleapis.com" --format="value(name)" | grep -q cloudbuild; then
    echo "⚠️  Cloud Build API etkin değil, etkinleştiriliyor..."
    gcloud services enable cloudbuild.googleapis.com
    echo "⏳ API etkinleştiriliyor, 30 saniye bekleniyor..."
    sleep 30
else
    echo "✅ Cloud Build API etkin"
fi

# 2. Cloud Build servis hesabı izinlerini kontrol et
echo ""
echo "📋 2. Cloud Build servis hesabı izinleri kontrol ediliyor..."
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)" 2>/dev/null || echo "")
if [ -n "$PROJECT_NUMBER" ]; then
    CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
    echo "   Cloud Build SA: $CLOUD_BUILD_SA"
    
    # Rolleri kontrol et
    HAS_RUN_ADMIN=$(gcloud projects get-iam-policy "$PROJECT_ID" \
        --flatten="bindings[].members" \
        --filter="bindings.members:serviceAccount:${CLOUD_BUILD_SA} AND bindings.role:roles/run.admin" \
        --format="value(bindings.role)" 2>/dev/null | wc -l)
    
    if [ "$HAS_RUN_ADMIN" -eq 0 ]; then
        echo "⚠️  Cloud Build SA'ya run.admin rolü ekleniyor..."
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:${CLOUD_BUILD_SA}" \
            --role="roles/run.admin" \
            --condition=None 2>/dev/null || echo "   (Rol zaten var veya eklenemedi)"
    fi
fi

# 3. Deploy yöntemi seç
echo ""
echo "📋 3. Deploy yöntemi seçiliyor..."

# Yöntem 1: Doğru Cloud Build config ile
echo "   Yöntem 1: Cloud Build (deploy/cloud_run/cloudbuild.yaml) deneniyor..."
if gcloud builds submit \
    --config=deploy/cloud_run/cloudbuild.yaml \
    --region="$REGION" \
    --substitutions="_SERVICE=${SERVICE_NAME},_REGION=${REGION},_REPOSITORY=${REPOSITORY},_IMAGE_TAG=latest" \
    2>&1 | tee /tmp/cloudbuild.log; then
    echo "✅ Cloud Build başarılı!"
    exit 0
else
    echo "⚠️  Cloud Build başarısız, alternatif yöntem deneniyor..."
fi

# Yöntem 2: Deploy script
if [ -f "deploy_to_cloud_run.sh" ]; then
    echo ""
    echo "   Yöntem 2: deploy_to_cloud_run.sh script'i deneniyor..."
    chmod +x deploy_to_cloud_run.sh
    if ./deploy_to_cloud_run.sh; then
        echo "✅ Deploy script başarılı!"
        exit 0
    else
        echo "⚠️  Deploy script başarısız..."
    fi
fi

# Yöntem 3: Manuel bilgi
echo ""
echo "❌ Otomatik deploy başarısız oldu."
echo ""
echo "Manuel deploy için:"
echo "1. GitHub Actions kullanın (otomatik deploy)"
echo "2. Veya Cloud Console'dan Cloud Build trigger oluşturun"
echo "3. Veya deploy/cloud_run/cloudbuild.yaml dosyasını kontrol edin"
echo ""
echo "Detaylı log: /tmp/cloudbuild.log"

exit 1

