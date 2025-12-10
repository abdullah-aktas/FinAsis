#!/bin/bash
# Hızlı Database Bağlantı Kontrolü
# Cloud Shell'de çalıştırın: bash deploy/quick_check_database.sh

set -euo pipefail

PROJECT_ID="finasis-478502"
INSTANCE_NAME="finasis-db"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
DB_NAME="finasis"
DB_USER="finasis-app"

echo "=========================================="
echo "🔍 Database Bağlantı Kontrolü"
echo "=========================================="
echo ""

# 1. Cloud SQL Instance Durumu
echo "1️⃣  Cloud SQL Instance Durumu..."
INSTANCE_STATE=$(gcloud sql instances describe $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --format="value(state)" 2>/dev/null || echo "NOT_FOUND")

if [ "$INSTANCE_STATE" = "RUNNABLE" ]; then
    echo "   ✅ Instance çalışıyor: $INSTANCE_NAME"
    echo "   📊 Durum: $INSTANCE_STATE"
    
    # Instance detayları
    INSTANCE_INFO=$(gcloud sql instances describe $INSTANCE_NAME \
        --project=$PROJECT_ID \
        --format="value(databaseVersion,settings.tier,settings.availabilityType)" 2>/dev/null || echo "")
    if [ -n "$INSTANCE_INFO" ]; then
        echo "   📋 Versiyon: $(echo $INSTANCE_INFO | cut -d' ' -f1)"
        echo "   📋 Tier: $(echo $INSTANCE_INFO | cut -d' ' -f2)"
    fi
else
    echo "   ❌ Instance bulunamadı veya çalışmıyor!"
    echo "   📊 Durum: $INSTANCE_STATE"
    exit 1
fi
echo ""

# 2. Database Kontrolü
echo "2️⃣  Database Kontrolü..."
if gcloud sql databases list \
    --instance=$INSTANCE_NAME \
    --project=$PROJECT_ID \
    --format="value(name)" 2>/dev/null | grep -q "^${DB_NAME}$"; then
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
if gcloud sql users list \
    --instance=$INSTANCE_NAME \
    --project=$PROJECT_ID \
    --format="value(name)" 2>/dev/null | grep -q "^${DB_USER}$"; then
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
SERVICE_ACCOUNT="github-actions-deploy@finasis-478502.iam.gserviceaccount.com"
HAS_ROLE=$(gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT AND bindings.role:roles/cloudsql.client" \
    --format="value(bindings.role)" 2>/dev/null || echo "")

if [ -n "$HAS_ROLE" ]; then
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
EXPECTED_CONNECTION="$PROJECT_ID:$REGION:$INSTANCE_NAME"
CLOUD_SQL_INSTANCES=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(spec.template.spec.containers[0].cloudSqlInstances)" 2>/dev/null || echo "")

if echo "$CLOUD_SQL_INSTANCES" | grep -q "$EXPECTED_CONNECTION"; then
    echo "   ✅ Cloud SQL instance Cloud Run'a eklenmiş"
    echo "   📋 Bağlantı: $EXPECTED_CONNECTION"
else
    echo "   ❌ Cloud SQL instance Cloud Run'a eklenmemiş"
    echo "   💡 Eklemek için:"
    echo "      gcloud run services update $SERVICE_NAME \\"
    echo "        --add-cloudsql-instances=$EXPECTED_CONNECTION \\"
    echo "        --region=$REGION \\"
    echo "        --project=$PROJECT_ID"
    exit 1
fi
echo ""

# 6. Environment Variables Kontrolü
echo "6️⃣  Environment Variables Kontrolü..."
ENV_JSON=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="json" 2>/dev/null || echo "{}")

ENV_VARS=$(echo "$ENV_JSON" | jq -r '.spec.template.spec.containers[0].env[]? | "\(.name)=\(.value)"' 2>/dev/null || echo "")

ALL_OK=true

# DB Engine kontrolü
if echo "$ENV_VARS" | grep -q "DJANGO_DB_ENGINE=django.db.backends.postgresql"; then
    echo "   ✅ DJANGO_DB_ENGINE=postgresql"
else
    echo "   ❌ DJANGO_DB_ENGINE eksik veya yanlış"
    ALL_OK=false
fi

# DB Name kontrolü
if echo "$ENV_VARS" | grep -q "DJANGO_DB_NAME=$DB_NAME"; then
    echo "   ✅ DJANGO_DB_NAME=$DB_NAME"
else
    echo "   ❌ DJANGO_DB_NAME eksik veya yanlış (beklenen: $DB_NAME)"
    ALL_OK=false
fi

# DB User kontrolü
if echo "$ENV_VARS" | grep -q "DJANGO_DB_USER=$DB_USER"; then
    echo "   ✅ DJANGO_DB_USER=$DB_USER"
else
    echo "   ❌ DJANGO_DB_USER eksik veya yanlış (beklenen: $DB_USER)"
    ALL_OK=false
fi

