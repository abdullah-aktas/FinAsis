#!/bin/bash
# Cloud Run service account izinlerini düzelt
# Cloud Shell'de çalıştırın: bash deploy/fix_service_account_permissions.sh

set -euo pipefail

PROJECT_ID="finasis-478502"
SA_EMAIL="github-actions-deploy@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🔧 Service account izinleri düzeltiliyor..."
echo "Service Account: $SA_EMAIL"
echo ""

# Service account'un kendi kendini kullanabilmesi için izin ver
echo "📋 Service account'a kendi kendini kullanma izni veriliyor..."
gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser" \
  --project="$PROJECT_ID" || {
  echo "⚠️  İzin zaten mevcut olabilir, devam ediliyor..."
}

echo ""
echo "✅ İzinler güncellendi!"
echo ""
echo "📊 Kontrol için:"
echo "   gcloud iam service-accounts get-iam-policy $SA_EMAIL --project=$PROJECT_ID"

