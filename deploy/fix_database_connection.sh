#!/bin/bash
# Database Bağlantı Sorunlarını Düzelt
# Cloud Shell'de çalıştırın: bash deploy/fix_database_connection.sh

set -euo pipefail

PROJECT_ID="finasis-478502"
INSTANCE_NAME="finasis-db"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
SERVICE_ACCOUNT="github-actions-deploy@finasis-478502.iam.gserviceaccount.com"

echo "=========================================="
echo "🔧 Database Bağlantı Sorunlarını Düzeltme"
echo "=========================================="
echo ""

# 1. Service Account'a Cloud SQL Client Rolü Ver
echo "1️⃣  Service Account'a Cloud SQL Client Rolü Veriliyor..."
if gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT AND bindings.role:roles/cloudsql.client" \
    --format="value(bindings.role)" 2>/dev/null | grep -q "cloudsql.client"; then
    echo "   ✅ Service account zaten Cloud SQL Client rolüne sahip"
else
    echo "   🔧 Cloud SQL Client rolü veriliyor..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/cloudsql.client" \
        --condition=None \
        --project=$PROJECT_ID
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Cloud SQL Client rolü başarıyla verildi"
    else
        echo "   ❌ Rol verme başarısız!"
        exit 1
    fi
fi
echo ""

# 2. Cloud Run Servisine Cloud SQL Instance Ekle
echo "2️⃣  Cloud Run Servisine Cloud SQL Instance Ekleniyor..."
EXPECTED_CONNECTION="$PROJECT_ID:$REGION:$INSTANCE_NAME"
CURRENT_INSTANCES=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(spec.template.spec.containers[0].cloudSqlInstances)" 2>/dev/null || echo "")

if echo "$CURRENT_INSTANCES" | grep -q "$EXPECTED_CONNECTION"; then
    echo "   ✅ Cloud SQL instance zaten Cloud Run'a eklenmiş"
else
    echo "   🔧 Cloud SQL instance ekleniyor: $EXPECTED_CONNECTION"
    gcloud run services update $SERVICE_NAME \
        --add-cloudsql-instances=$EXPECTED_CONNECTION \
        --region=$REGION \
        --project=$PROJECT_ID
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Cloud SQL instance başarıyla eklendi"
    else
        echo "   ❌ Cloud SQL instance ekleme başarısız!"
        exit 1
    fi
fi
echo ""

# 3. Doğrulama
echo "3️⃣  Değişiklikler Doğrulanıyor..."
echo ""

# Service account rolü kontrolü
HAS_ROLE=$(gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT AND bindings.role:roles/cloudsql.client" \
    --format="value(bindings.role)" 2>/dev/null || echo "")

if [ -n "$HAS_ROLE" ]; then
    echo "   ✅ Service account Cloud SQL Client rolüne sahip"
else
    echo "   ❌ Service account rolü hala yok!"
fi

# Cloud SQL instance kontrolü
UPDATED_INSTANCES=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(spec.template.spec.containers[0].cloudSqlInstances)" 2>/dev/null || echo "")

if echo "$UPDATED_INSTANCES" | grep -q "$EXPECTED_CONNECTION"; then
    echo "   ✅ Cloud SQL instance Cloud Run'a eklenmiş"
    echo "   📋 Bağlantı: $EXPECTED_CONNECTION"
else
    echo "   ❌ Cloud SQL instance hala eklenmemiş!"
fi
echo ""

# Özet
echo "=========================================="
if [ -n "$HAS_ROLE" ] && echo "$UPDATED_INSTANCES" | grep -q "$EXPECTED_CONNECTION"; then
    echo "✅ TÜM DÜZELTMELER BAŞARILI!"
    echo ""
    echo "📝 Sonraki adımlar:"
    echo "   1. Yeni bir deployment çalıştırın (GitHub Actions veya manuel)"
    echo "   2. Health endpoint'i test edin:"
    echo "      curl https://finasis-prod-s3kju7bqua-ew.a.run.app/health/"
    echo "   3. Database bağlantısının çalıştığını doğrulayın"
else
    echo "⚠️  BAZI DÜZELTMELER BAŞARISIZ"
    echo "   Yukarıdaki hataları kontrol edin"
fi
echo "=========================================="

