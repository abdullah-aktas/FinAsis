#!/bin/bash
# Tam Deployment Script - Tüm projeyi baştan sona canlıya alır
# Cloud Shell'de çalıştırın

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
IMAGE_SERVICE="finasis-api"
REPOSITORY="finasis-app"
TRIGGER_NAME="finasis-prod-europe-west1-abdullah-aktas-FinAsis"

echo "🚀 FinAsis Tam Deployment"
echo "=========================="
echo ""
echo "Bu script tüm projeyi baştan sona canlıya alacak:"
echo "  ✅ Son kodları çekecek"
echo "  ✅ Tüm dosyaları kontrol edecek"
echo "  ✅ Cloud Build ile deploy edecek"
echo "  ✅ Migration'ları çalıştıracak"
echo "  ✅ Static dosyaları toplayacak"
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
echo "📋 2. Git Repository Güncelleme"
echo "-------------------------------"
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
    git pull origin main || {
        echo "⚠️  Git pull başarısız, devam ediliyor..."
    }
fi
echo ""

# 3. Dosya kontrolü
echo "📋 3. Kritik Dosya Kontrolü"
echo "----------------------------"
CRITICAL_FILES=(
    "Dockerfile"
    "deploy/cloud_run/cloudbuild.yaml"
    "deploy/entrypoint.sh"
    "requirements.txt"
    "manage.py"
    "config/settings/base.py"
    "config/urls.py"
)

MISSING_FILES=()
for file in "${CRITICAL_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
        echo "❌ Eksik: $file"
    else
        echo "✅ Mevcut: $file"
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo ""
    echo "❌ Kritik dosyalar eksik! Deployment durduruluyor."
    exit 1
fi
echo ""

# 4. Migration dosyaları kontrolü
echo "📋 4. Migration Dosyaları Kontrolü"
echo "----------------------------------"
MIGRATION_COUNT=$(find . -path "*/migrations/*.py" -not -path "*/__pycache__/*" | wc -l)
echo "✅ Bulunan migration dosyası: $MIGRATION_COUNT"
echo ""

# 5. Cloud Build trigger kontrolü
echo "📋 5. Cloud Build Trigger Kontrolü"
echo "-----------------------------------"
TRIGGER_ID=$(gcloud builds triggers list \
    --filter="name:$TRIGGER_NAME" \
    --format="value(id)" \
    --region=$REGION \
    --project=$PROJECT_ID 2>/dev/null | head -1)

if [ -z "$TRIGGER_ID" ]; then
    echo "⚠️  Cloud Build trigger bulunamadı!"
    echo "📋 Mevcut trigger'lar:"
    gcloud builds triggers list --region=$REGION --project=$PROJECT_ID
    echo ""
    echo "❌ Deployment durduruluyor. Lütfen önce Cloud Build trigger oluşturun."
    exit 1
fi

echo "✅ Trigger bulundu: $TRIGGER_NAME (ID: $TRIGGER_ID)"
echo ""

# 6. Deployment başlatma
echo "📋 6. Deployment Başlatılıyor"
echo "-----------------------------"
echo "🚀 Cloud Build trigger'ı tetikleniyor..."
echo ""

gcloud builds triggers run $TRIGGER_ID \
    --branch=main \
    --region=$REGION \
    --project=$PROJECT_ID

echo ""
echo "✅ Cloud Build trigger başarıyla tetiklendi!"
echo ""

# 7. Build durumu takibi
echo "📋 7. Build Durumu"
echo "-----------------"
echo "📊 Build durumunu takip edin:"
echo "   https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
echo ""
echo "⏳ Build tamamlanması yaklaşık 10-15 dakika sürebilir."
echo ""

# 8. Sonraki adımlar
echo "📋 8. Deployment Sonrası Kontroller"
echo "-----------------------------------"
echo "Deployment tamamlandıktan sonra şunları kontrol edin:"
echo ""
echo "1. Cloud Run servis durumu:"
echo "   gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
echo ""
echo "2. Servis URL'i:"
echo "   gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format='value(status.url)'"
echo ""
echo "3. Health check:"
echo "   curl \$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format='value(status.url)')/health/"
echo ""
echo "4. Logları kontrol et:"
echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --limit=50"
echo ""

echo "🎉 Deployment başlatıldı!"
echo "📊 Build durumunu yukarıdaki linkten takip edebilirsiniz."

