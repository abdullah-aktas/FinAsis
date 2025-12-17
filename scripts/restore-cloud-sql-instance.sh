#!/bin/bash
# SUSPENDED Cloud SQL instance'ı restore etme scripti

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
INSTANCE_NAME="finasis-db"

echo "🔧 Cloud SQL Instance Restore İşlemi"
echo "====================================="
echo ""

# Instance detaylarını al
echo "📊 Instance detayları:"
gcloud sql instances describe "$INSTANCE_NAME" \
  --project="$PROJECT_ID" \
  --format="yaml(name,state,settings.tier,settings.availabilityType,settings.backupConfiguration)"

echo ""

# SUSPENDED instance'ları restore etmek için önce backup'ları kontrol et
echo "💾 Mevcut backup'lar:"
gcloud sql backups list \
  --instance="$INSTANCE_NAME" \
  --project="$PROJECT_ID" \
  --limit=5 \
  --format="table(id,windowStartTime,status,type)" || {
  echo "⚠️  Backup bulunamadı veya instance'a erişilemiyor"
}

echo ""

# Billing hesabını kontrol et
echo "💳 Billing hesabı durumu:"
BILLING_ACCOUNT=$(gcloud billing projects describe "$PROJECT_ID" \
  --format="value(billingAccountName)" 2>/dev/null || echo "NOT_FOUND")

if [ "$BILLING_ACCOUNT" = "NOT_FOUND" ] || [ -z "$BILLING_ACCOUNT" ]; then
  echo "❌ Billing hesabı bulunamadı veya aktif değil!"
  echo "💡 Çözüm: Google Cloud Console → Billing → Projects → finasis-478502"
  echo "   Billing hesabını aktif hale getirin"
  exit 1
else
  echo "✅ Billing hesabı: $BILLING_ACCOUNT"
fi

echo ""
echo "⚠️  SUSPENDED instance'ı aktifleştirmek için:"
echo ""
echo "1️⃣  YÖNTEM 1: Google Cloud Console (Önerilen)"
echo "   - https://console.cloud.google.com/sql/instances?project=$PROJECT_ID"
echo "   - finasis-db instance'ını seçin"
echo "   - 'ACTIVATE' veya 'RESTORE' butonuna tıklayın"
echo ""
echo "2️⃣  YÖNTEM 2: Instance'ı silip yeniden oluştur (VERİ KAYBI RİSKİ)"
echo "   ⚠️  DİKKAT: Bu yöntem veri kaybına neden olabilir!"
echo "   - Önce backup alın: gcloud sql backups create --instance=$INSTANCE_NAME"
echo "   - Instance'ı silin ve yeniden oluşturun"
echo ""
echo "3️⃣  YÖNTEM 3: Support ile iletişime geçin"
echo "   - Google Cloud Support'a başvurun"
echo "   - Instance'ın neden SUSPENDED olduğunu sorun"
echo ""
echo "📋 Mevcut durum:"
gcloud sql instances describe "$INSTANCE_NAME" \
  --project="$PROJECT_ID" \
  --format="table(name,state,settings.tier,settings.availabilityType)"

