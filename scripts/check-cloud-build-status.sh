#!/bin/bash
# Cloud Build durum kontrolü scripti

set -e

PROJECT_ID="finasis-478502"

echo "🔍 Cloud Build durumu kontrol ediliyor..."

# Proje ID'sini ayarla
gcloud config set project $PROJECT_ID

# Cloud Build API durumunu kontrol et
echo "📡 Cloud Build API durumu:"
gcloud services list --enabled --filter="name:cloudbuild.googleapis.com" --project=$PROJECT_ID || echo "❌ Cloud Build API etkin değil"

# Cloud Build servisini kontrol et
echo ""
echo "🔧 Cloud Build servisi kontrol ediliyor..."
gcloud builds list --limit=1 --project=$PROJECT_ID 2>&1 || echo "⚠️  Cloud Build servisine erişilemiyor"

# Cloud Storage bucket kontrolü
echo ""
echo "🪣 Cloud Build storage bucket:"
BUCKET_NAME="${PROJECT_ID}_cloudbuild"
gsutil ls -b gs://$BUCKET_NAME 2>&1 || echo "⚠️  Bucket bulunamadı"

echo ""
echo "✅ Kontrol tamamlandı!"

