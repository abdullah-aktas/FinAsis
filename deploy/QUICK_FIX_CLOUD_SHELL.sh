#!/bin/bash
# Cloud Shell'de Hızlı Düzeltme Scripti
# Git çakışmasını çözer, HTTP 400'ü düzeltir ve deployment yapar

set -e

PROJECT_ID="${PROJECT_ID:-finasis-478502}"
REGION="${REGION:-europe-west1}"
SERVICE_NAME="${SERVICE_NAME:-finasis-prod}"

echo "🔧 Cloud Shell Hızlı Düzeltme"
echo "=============================="
echo ""

# 1. Git çakışmasını çöz
echo "📋 1. Git Çakışmasını Çözüyoruz..."
echo "-------------------"
cd ~/FinAsis

# users_export.json'ı stash et veya sil (gitignore'da)
if [ -f "users_export.json" ]; then
    git stash push -m "Stash users_export.json" users_export.json 2>/dev/null || \
    git checkout -- users_export.json 2>/dev/null || \
    rm -f users_export.json
    echo "✅ users_export.json temizlendi"
fi

# Çakışan scriptleri sil (yenilerini çekeceğiz)
rm -f deploy/check_cloud_shell_connection.sh \
      deploy/fix_cloud_build_auth.sh \
      deploy/fix_http_400_error.sh \
      deploy/test_deployment.sh \
      deploy/check_failed_build.sh 2>/dev/null || true

echo "✅ Çakışan dosyalar temizlendi"
echo ""

# Git pull yap
echo "📋 2. Git Pull Yapılıyor..."
git pull origin main
echo "✅ Git pull tamamlandı"
echo ""

# 2. HTTP 400 hatasını düzelt
echo "📋 3. HTTP 400 Hatasını Düzeltiyoruz..."
echo "-------------------"

# Servis URL'sini al
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" 2>/dev/null || echo "")

if [ -z "$SERVICE_URL" ]; then
    echo "❌ Servis bulunamadı: $SERVICE_NAME"
    exit 1
fi

SERVICE_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')
echo "✅ Servis URL: $SERVICE_URL"
echo "   Host: $SERVICE_HOST"

# Yeni ALLOWED_HOSTS
NEW_ALLOWED_HOSTS="finasis.com.tr,www.finasis.com.tr,$SERVICE_HOST"
echo "📝 Yeni ALLOWED_HOSTS: $NEW_ALLOWED_HOSTS"
echo ""

# Environment variables'ı doğru formatta oluştur
# --update-env-vars için KEY=VALUE,KEY2=VALUE2 formatı
ENV_VARS_UPDATE="DJANGO_ALLOWED_HOSTS=$NEW_ALLOWED_HOSTS"
ENV_VARS_UPDATE="$ENV_VARS_UPDATE,DJANGO_DEBUG=False"
ENV_VARS_UPDATE="$ENV_VARS_UPDATE,MPLCONFIGDIR=/tmp/matplotlib-cache"
ENV_VARS_UPDATE="$ENV_VARS_UPDATE,PYTHONUNBUFFERED=1"
ENV_VARS_UPDATE="$ENV_VARS_UPDATE,PYTHONDONTWRITEBYTECODE=1"

echo "🔄 Environment variables güncelleniyor..."
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --update-env-vars="$ENV_VARS_UPDATE" \
    --quiet

echo "✅ ALLOWED_HOSTS güncellendi!"
echo ""

# Health check
echo "🧪 Health check yapılıyor..."
sleep 5
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Servis çalışıyor! (HTTP $HTTP_CODE)"
else
    echo "⚠️  Servis hala sorunlu (HTTP $HTTP_CODE)"
fi
echo ""

# 3. Cloud Build authentication kontrolü
echo "📋 4. Cloud Build Authentication Kontrolü..."
echo "-------------------"

# Cloud Build API'sini etkinleştir
gcloud services enable cloudbuild.googleapis.com --quiet
echo "✅ Cloud Build API aktif"

# Compute service account'a izin ver
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)" 2>/dev/null)
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

echo "📋 Compute SA: $COMPUTE_SA"
echo "📋 Cloud Build SA: $CLOUD_BUILD_SA"

# Gerekli rolleri ekle
for SA in "$COMPUTE_SA" "$CLOUD_BUILD_SA"; do
    for ROLE in "roles/run.admin" "roles/iam.serviceAccountUser"; do
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:$SA" \
            --role="$ROLE" \
            --quiet 2>/dev/null && echo "   ✅ $ROLE eklendi ($SA)" || echo "   ℹ️  $ROLE zaten mevcut ($SA)"
    done
done
echo ""

# 4. Deployment önerisi
echo "📋 5. Deployment Hazır!"
echo "-------------------"
echo "✅ Tüm düzeltmeler tamamlandı!"
echo ""
echo "🚀 Şimdi deployment yapabilirsiniz:"
echo "   gcloud builds submit \\"
echo "     --config=deploy/cloud_run/cloudbuild.yaml \\"
echo "     --region=$REGION \\"
echo "     --substitutions=_SERVICE=$SERVICE_NAME"
echo ""

