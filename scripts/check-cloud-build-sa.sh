#!/bin/bash
# Cloud Build Service Account kontrol scripti
# Cloud Shell'de çalıştırın: bash scripts/check-cloud-build-sa.sh

set -e

PROJECT_ID="finasis-478502"

echo "🔍 Cloud Build Service Account kontrolü başlatılıyor..."
echo ""

# Project number'ı al
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

echo "📊 Proje Bilgileri:"
echo "   Project ID: $PROJECT_ID"
echo "   Project Number: $PROJECT_NUMBER"
echo "   Cloud Build Service Account: $CB_SA"
echo ""

# Cloud Build API'sinin etkin olup olmadığını kontrol et
echo "🔍 Cloud Build API durumu kontrol ediliyor..."
if gcloud services list --enabled --project=$PROJECT_ID --filter="name:cloudbuild.googleapis.com" --format="value(name)" | grep -q cloudbuild; then
  echo "✅ Cloud Build API etkin"
else
  echo "❌ Cloud Build API etkin değil!"
  echo "   Etkinleştirmek için: gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID"
fi
echo ""

# IAM policy'den service account'un rollerini kontrol et
echo "🔍 Cloud Build Service Account IAM rolleri kontrol ediliyor..."
echo ""

IAM_ROLES=$(gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$CB_SA" \
  --format="value(bindings.role)" 2>/dev/null || echo "")

if [ -z "$IAM_ROLES" ]; then
  echo "⚠️  IAM policy'de $CB_SA bulunamadı veya roller atanmamış"
  echo "   Bu normal olabilir - Cloud Build API etkinleştirildiğinde otomatik oluşturulur"
else
  echo "✅ Atanmış roller:"
  echo "$IAM_ROLES" | while read role; do
    echo "   - $role"
  done
fi
echo ""

# Gerekli rollerin var olup olmadığını kontrol et
REQUIRED_ROLES=(
  "roles/artifactregistry.writer"
  "roles/run.admin"
  "roles/iam.serviceAccountUser"
)

echo "📋 Gerekli roller kontrol ediliyor..."
MISSING_ROLES=()

for role in "${REQUIRED_ROLES[@]}"; do
  if echo "$IAM_ROLES" | grep -q "$role"; then
    echo "   ✅ $role"
  else
    echo "   ❌ $role (eksik)"
    MISSING_ROLES+=("$role")
  fi
done
echo ""

# Eksik roller varsa setup scriptini öner
if [ ${#MISSING_ROLES[@]} -gt 0 ]; then
  echo "⚠️  Bazı roller eksik!"
  echo "   Setup için çalıştırın: bash scripts/setup-cloud-build.sh"
  echo ""
  echo "   Veya manuel olarak:"
  for role in "${MISSING_ROLES[@]}"; do
    echo "   gcloud projects add-iam-policy-binding $PROJECT_ID \\"
    echo "     --member=\"serviceAccount:$CB_SA\" \\"
    echo "     --role=\"$role\""
  done
else
  echo "✅ Tüm gerekli roller atanmış!"
fi
echo ""

# Cloud Build Settings için öneri
echo "📝 Cloud Build Console Ayarları:"
echo "   1. https://console.cloud.google.com/cloud-build/settings?project=$PROJECT_ID"
echo "   2. Service account alanına şunu girin: $CB_SA"
echo "   3. Veya 'Use default compute service account' seçeneğini kaldırın"
echo ""

echo "✅ Kontrol tamamlandı!"

