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

# VM'yi oluştur (service account belirtmeden - varsayılan kullanılır)
echo "🖥️  VM oluşturuluyor: $VM_NAME"
gcloud compute instances create $VM_NAME \
  --zone=$ZONE \
  --machine-type=$MACHINE_TYPE \
  --boot-disk-size=$DISK_SIZE \
  --boot-disk-type=pd-ssd \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --project=$PROJECT_ID \
  --scopes=https://www.googleapis.com/auth/cloud-platform

echo "✅ VM oluşturuldu!"
echo ""
echo "🔗 VM'e SSH ile bağlanmak için:"
echo "   gcloud compute ssh $VM_NAME --zone=$ZONE --project=$PROJECT_ID"
echo ""
echo "📋 Sonraki adımlar:"
echo "   1. VM'e SSH ile bağlanın"
echo "   2. Runner'ı kurun (docs/SELF_HOSTED_RUNNER_SETUP.md dosyasına bakın)"

