#!/bin/bash
# Cloud SQL bağlantı kontrolü scripti

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
INSTANCE_NAME="finasis-db"
SERVICE_NAME="finasis-prod"
CONNECTION_NAME="${PROJECT_ID}:${REGION}:${INSTANCE_NAME}"

echo "🔍 Cloud SQL Bağlantı Kontrolü"
echo "================================"
echo ""

# 1. Cloud SQL Instance durumunu kontrol et
echo "1️⃣  Cloud SQL Instance durumu:"
gcloud sql instances describe "$INSTANCE_NAME" \
  --project="$PROJECT_ID" \
  --format="table(name,state,settings.ipConfiguration.ipAddresses[0].ipAddress)" || {
  echo "❌ Cloud SQL instance bulunamadı veya erişilemiyor"
  exit 1
}

echo ""

# 2. Cloud Run servisinin Cloud SQL erişimini kontrol et
echo "2️⃣  Cloud Run servisinin Cloud SQL erişimi:"
gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format="value(spec.template.spec.containers[0].env)" | grep -i cloudsql || {
  echo "⚠️  Cloud SQL bağlantısı bulunamadı"
}

echo ""

# 3. Service Account'u kontrol et
echo "3️⃣  Service Account:"
SERVICE_ACCOUNT=$(gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format="value(spec.template.spec.serviceAccountName)")

echo "Service Account: $SERVICE_ACCOUNT"

# 4. Service Account'un Cloud SQL Client rolü var mı?
echo ""
echo "4️⃣  Service Account izinleri:"
gcloud projects get-iam-policy "$PROJECT_ID" \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT" \
  --format="table(bindings.role)" | grep -i sql || {
  echo "⚠️  Cloud SQL Client rolü bulunamadı"
  echo ""
  echo "💡 Çözüm: Service Account'a Cloud SQL Client rolü verin:"
  echo "   gcloud projects add-iam-policy-binding $PROJECT_ID \\"
  echo "     --member=serviceAccount:$SERVICE_ACCOUNT \\"
  echo "     --role=roles/cloudsql.client"
}

echo ""
echo "5️⃣  Environment Variables:"
gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format="value(spec.template.spec.containers[0].env)" | grep -E "(DB_|CLOUD_SQL)" || {
  echo "⚠️  Database environment variables bulunamadı"
}

echo ""
echo "✅ Kontrol tamamlandı"