# DB Host kontrolü
EXPECTED_HOST="/cloudsql/$EXPECTED_CONNECTION"
if echo "$ENV_VARS" | grep -q "DJANGO_DB_HOST=$EXPECTED_HOST"; then
    echo "   ✅ DJANGO_DB_HOST=$EXPECTED_HOST"
else
    echo "   ❌ DJANGO_DB_HOST eksik veya yanlış"
    echo "      Beklenen: $EXPECTED_HOST"
    ALL_OK=false
fi

# DB Password kontrolü
if echo "$ENV_VARS" | grep -q "DJANGO_DB_PASSWORD="; then
    echo "   ✅ DJANGO_DB_PASSWORD set edilmiş (değer gizli)"
else
    echo "   ❌ DJANGO_DB_PASSWORD eksik"
    echo "   💡 GitHub Secrets'te DJANGO_DB_PASSWORD olduğundan emin olun"
    ALL_OK=false
fi

if [ "$ALL_OK" = false ]; then
    echo ""
    echo "   ⚠️  Bazı environment variables eksik veya yanlış!"
    exit 1
fi
echo ""

# 7. Health Endpoint Testi (Gerçek Bağlantı Testi)
echo "7️⃣  Health Endpoint Testi (Gerçek Bağlantı Testi)..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="value(status.url)" 2>/dev/null || echo "")

if [ -z "$SERVICE_URL" ]; then
    echo "   ❌ Servis URL bulunamadı"
    exit 1
fi

echo "   🌐 Servis URL: $SERVICE_URL"
echo "   🔄 Health endpoint test ediliyor..."

HEALTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$SERVICE_URL/health/" 2>/dev/null || echo "")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | sed '/HTTP_CODE:/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ HTTP 200 OK"
    
    # JSON parse et
    if command -v jq &> /dev/null; then
        STATUS=$(echo "$HEALTH_BODY" | jq -r '.status' 2>/dev/null || echo "")
        DB_STATUS=$(echo "$HEALTH_BODY" | jq -r '.checks.database.status' 2>/dev/null || echo "")
        DB_TIME=$(echo "$HEALTH_BODY" | jq -r '.checks.database.response_time_ms' 2>/dev/null || echo "")
        
        if [ "$STATUS" = "healthy" ]; then
            echo "   ✅ Status: healthy"
        else
            echo "   ⚠️  Status: $STATUS"
        fi
        
        if [ "$DB_STATUS" = "ok" ]; then
            echo "   ✅ Database bağlantısı: OK (${DB_TIME}ms)"
        else
            echo "   ❌ Database bağlantısı: FAILED"
            echo "   📋 Yanıt: $HEALTH_BODY"
        fi
    else
        # jq yoksa basit grep
        if echo "$HEALTH_BODY" | grep -q '"status":"healthy"'; then
            echo "   ✅ Status: healthy"
        else
            echo "   ⚠️  Status: unhealthy veya bilinmeyen"
        fi
        
        if echo "$HEALTH_BODY" | grep -q '"database".*"status":"ok"'; then
            echo "   ✅ Database bağlantısı: OK"
        else
            echo "   ❌ Database bağlantısı: FAILED"
            echo "   📋 Yanıt: ${HEALTH_BODY:0:500}..."
        fi
    fi
elif [ "$HTTP_CODE" = "400" ]; then
    echo "   ⚠️  HTTP 400 Bad Request"
    echo "   💡 CSRF veya middleware sorunu olabilir"
    echo "   📋 Yanıt: ${HEALTH_BODY:0:200}..."
elif [ "$HTTP_CODE" = "503" ]; then
    echo "   ❌ HTTP 503 Service Unavailable"
    echo "   💡 Database bağlantısı başarısız"
    echo "   📋 Yanıt: ${HEALTH_BODY:0:200}..."
else
    echo "   ❌ HTTP $HTTP_CODE"
    echo "   📋 Yanıt: ${HEALTH_BODY:0:200}..."
fi
echo ""

# 8. Son Loglar (Database Hataları)
echo "8️⃣  Son Loglar (Database Hataları)..."
RECENT_LOGS=$(gcloud run services logs read $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --limit=20 \
    --format="value(textPayload)" 2>/dev/null || echo "")

DB_ERRORS=$(echo "$RECENT_LOGS" | grep -iE "(database|postgresql|connection|operationalerror|connection refused|timeout)" || echo "")

if [ -z "$DB_ERRORS" ]; then
    echo "   ✅ Son loglarda database hatası yok"
else
    echo "   ⚠️  Son loglarda database hataları bulundu:"
    echo "$DB_ERRORS" | head -5 | sed 's/^/      /'
fi
echo ""

# Özet
echo "=========================================="
if [ "$ALL_OK" = true ] && [ "$HTTP_CODE" = "200" ]; then
    echo "✅ TÜM KONTROLLER BAŞARILI!"
    echo "   Database bağlantısı sağlıklı çalışıyor."
else
    echo "⚠️  BAZI SORUNLAR TESPİT EDİLDİ"
    echo "   Yukarıdaki hataları düzeltin."
fi
echo "=========================================="

