#!/bin/bash
# Canlıdaki projeyi güncellemek için Cloud Shell komutları
# Cloud Shell'de çalıştırın

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
IMAGE_SERVICE="finasis-api"
REPOSITORY="finasis-app"
TRIGGER_NAME="finasis-prod-europe-west1-abdullah-aktas-FinAsis"

echo "🚀 FinAsis Production Deployment"
echo "=================================="
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
        echo "📥 Son değişiklikleri çekiyorum..."
        git pull origin main
    else
        echo "📥 Repository clone ediliyor..."
        git clone https://github.com/abdullah-aktas/FinAsis.git
        cd FinAsis
    fi
else
    echo "✅ Git repository mevcut"
    echo "📥 Son değişiklikleri çekiyorum..."
    git pull origin main || echo "⚠️  Git pull başarısız, devam ediliyor..."
fi
echo ""

# 3. Yöntem seçimi
echo "📋 3. Deployment Yöntemi Seçimi"
echo "-------------------------------"
echo "1️⃣  Cloud Build Trigger'ı Tetikle (Önerilen - Hızlı)"
echo "2️⃣  Direkt Cloud Build Submit (Manuel)"
echo ""
read -p "Hangi yöntemi kullanmak istersiniz? (1/2): " METHOD

if [ "$METHOD" = "1" ]; then
    # Yöntem 1: Cloud Build Trigger'ı Tetikle
    echo ""
    echo "🚀 Cloud Build Trigger'ı tetikleniyor..."
    echo "📋 Trigger: $TRIGGER_NAME"
    
    # Trigger ID'yi bul
    TRIGGER_ID=$(gcloud builds triggers list \
        --filter="name:$TRIGGER_NAME" \
        --format="value(id)" \
        --region=$REGION \
        --project=$PROJECT_ID | head -1)
    
    if [ -z "$TRIGGER_ID" ]; then
        echo "❌ Trigger bulunamadı!"
        echo "📋 Mevcut trigger'lar:"
        gcloud builds triggers list --region=$REGION --project=$PROJECT_ID
        exit 1
    fi
    
    echo "✅ Trigger ID: $TRIGGER_ID"
    echo ""
    
    # Trigger'ı tetikle
    gcloud builds triggers run $TRIGGER_ID \
        --branch=main \
        --region=$REGION \
        --project=$PROJECT_ID
    
    echo ""
    echo "✅ Cloud Build trigger başarıyla tetiklendi!"
    echo "📊 Build durumunu takip edin:"
    echo "   https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
    
elif [ "$METHOD" = "2" ]; then
    # Yöntem 2: Direkt Cloud Build Submit
    echo ""
    echo "🚀 Cloud Build Submit başlatılıyor..."
    
    gcloud builds submit \
        --config=deploy/cloud_run/cloudbuild.yaml \
        --region=$REGION \
        --substitutions=_SERVICE=$IMAGE_SERVICE,_CLOUD_RUN_SERVICE=$SERVICE_NAME,_REGION=$REGION,_REPOSITORY=$REPOSITORY,_CLOUD_SQL_CONNECTION="",_CLOUD_RUN_ENV_VARS="",_CLOUD_RUN_SECRETS="" \
        --project=$PROJECT_ID
    
    echo ""
    echo "✅ Cloud Build başarıyla tamamlandı!"
    echo "📊 Build durumunu takip edin:"
    echo "   https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
    
else
    echo "❌ Geçersiz seçim!"
    exit 1
fi

echo ""
echo "🎉 Deployment tamamlandı!"
echo "🔗 Cloud Run servisi:"
echo "   https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME?project=$PROJECT_ID"

