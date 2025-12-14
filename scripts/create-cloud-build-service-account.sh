#!/bin/bash
# Cloud Build Service Account oluşturma scripti
# Cloud Shell'de çalıştırın: bash scripts/create-cloud-build-service-account.sh

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"

echo "🔧 Cloud Build Service Account oluşturuluyor..."
echo ""

# Proje bilgilerini al
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

echo "📊 Proje Bilgileri:"
echo "   Project ID: $PROJECT_ID"
echo "   Project Number: $PROJECT_NUMBER"
echo "   Cloud Build Service Account: $CB_SA"
echo ""

# 1. Cloud Build API'sini etkinleştir
echo "📡 Cloud Build API etkinleştiriliyor..."
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID

echo ""
echo "⏳ Cloud Build API'sinin tam etkinleşmesi için 30 saniye bekleniyor..."
sleep 30

# 2. Service account'un var olup olmadığını kontrol et
echo ""
echo "🔍 Cloud Build service account kontrol ediliyor..."
if gcloud iam service-accounts describe $CB_SA --project=$PROJECT_ID &>/dev/null; then
  echo "   ✅ Cloud Build service account zaten mevcut: $CB_SA"
else
  echo "   ⚠️  Cloud Build service account henüz oluşturulmamış"
  echo "   Service account'u tetiklemek için test build başlatılıyor..."
  echo ""
  
  # Test build başlat (service account'u tetiklemek için)
  # Boş bir dizinde minimal build başlat (tüm projeyi yüklememek için)
  TEST_BUILD_DIR="/tmp/test-build-$(date +%s)"
  TEST_BUILD_YAML="$TEST_BUILD_DIR/cloudbuild.yaml"
  mkdir -p "$TEST_BUILD_DIR"
  
  cat > "$TEST_BUILD_YAML" <<EOF
steps:
- name: 'ubuntu'
  args: ['echo', 'Test build to trigger Cloud Build service account creation']
timeout: "60s"
EOF
  
  echo "   🚀 Test build başlatılıyor (boş dizinde, hızlı)..."
  cd "$TEST_BUILD_DIR"
  if gcloud builds submit --config=cloudbuild.yaml --project=$PROJECT_ID --quiet 2>&1 | grep -q "SUCCESS\|WORKING"; then
    echo "   ✅ Test build başlatıldı, service account oluşturuluyor..."
    echo "   ⏳ Service account'un oluşturulması için 15 saniye bekleniyor..."
    sleep 15
  else
    echo "   ⚠️  Test build başlatılamadı (NOT_FOUND hatası normal olabilir)"
    echo "   💡 Cloud Build API'sinin tam etkinleşmesi için birkaç dakika bekleyin"
    echo "   💡 Veya Cloud Build Console'dan manuel bir build başlatın:"
    echo "      https://console.cloud.google.com/cloud-build?project=$PROJECT_ID"
  fi
  cd - > /dev/null
  rm -rf "$TEST_BUILD_DIR"
  
  # Tekrar kontrol et
  if gcloud iam service-accounts describe $CB_SA --project=$PROJECT_ID &>/dev/null; then
    echo "   ✅ Cloud Build service account başarıyla oluşturuldu: $CB_SA"
  else
    echo "   ⚠️  Service account henüz oluşturulmadı, birkaç dakika bekleyin"
    echo "   💡 Veya Cloud Build Console'dan manuel bir build başlatın:"
    echo "      https://console.cloud.google.com/cloud-build?project=$PROJECT_ID"
  fi
fi

# 3. IAM rollerini kontrol et ve ata
echo ""
echo "🔍 IAM rolleri kontrol ediliyor..."
IAM_ROLES=$(gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$CB_SA" \
  --format="value(bindings.role)" 2>/dev/null || echo "")

REQUIRED_ROLES=(
  "roles/artifactregistry.writer"
  "roles/run.admin"
  "roles/iam.serviceAccountUser"
)

MISSING_ROLES=()
for role in "${REQUIRED_ROLES[@]}"; do
  if echo "$IAM_ROLES" | grep -q "$role"; then
    echo "   ✅ $role"
  else
    echo "   ❌ $role (eksik, atanıyor...)"
    gcloud projects add-iam-policy-binding $PROJECT_ID \
      --member="serviceAccount:$CB_SA" \
      --role="$role" \
      --condition=None || echo "   ⚠️  Rol atanamadı (service account henüz oluşturulmamış olabilir)"
    MISSING_ROLES+=("$role")
  fi
done

# 4. Service account'u listeleyerek kontrol et
echo ""
echo "🔍 Service accounts listesi kontrol ediliyor..."
ALL_SERVICE_ACCOUNTS=$(gcloud iam service-accounts list --project=$PROJECT_ID --format="value(email)")

if echo "$ALL_SERVICE_ACCOUNTS" | grep -q "@cloudbuild.gserviceaccount.com"; then
  echo "   ✅ Cloud Build service account listede görünüyor"
  echo "$ALL_SERVICE_ACCOUNTS" | grep "@cloudbuild.gserviceaccount.com" | while read sa; do
    echo "      - $sa"
  done
else
  echo "   ⚠️  Cloud Build service account listede görünmüyor"
  echo ""
  echo "   💡 Çözüm:"
  echo "   1. Cloud Build Console'dan manuel bir build başlatın:"
  echo "      https://console.cloud.google.com/cloud-build?project=$PROJECT_ID"
  echo "   2. Veya birkaç dakika daha bekleyin (API propagation için)"
  echo "   3. Service Accounts sayfasını yenileyin:"
  echo "      https://console.cloud.google.com/iam-admin/serviceaccounts?project=$PROJECT_ID"
fi

echo ""
echo "✅ Kontrol tamamlandı!"
echo ""
echo "📝 Sonraki Adımlar:"
echo "   1. Service Accounts sayfasını yenileyin:"
echo "      https://console.cloud.google.com/iam-admin/serviceaccounts?project=$PROJECT_ID"
echo "   2. Cloud Build Permissions sayfasına gidin:"
echo "      https://console.cloud.google.com/cloud-build/permissions?project=$PROJECT_ID"
echo "   3. Service account alanına şunu yazın (dropdown'da görünmese bile):"
echo "      $CB_SA"
echo "   4. 'OK' ve 'Save' butonlarına tıklayın"

