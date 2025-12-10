#!/bin/bash
# Cloud Build API ve izinlerini düzelt
# Cloud Shell'de çalıştırın

set -euo pipefail

PROJECT_ID="finasis-478502"

echo "🔧 Cloud Build API ve İzinlerini Düzeltme"
echo "=========================================="
echo ""

# 1. Proje ayarı
echo "📋 1. Proje ayarlanıyor..."
gcloud config set project "$PROJECT_ID"
echo "✅ Proje: $PROJECT_ID"
echo ""

# 2. Gerekli API'leri etkinleştir
echo "📋 2. Gerekli API'ler etkinleştiriliyor..."
gcloud services enable cloudbuild.googleapis.com --project="$PROJECT_ID"
gcloud services enable run.googleapis.com --project="$PROJECT_ID"
gcloud services enable artifactregistry.googleapis.com --project="$PROJECT_ID"
gcloud services enable sqladmin.googleapis.com --project="$PROJECT_ID"
echo "✅ API'ler etkinleştirildi"
echo ""

# 3. Artifact Registry repository kontrolü
echo "📋 3. Artifact Registry repository kontrolü..."
REGION="europe-west1"
REPOSITORY="finasis-app"

if gcloud artifacts repositories describe "$REPOSITORY" \
  --location="$REGION" \
  --project="$PROJECT_ID" >/dev/null 2>&1; then
  echo "✅ Repository mevcut: $REPOSITORY"
else
  echo "⚠️  Repository bulunamadı, oluşturuluyor..."
  gcloud artifacts repositories create "$REPOSITORY" \
    --repository-format=docker \
    --location="$REGION" \
    --description="FinAsis Cloud Run images" \
    --project="$PROJECT_ID"
  echo "✅ Repository oluşturuldu: $REPOSITORY"
fi
echo ""

# 4. Service account izinleri kontrolü
echo "📋 4. Service account izinleri kontrol ediliyor..."
SERVICE_ACCOUNT="github-actions-deploy@${PROJECT_ID}.iam.gserviceaccount.com"

# Gerekli roller
ROLES=(
  "roles/cloudbuild.builds.editor"
  "roles/run.admin"
  "roles/storage.admin"
  "roles/artifactregistry.writer"
  "roles/iam.serviceAccountUser"
)

for ROLE in "${ROLES[@]}"; do
  if gcloud projects get-iam-policy "$PROJECT_ID" \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:${SERVICE_ACCOUNT} AND bindings.role:${ROLE}" \
    --format="value(bindings.role)" | grep -q "$ROLE"; then
    echo "   ✅ $ROLE mevcut"
  else
    echo "   ⚠️  $ROLE eksik, ekleniyor..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
      --member="serviceAccount:${SERVICE_ACCOUNT}" \
      --role="$ROLE" \
      --condition=None
    echo "   ✅ $ROLE eklendi"
  fi
done
echo ""

# 5. Cloud Build service account izinleri
echo "📋 5. Cloud Build service account izinleri..."
CLOUD_BUILD_SA="${PROJECT_ID}@cloudbuild.gserviceaccount.com"

CLOUD_BUILD_ROLES=(
  "roles/run.admin"
  "roles/iam.serviceAccountUser"
)

for ROLE in "${CLOUD_BUILD_ROLES[@]}"; do
  if gcloud projects get-iam-policy "$PROJECT_ID" \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:${CLOUD_BUILD_SA} AND bindings.role:${ROLE}" \
    --format="value(bindings.role)" | grep -q "$ROLE"; then
    echo "   ✅ Cloud Build SA: $ROLE mevcut"
  else
    echo "   ⚠️  Cloud Build SA: $ROLE eksik, ekleniyor..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
      --member="serviceAccount:${CLOUD_BUILD_SA}" \
      --role="$ROLE" \
      --condition=None
    echo "   ✅ Cloud Build SA: $ROLE eklendi"
  fi
done
echo ""

# 6. Docker authentication
echo "📋 6. Docker authentication yapılandırılıyor..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
echo "✅ Docker authentication yapılandırıldı"
echo ""

# 7. Test build (opsiyonel)
echo "=========================================="
echo "✅ Tüm kontroller tamamlandı!"
echo "=========================================="
echo ""
echo "💡 Şimdi deployment yapabilirsiniz:"
echo "   bash deploy/manual_deploy_cloud_shell.sh"
echo ""

