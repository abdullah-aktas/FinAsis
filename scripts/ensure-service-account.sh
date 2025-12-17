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

# Service account ID'sini email'den çıkar
SA_ID=$(echo "$SA_EMAIL" | cut -d'@' -f1)

# Eğer compute service account ise (PROJECT_NUMBER-compute@developer.gserviceaccount.com formatında)
# Compute Engine API'sini etkinleştirerek otomatik oluşturulmasını sağla
if echo "$SA_EMAIL" | grep -q "compute@developer.gserviceaccount.com"; then
  echo "🔧 Compute service account için Compute Engine API etkinleştiriliyor..."
  gcloud services enable compute.googleapis.com --project="$PROJECT_ID" || true
  echo "⏳ Service account'un oluşturulması için 30 saniye bekleniyor..."
  sleep 30
  
  # Tekrar kontrol et
  if gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
    echo "✅ Compute service account oluşturuldu: $SA_EMAIL"
    exit 0
  else
    echo "⚠️  Service account henüz oluşturulmadı (normal olabilir, birkaç dakika bekleyin)"
    exit 0
  fi
fi

# Diğer service account'lar için manuel oluşturma dene
echo "🔧 Service account oluşturuluyor: $SA_EMAIL"
if gcloud iam service-accounts create "$SA_ID" \
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

