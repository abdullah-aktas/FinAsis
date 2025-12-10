#!/bin/bash
# Cloud SQL Bağlantı Kontrol Scripti
# Tüm database bağlantı ayarlarını kontrol eder

set -euo pipefail

PROJECT_ID="finasis-478502"
INSTANCE_NAME="finasis-db"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
SERVICE_ACCOUNT="github-actions-deploy@finasis-478502.iam.gserviceaccount.com"
DB_NAME="finasis"
DB_USER="finasis-app"

echo "=========================================="
echo "🔍 Cloud SQL Bağlantı Kontrolü"
echo "=========================================="
echo ""

# 1. Cloud SQL Instance Kontrolü
echo "1️⃣  Cloud SQL Instance Kontrolü..."
if gcloud sql instances describe $INSTANCE_NAME --project=$PROJECT_ID --format="value(state)" 2>/dev/null | grep -q "RUNNABLE"; then
    echo "   ✅ Instance çalışıyor: $INSTANCE_NAME"
    INSTANCE_STATE=$(gcloud sql instances describe $INSTANCE_NAME --project=$PROJECT_ID --format="value(state)")
    echo "   📊 Durum: $INSTANCE_STATE"
else
    echo "   ❌ Instance bulunamadı veya çalışmıyor: $INSTANCE_NAME"
    exit 1
fi
echo ""

# 2. Database Kontrolü
echo "2️⃣  Database Kontrolü..."
if gcloud sql databases list --instance=$INSTANCE_NAME --project=$PROJECT_ID 2>/dev/null | grep -q "$DB_NAME"; then
    echo "   ✅ Database mevcut: $DB_NAME"
else
    echo "   ❌ Database bulunamadı: $DB_NAME"
    echo "   💡 Oluşturmak için:"
    echo "      gcloud sql databases create $DB_NAME --instance=$INSTANCE_NAME --project=$PROJECT_ID"
    exit 1
fi
echo ""

# 3. User Kontrolü
echo "3️⃣  User Kontrolü..."
if gcloud sql users list --instance=$INSTANCE_NAME --project=$PROJECT_ID 2>/dev/null | grep -q "$DB_USER"; then
    echo "   ✅ User mevcut: $DB_USER"
else
    echo "   ❌ User bulunamadı: $DB_USER"
    echo "   💡 Oluşturmak için:"
    echo "      gcloud sql users create $DB_USER --instance=$INSTANCE_NAME --password='GÜÇLÜ_ŞİFRE' --project=$PROJECT_ID"
    exit 1
fi
echo ""

# 4. Service Account İzinleri
echo "4️⃣  Service Account İzinleri..."
if gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT" \
    --format="value(bindings.role)" 2>/dev/null | grep -q "cloudsql.client"; then
    echo "   ✅ Service account Cloud SQL Client rolüne sahip"
else
    echo "   ❌ Service account Cloud SQL Client rolüne sahip değil"
    echo "   💡 Rol vermek için:"
    echo "      gcloud projects add-iam-policy-binding $PROJECT_ID \\"
    echo "        --member=\"serviceAccount:$SERVICE_ACCOUNT\" \\"
    echo "        --role=\"roles/cloudsql.client\""
    exit 1
fi
echo ""

# 5. Cloud Run Cloud SQL Bağlantısı
echo "5️⃣  Cloud Run Cloud SQL Bağlantısı..."
CLOUD_SQL_INSTANCES=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(spec.template.spec.containers[0].cloudSqlInstances)" 2>/dev/null || echo "")

if echo "$CLOUD_SQL_INSTANCES" | grep -q "$PROJECT_ID:$REGION:$INSTANCE_NAME"; then
    echo "   ✅ Cloud SQL instance Cloud Run'a eklenmiş"
    echo "   📋 Bağlantı: $PROJECT_ID:$REGION:$INSTANCE_NAME"
else
    echo "   ❌ Cloud SQL instance Cloud Run'a eklenmemiş"
    echo "   💡 Eklemek için:"
    echo "      gcloud run services update $SERVICE_NAME \\"
    echo "        --add-cloudsql-instances=$PROJECT_ID:$REGION:$INSTANCE_NAME \\"
    echo "        --region=$REGION \\"
    echo "        --project=$PROJECT_ID"
    exit 1
fi
echo ""

