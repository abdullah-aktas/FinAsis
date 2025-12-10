#!/bin/bash
# Secret Manager'a secret'ları ekle
# Cloud Shell'de çalıştırın

set -euo pipefail

PROJECT_ID="finasis-478502"

echo "🔐 Secret Manager'a Secret'ları Ekleme"
echo "======================================"
echo ""

# 1. DJANGO_SECRET_KEY
echo "📋 1. DJANGO_SECRET_KEY ekleniyor..."
read -sp "DJANGO_SECRET_KEY değerini girin: " SECRET_KEY
echo ""

if [ -z "$SECRET_KEY" ]; then
  echo "❌ ERROR: DJANGO_SECRET_KEY boş olamaz!"
  exit 1
fi

# Secret oluştur veya güncelle
if gcloud secrets describe DJANGO_SECRET_KEY --project="$PROJECT_ID" >/dev/null 2>&1; then
  echo "   ⚠️  Secret zaten mevcut, yeni versiyon ekleniyor..."
  echo -n "$SECRET_KEY" | gcloud secrets versions add DJANGO_SECRET_KEY \
    --data-file=- \
    --project="$PROJECT_ID"
else
  echo "   📝 Yeni secret oluşturuluyor..."
  echo -n "$SECRET_KEY" | gcloud secrets create DJANGO_SECRET_KEY \
    --data-file=- \
    --replication-policy="automatic" \
    --project="$PROJECT_ID"
fi
echo "   ✅ DJANGO_SECRET_KEY eklendi"
echo ""

# 2. DJANGO_DB_PASSWORD
echo "📋 2. DJANGO_DB_PASSWORD ekleniyor..."
read -sp "DJANGO_DB_PASSWORD değerini girin: " DB_PASSWORD
echo ""

if [ -z "$DB_PASSWORD" ]; then
  echo "❌ ERROR: DJANGO_DB_PASSWORD boş olamaz!"
  exit 1
fi

# Secret oluştur veya güncelle
if gcloud secrets describe DJANGO_DB_PASSWORD --project="$PROJECT_ID" >/dev/null 2>&1; then
  echo "   ⚠️  Secret zaten mevcut, yeni versiyon ekleniyor..."
  echo -n "$DB_PASSWORD" | gcloud secrets versions add DJANGO_DB_PASSWORD \
    --data-file=- \
    --project="$PROJECT_ID"
else
  echo "   📝 Yeni secret oluşturuluyor..."
  echo -n "$DB_PASSWORD" | gcloud secrets create DJANGO_DB_PASSWORD \
    --data-file=- \
    --replication-policy="automatic" \
    --project="$PROJECT_ID"
fi
echo "   ✅ DJANGO_DB_PASSWORD eklendi"
echo ""

# 3. Service account'a erişim izni ver
echo "📋 3. Service account'a erişim izni veriliyor..."
SERVICE_ACCOUNT="github-actions-deploy@${PROJECT_ID}.iam.gserviceaccount.com"

for SECRET_NAME in DJANGO_SECRET_KEY DJANGO_DB_PASSWORD; do
  if gcloud secrets get-iam-policy "$SECRET_NAME" \
    --project="$PROJECT_ID" \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:${SERVICE_ACCOUNT}" \
    --format="value(bindings.members)" | grep -q "$SERVICE_ACCOUNT"; then
    echo "   ✅ $SECRET_NAME için izin mevcut"
  else
    echo "   ⚠️  $SECRET_NAME için izin ekleniyor..."
    gcloud secrets add-iam-policy-binding "$SECRET_NAME" \
      --member="serviceAccount:${SERVICE_ACCOUNT}" \
      --role="roles/secretmanager.secretAccessor" \
      --project="$PROJECT_ID"
    echo "   ✅ $SECRET_NAME için izin eklendi"
  fi
done
echo ""

echo "=========================================="
echo "✅ Tüm secret'lar eklendi!"
echo "=========================================="
echo ""
echo "💡 Şimdi secret'ları görebilirsiniz:"
echo "   gcloud secrets versions access latest --secret=DJANGO_SECRET_KEY --project=$PROJECT_ID"
echo "   gcloud secrets versions access latest --secret=DJANGO_DB_PASSWORD --project=$PROJECT_ID"
echo ""

