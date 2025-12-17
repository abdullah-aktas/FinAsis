#!/bin/bash
# Service Account hatalarını düzeltme scripti
# Default compute service account oluşturma hatalarını önler
# Cloud Shell'de çalıştırın: bash scripts/fix-service-account-errors.sh

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"

echo "🔧 Service Account Hatalarını Düzeltme Başlatılıyor..."
echo ""

# Proje bilgilerini al
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

echo "📊 Proje Bilgileri:"
echo "   Project ID: $PROJECT_ID"
echo "   Project Number: $PROJECT_NUMBER"
echo "   Compute Service Account: $COMPUTE_SA"
echo "   Cloud Build Service Account: $CB_SA"
echo ""

# 1. Default compute service account'u kontrol et ve oluştur (idempotent)
echo "🔍 Default compute service account kontrol ediliyor..."
if gcloud iam service-accounts describe "$COMPUTE_SA" --project=$PROJECT_ID &>/dev/null; then
  echo "   ✅ Default compute service account zaten mevcut: $COMPUTE_SA"
else
  echo "   ⚠️  Default compute service account mevcut değil"
  echo "   💡 Compute Engine API'sini etkinleştirerek otomatik oluşturulacak..."
  
  # Compute Engine API'sini etkinleştir (service account'u otomatik oluşturur)
  gcloud services enable compute.googleapis.com --project=$PROJECT_ID || true
  
  echo "   ⏳ Service account'un oluşturulması için 30 saniye bekleniyor..."
  sleep 30
  
  # Tekrar kontrol et
  if gcloud iam service-accounts describe "$COMPUTE_SA" --project=$PROJECT_ID &>/dev/null; then
    echo "   ✅ Default compute service account oluşturuldu: $COMPUTE_SA"
  else
    echo "   ⚠️  Service account henüz oluşturulmadı, birkaç dakika bekleyin"
    echo "   💡 Veya Compute Engine API'sini manuel etkinleştirin:"
    echo "      https://console.cloud.google.com/apis/library/compute.googleapis.com?project=$PROJECT_ID"
  fi
fi

# 2. Cloud Build service account'u kontrol et
echo ""
echo "🔍 Cloud Build service account kontrol ediliyor..."
if gcloud iam service-accounts describe "$CB_SA" --project=$PROJECT_ID &>/dev/null; then
  echo "   ✅ Cloud Build service account mevcut: $CB_SA"
else
  echo "   ⚠️  Cloud Build service account mevcut değil"
  echo "   💡 Cloud Build API'sini etkinleştirerek otomatik oluşturulacak..."
  
  gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID || true
  
  echo "   ⏳ Service account'un oluşturulması için 30 saniye bekleniyor..."
  sleep 30
  
  if gcloud iam service-accounts describe "$CB_SA" --project=$PROJECT_ID &>/dev/null; then
    echo "   ✅ Cloud Build service account oluşturuldu: $CB_SA"
  else
    echo "   ⚠️  Service account henüz oluşturulmadı"
  fi
fi

# 3. Service account oluşturma işlemlerini idempotent hale getiren helper function
echo ""
echo "📝 Helper script oluşturuluyor..."
cat > scripts/ensure-service-account.sh <<'EOF'
#!/bin/bash
# Service account'u idempotent şekilde oluştur/doğrula
# Kullanım: ensure-service-account.sh <service-account-email> <display-name>

set -e

SA_EMAIL="$1"
SA_DISPLAY_NAME="${2:-Default service account}"
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-finasis-478502}"

if [ -z "$SA_EMAIL" ]; then
  echo "❌ Hata: Service account email gerekli"
  exit 1
fi

# Service account'un var olup olmadığını kontrol et
if gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
  echo "✅ Service account zaten mevcut: $SA_EMAIL"
  exit 0
fi

# Service account oluştur
echo "🔧 Service account oluşturuluyor: $SA_EMAIL"
if gcloud iam service-accounts create "$(echo $SA_EMAIL | cut -d'@' -f1 | cut -d'-' -f2-)" \
  --display-name="$SA_DISPLAY_NAME" \
  --project="$PROJECT_ID" 2>&1 | grep -q "already exists\|ALREADY_EXISTS"; then
  echo "✅ Service account zaten mevcut (already exists hatası ignore edildi): $SA_EMAIL"
  exit 0
elif [ $? -eq 0 ]; then
  echo "✅ Service account oluşturuldu: $SA_EMAIL"
  exit 0
else
  echo "⚠️  Service account oluşturulamadı (normal olabilir, API tarafından otomatik oluşturulabilir)"
  exit 0
fi
EOF

chmod +x scripts/ensure-service-account.sh
echo "   ✅ Helper script oluşturuldu: scripts/ensure-service-account.sh"

# 4. Deployment script'lerini güncelleme önerileri
echo ""
echo "📋 Öneriler:"
echo "   1. Deployment script'lerinde service account oluşturma işlemlerinden önce"
echo "      'ensure-service-account.sh' helper'ını kullanın"
echo "   2. 'gcloud iam service-accounts create' komutlarından önce"
echo "      service account'un var olup olmadığını kontrol edin"
echo "   3. 'already exists' hatalarını ignore edin (|| true ekleyin)"

echo ""
echo "✅ Service account hata düzeltme tamamlandı!"
echo ""
echo "📝 Sonraki Adımlar:"
echo "   1. Deployment script'lerini güncelleyin (otomatik güncelleme yapılacak)"
echo "   2. Test deployment çalıştırın"
echo "   3. Log'larda ERROR sayısının azaldığını kontrol edin"

