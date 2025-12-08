#!/bin/bash
# Cloud SQL instance bilgilerini al ve Cloud Build trigger'ı güncelle
# Cloud Shell'de çalıştırın

PROJECT_ID="finasis-478502"
REGION="europe-west1"
TRIGGER_NAME="finasis-prod-europe-west1-abdullah-aktas-FinAsis"

echo "🔍 Cloud SQL Instance'ları Listeleniyor..."
echo "=========================================="
echo ""

# Cloud SQL instance'larını listele
gcloud sql instances list --project=$PROJECT_ID

echo ""
echo "📋 Yukarıdaki listeden Cloud SQL instance adını seçin"
echo "   (Örnek: finasis-prod-sql veya finasis-db)"
echo ""
read -p "Cloud SQL instance adı: " SQL_INSTANCE_NAME

if [ -z "$SQL_INSTANCE_NAME" ]; then
    echo "❌ Instance adı boş olamaz!"
    exit 1
fi

# Connection name oluştur
CONNECTION_NAME="${PROJECT_ID}:${REGION}:${SQL_INSTANCE_NAME}"

echo ""
echo "✅ Connection Name: $CONNECTION_NAME"
echo ""

# Cloud Build trigger'ı güncelle
echo "🔧 Cloud Build trigger güncelleniyor..."
echo ""

# Trigger'ı güncelle (substitution ekle)
gcloud builds triggers update $TRIGGER_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --substitutions="_CLOUD_SQL_CONNECTION=$CONNECTION_NAME" || {
    echo "⚠️  Trigger güncellenemedi, manuel olarak Cloud Console'dan güncelleyin:"
    echo "   https://console.cloud.google.com/cloud-build/triggers?project=$PROJECT_ID"
    echo ""
    echo "   Substitution ekleyin: _CLOUD_SQL_CONNECTION = $CONNECTION_NAME"
    exit 1
}

echo ""
echo "✅ Cloud Build trigger güncellendi!"
echo ""
echo "📝 Sonraki deployment'ta database environment variables otomatik olarak set edilecek."
echo ""

