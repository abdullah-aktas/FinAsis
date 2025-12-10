#!/bin/bash
# Cloud Shell'de direkt çalıştırılabilir - git pull gerektirmez
# Kullanım: bash deploy/quick_check_secrets.sh

set -euo pipefail

PROJECT_ID="finasis-478502"

echo "🔍 Secret Manager kontrolü..."
echo "Proje: $PROJECT_ID"
echo ""

# Gerekli secret'lar
REQUIRED_SECRETS=(
  "DJANGO_SECRET_KEY"
  "DJANGO_DB_PASSWORD"
)

MISSING_SECRETS=()

for SECRET_NAME in "${REQUIRED_SECRETS[@]}"; do
  echo "📋 Kontrol ediliyor: $SECRET_NAME"
  
  if gcloud secrets describe "$SECRET_NAME" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "   ✅ $SECRET_NAME mevcut"
  else
    echo "   ❌ $SECRET_NAME bulunamadı!"
    MISSING_SECRETS+=("$SECRET_NAME")
    echo ""
    echo "   🔧 Oluşturmak için:"
    echo "   echo 'your-secret-value' | gcloud secrets create $SECRET_NAME --data-file=- --project=$PROJECT_ID"
    echo "   echo 'your-secret-value' | gcloud secrets versions add $SECRET_NAME --data-file=- --project=$PROJECT_ID"
    echo ""
  fi
done

echo ""
echo "📊 Özet:"
if [ ${#MISSING_SECRETS[@]} -eq 0 ]; then
  echo "✅ Tüm secret'lar mevcut!"
else
  echo "⚠️  Eksik secret'lar: ${MISSING_SECRETS[*]}"
  echo ""
  echo "💡 Not: GitHub Secrets kullanıyorsanız, Secret Manager'da olmasına gerek yok."
  echo "   GitHub Actions workflow'u GitHub Secrets'tan alacak."
fi

echo ""
echo "📊 Tüm secret'ları listelemek için:"
echo "   gcloud secrets list --project=$PROJECT_ID"
echo ""
echo "💡 Secret değerini görmek için (dikkatli kullanın!):"
echo "   gcloud secrets versions access latest --secret=SECRET_NAME --project=$PROJECT_ID"