# 6. Environment Variables Kontrolü
echo "6️⃣  Environment Variables Kontrolü..."
ENV_VARS=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="json" 2>/dev/null | jq -r '.spec.template.spec.containers[0].env[]? | "\(.name)=\(.value)"' || echo "")

MISSING_VARS=()

if echo "$ENV_VARS" | grep -q "DJANGO_DB_ENGINE=django.db.backends.postgresql"; then
    echo "   ✅ DJANGO_DB_ENGINE set edilmiş"
else
    echo "   ❌ DJANGO_DB_ENGINE set edilmemiş"
    MISSING_VARS+=("DJANGO_DB_ENGINE=django.db.backends.postgresql")
fi

if echo "$ENV_VARS" | grep -q "DJANGO_DB_NAME=$DB_NAME"; then
    echo "   ✅ DJANGO_DB_NAME set edilmiş"
else
    echo "   ❌ DJANGO_DB_NAME set edilmemiş"
    MISSING_VARS+=("DJANGO_DB_NAME=$DB_NAME")
fi

if echo "$ENV_VARS" | grep -q "DJANGO_DB_USER=$DB_USER"; then
    echo "   ✅ DJANGO_DB_USER set edilmiş"
else
    echo "   ❌ DJANGO_DB_USER set edilmemiş"
    MISSING_VARS+=("DJANGO_DB_USER=$DB_USER")
fi

EXPECTED_HOST="/cloudsql/$PROJECT_ID:$REGION:$INSTANCE_NAME"
if echo "$ENV_VARS" | grep -q "DJANGO_DB_HOST=$EXPECTED_HOST"; then
    echo "   ✅ DJANGO_DB_HOST set edilmiş"
else
    echo "   ❌ DJANGO_DB_HOST set edilmemiş veya yanlış"
    echo "      Beklenen: $EXPECTED_HOST"
    MISSING_VARS+=("DJANGO_DB_HOST=$EXPECTED_HOST")
fi

if echo "$ENV_VARS" | grep -q "DJANGO_DB_PASSWORD="; then
    echo "   ✅ DJANGO_DB_PASSWORD set edilmiş (değer gizli)"
else
    echo "   ❌ DJANGO_DB_PASSWORD set edilmemiş"
    echo "   💡 GitHub Secrets'te DJANGO_DB_PASSWORD olduğundan emin olun"
fi

if echo "$ENV_VARS" | grep -q "CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:$INSTANCE_NAME"; then
    echo "   ✅ CLOUD_SQL_CONNECTION_NAME set edilmiş"
else
    echo "   ⚠️  CLOUD_SQL_CONNECTION_NAME set edilmemiş (opsiyonel)"
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo ""
    echo "   💡 Eksik environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "      - $var"
    done
    exit 1
fi
echo ""

# 7. Health Endpoint Testi
echo "7️⃣  Health Endpoint Testi..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo "   🌐 Servis URL: $SERVICE_URL"
    HEALTH_RESPONSE=$(curl -s "$SERVICE_URL/health/" 2>/dev/null || echo "")
    
    if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
        echo "   ✅ Health endpoint başarılı (healthy)"
        if echo "$HEALTH_RESPONSE" | grep -q '"database".*"status":"ok"'; then
            echo "   ✅ Database bağlantısı başarılı"
        else
            echo "   ⚠️  Database bağlantısı başarısız (health endpoint'te)"
        fi
    elif echo "$HEALTH_RESPONSE" | grep -q '"status":"unhealthy"'; then
        echo "   ❌ Health endpoint unhealthy"
        echo "   📋 Yanıt: $HEALTH_RESPONSE"
    else
        echo "   ⚠️  Health endpoint yanıt vermiyor veya beklenmeyen format"
        echo "   📋 Yanıt: ${HEALTH_RESPONSE:0:200}..."
    fi
else
    echo "   ⚠️  Servis URL bulunamadı"
fi
echo ""

# Özet
echo "=========================================="
echo "✅ Tüm kontroller tamamlandı!"
echo "=========================================="
echo ""
echo "📝 Sonraki adımlar:"
echo "   1. Eğer eksikler varsa yukarıdaki komutları çalıştırın"
echo "   2. GitHub Secrets'te DJANGO_DB_PASSWORD olduğundan emin olun"
echo "   3. Deployment'ı tekrar çalıştırın"
echo ""

