#!/bin/bash
# Cloud Build Authentication Sorununu Çözme Scripti
# Compute service account'a Cloud Run izinleri verir

set -e

PROJECT_ID="${PROJECT_ID:-finasis-478502}"

echo "🔧 Cloud Build Authentication Sorununu Çözüyoruz..."
echo "=================================================="
echo ""

# Projeyi ayarla
gcloud config set project "$PROJECT_ID"

# Cloud Build API'sinin aktif olduğundan emin ol
echo "📋 Cloud Build API Kontrolü:"
gcloud services enable cloudbuild.googleapis.com --quiet
echo "✅ Cloud Build API aktif"
echo ""

# Compute service account'u bul
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)" 2>/dev/null)
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "📋 Compute Service Account: $COMPUTE_SA"
echo ""

# Gerekli rolleri ekle
echo "📋 Gerekli izinler ekleniyor..."
ROLES=(
    "roles/run.admin"
    "roles/iam.serviceAccountUser"
    "roles/artifactregistry.writer"
)

for ROLE in "${ROLES[@]}"; do
    echo "   $ROLE kontrol ediliyor..."
    # İzin zaten varsa hata vermesin
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$COMPUTE_SA" \
        --role="$ROLE" \
        --condition=None \
        --quiet 2>/dev/null && echo "   ✅ $ROLE eklendi" || echo "   ℹ️  $ROLE zaten mevcut"
done
echo ""

# Cloud Build service account'u da kontrol et
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
echo "📋 Cloud Build Service Account: $CLOUD_BUILD_SA"

for ROLE in "${ROLES[@]}"; do
    echo "   Cloud Build SA için $ROLE kontrol ediliyor..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$CLOUD_BUILD_SA" \
        --role="$ROLE" \
        --condition=None \
        --quiet 2>/dev/null && echo "   ✅ $ROLE eklendi" || echo "   ℹ️  $ROLE zaten mevcut"
done
echo ""

echo "✅ İzinler kontrol edildi!"
echo ""
echo "🔧 Şimdi deployment yapmayı deneyin:"
echo "   gcloud builds submit \\"
echo "     --config=deploy/cloud_run/cloudbuild.yaml \\"
echo "     --region=europe-west1 \\"
echo "     --substitutions=_SERVICE=finasis-prod"
echo ""
