#!/bin/bash
# Self-hosted runner için VM oluşturma scripti

set -e

PROJECT_ID="finasis-478502"
ZONE="europe-west1-b"
VM_NAME="finasis-runner"
MACHINE_TYPE="e2-standard-8"
DISK_SIZE="200GB"  # 100GB yerine 200GB (I/O performansı için)

echo "🖥️  Self-hosted runner VM oluşturuluyor..."

# Proje ID'sini ayarla
gcloud config set project $PROJECT_ID

# Compute Engine API'yi etkinleştir
echo "📡 Compute Engine API etkinleştiriliyor..."
gcloud services enable compute.googleapis.com --project=$PROJECT_ID

# Default service account'u kontrol et
echo "🔐 Service account kontrol ediliyor..."
DEFAULT_SA="${PROJECT_ID}@appspot.gserviceaccount.com" || true
COMPUTE_SA=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")-compute@developer.gserviceaccount.com

# App Engine'i etkinleştir (default service account için gerekli)
echo "🚀 App Engine etkinleştiriliyor (default service account için)..."
gcloud app create --region=europe-west1 --project=$PROJECT_ID 2>/dev/null || echo "⚠️  App Engine zaten mevcut veya oluşturulamadı"

# Birkaç saniye bekle (service account'ların oluşması için)
echo "⏳ Service account'ların hazır olması bekleniyor..."
sleep 5

# VM'yi oluştur (idempotent - service account kontrolü ile)
echo "🖥️  VM oluşturuluyor: $VM_NAME"

# Önce compute service account'u dene (en güvenilir)
if gcloud iam service-accounts describe "$COMPUTE_SA" --project=$PROJECT_ID &>/dev/null; then
  echo "✅ Compute service account kullanılıyor: $COMPUTE_SA"
  gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --boot-disk-size=$DISK_SIZE \
    --boot-disk-type=pd-ssd \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --project=$PROJECT_ID \
    --service-account=$COMPUTE_SA \
    --scopes=https://www.googleapis.com/auth/cloud-platform || {
    echo "⚠️  VM oluşturma hatası (zaten mevcut olabilir)"
    exit 0
  }
# Sonra appspot service account'u dene
elif gcloud iam service-accounts describe "$APPSPOT_SA" --project=$PROJECT_ID &>/dev/null; then
  echo "✅ Appspot service account kullanılıyor: $APPSPOT_SA"
  gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --boot-disk-size=$DISK_SIZE \
    --boot-disk-type=pd-ssd \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --project=$PROJECT_ID \
    --service-account=$APPSPOT_SA \
    --scopes=https://www.googleapis.com/auth/cloud-platform || {
    echo "⚠️  VM oluşturma hatası (zaten mevcut olabilir)"
    exit 0
  }
else
  echo "⚠️  Service account bulunamadı, service account olmadan denenecek..."
  # Service account olmadan dene (no-scopes)
  gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --boot-disk-size=$DISK_SIZE \
    --boot-disk-type=pd-ssd \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --project=$PROJECT_ID \
    --no-service-account \
    --no-scopes || {
    echo "⚠️  VM oluşturma hatası (zaten mevcut olabilir veya service account gerekli)"
    # VM zaten mevcut olabilir, kontrol et
    if gcloud compute instances describe $VM_NAME --zone=$ZONE --project=$PROJECT_ID &>/dev/null; then
      echo "✅ VM zaten mevcut: $VM_NAME"
      exit 0
    else
      echo "❌ VM oluşturulamadı. Lütfen Cloud Console'dan manuel oluşturun."
      exit 1
    fi
  }
fi

echo "✅ VM oluşturuldu!"
echo ""
echo "🔗 VM'e SSH ile bağlanmak için:"
echo "   gcloud compute ssh $VM_NAME --zone=$ZONE --project=$PROJECT_ID"
echo ""
echo "📋 Sonraki adımlar:"
echo "   1. VM'e SSH ile bağlanın"
echo "   2. Runner'ı kurun (docs/SELF_HOSTED_RUNNER_SETUP.md dosyasına bakın)"

