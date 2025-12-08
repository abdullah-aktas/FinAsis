#!/bin/bash
# Cloud Build trigger'ına Cloud SQL connection ekle
# Cloud Shell'de çalıştırın

PROJECT_ID="finasis-478502"
REGION="europe-west1"
TRIGGER_NAME="finasis-prod-europe-west1-abdullah-aktas-FinAsis"
SQL_INSTANCE="finasis-db"
CONNECTION_NAME="${PROJECT_ID}:${REGION}:${SQL_INSTANCE}"

echo "🔧 Cloud Build Trigger Güncelleniyor"
echo "====================================="
echo ""
echo "📋 Bilgiler:"
echo "   Trigger: $TRIGGER_NAME"
echo "   Cloud SQL Instance: $SQL_INSTANCE"
echo "   Connection Name: $CONNECTION_NAME"
echo ""

# Trigger'ı güncelle
echo "🔄 Trigger güncelleniyor..."
gcloud builds triggers update $TRIGGER_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --update-substitutions="_CLOUD_SQL_CONNECTION=$CONNECTION_NAME" || {
    echo ""
    echo "⚠️  Otomatik güncelleme başarısız!"
    echo ""
    echo "📝 Manuel olarak Cloud Console'dan güncelleyin:"
    echo "   1. https://console.cloud.google.com/cloud-build/triggers?project=$PROJECT_ID"
    echo "   2. '$TRIGGER_NAME' trigger'ını seçin"
    echo "   3. 'Edit' butonuna tıklayın"
    echo "   4. 'Substitution variables' bölümüne gidin"
    echo "   5. Yeni variable ekleyin:"
    echo "      - Name: _CLOUD_SQL_CONNECTION"
    echo "      - Value: $CONNECTION_NAME"
    echo "   6. 'Save' butonuna tıklayın"
    exit 1
}

echo ""
echo "✅ Trigger başarıyla güncellendi!"
echo ""
echo "📝 Sonraki deployment'ta:"
echo "   ✅ PostgreSQL database kullanılacak"
echo "   ✅ Cloud SQL connection otomatik bağlanacak"
echo "   ✅ Database environment variables set edilecek"
echo ""

