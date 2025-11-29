#!/bin/bash
# Cloud Shell'de Git Sorununu Çöz ve Bağlantıyı Kontrol Et
# Bu script Cloud Shell'de çalıştırılmalıdır

set -e

echo "🔧 Cloud Shell Git Sorununu Çözüyoruz..."
echo "========================================"
echo ""

# 1. users_export.json dosyasını stash et (gitignore'da olduğu için)
echo "📋 1. users_export.json dosyasını stash ediyoruz..."
if [ -f "users_export.json" ]; then
    git stash push -m "Stash users_export.json before pull" users_export.json 2>/dev/null || {
        echo "⚠️  Stash başarısız, dosyayı yedekliyoruz..."
        cp users_export.json users_export.json.backup 2>/dev/null || true
        git checkout -- users_export.json 2>/dev/null || rm -f users_export.json
    }
    echo "✅ users_export.json stash edildi"
else
    echo "ℹ️  users_export.json dosyası bulunamadı"
fi
echo ""

# 2. Git pull yap
echo "📋 2. Git pull yapılıyor..."
git pull origin main
echo "✅ Git pull tamamlandı"
echo ""

# 3. Scriptleri kontrol et ve oluştur
echo "📋 3. Kontrol scriptlerini hazırlıyoruz..."
echo "-------------------"

# check_cloud_shell_connection.sh kontrolü
if [ ! -f "deploy/check_cloud_shell_connection.sh" ]; then
    echo "⚠️  check_cloud_shell_connection.sh bulunamadı, oluşturuluyor..."
    mkdir -p deploy
    cat > deploy/check_cloud_shell_connection.sh << 'SCRIPT_EOF'
#!/bin/bash
# Cloud Shell Bağlantı ve Deployment Durumu Kontrol Scripti
# Bu script Cloud Shell'de çalıştırılmalıdır

set -e

PROJECT_ID="${PROJECT_ID:-finasis-478502}"
REGION="${REGION:-europe-west1}"
SERVICE_NAME="${SERVICE_NAME:-finasis-prod}"
REPOSITORY="${REPOSITORY:-finasis-app}"

echo "🔍 Cloud Shell Bağlantı ve Deployment Durumu Kontrolü"
echo "=================================================="
echo ""

# 1. Proje Kontrolü
echo "📋 1. Proje Kontrolü"
echo "-------------------"
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$CURRENT_PROJECT" ]; then
    echo "❌ GCP projesi ayarlanmamış!"
    echo "   Şu komutu çalıştırın: gcloud config set project $PROJECT_ID"
    exit 1
fi

if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo "⚠️  Mevcut proje: $CURRENT_PROJECT"
    echo "   Beklenen proje: $PROJECT_ID"
    read -p "   Projeyi değiştirmek ister misiniz? (y/N): " CHANGE_PROJECT
    if [ "$CHANGE_PROJECT" = "y" ] || [ "$CHANGE_PROJECT" = "Y" ]; then
        gcloud config set project "$PROJECT_ID"
        echo "✅ Proje $PROJECT_ID olarak ayarlandı"
    fi
else
    echo "✅ Proje doğru: $CURRENT_PROJECT"
fi
echo ""

# 2. Gerekli API'lerin Aktif Olup Olmadığını Kontrol Et
echo "📋 2. Gerekli API'lerin Kontrolü"
echo "-------------------"
APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "artifactregistry.googleapis.com"
    "sqladmin.googleapis.com"
)

for API in "${APIS[@]}"; do
    if gcloud services list --enabled --filter="name:$API" --format="value(name)" | grep -q "$API"; then
        echo "✅ $API aktif"
    else
        echo "⚠️  $API aktif değil, etkinleştiriliyor..."
        gcloud services enable "$API" --quiet || echo "❌ $API etkinleştirilemedi"
    fi
done
echo ""

# 3. Cloud Run Servis Durumu
echo "📋 3. Cloud Run Servis Durumu"
echo "-------------------"
if gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" &>/dev/null; then
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="value(status.url)")
    echo "✅ Servis mevcut: $SERVICE_NAME"
    echo "   URL: $SERVICE_URL"
    
    # Son revision bilgisi
    LATEST_REVISION=$(gcloud run revisions list \
        --service="$SERVICE_NAME" \
        --region="$REGION" \
        --limit=1 \
        --format="value(metadata.name)" 2>/dev/null || echo "")
    
    if [ -n "$LATEST_REVISION" ]; then
        REVISION_IMAGE=$(gcloud run revisions describe "$LATEST_REVISION" \
            --region="$REGION" \
            --format="value(spec.containers[0].image)" 2>/dev/null || echo "")
        REVISION_CREATED=$(gcloud run revisions describe "$LATEST_REVISION" \
            --region="$REGION" \
            --format="value(metadata.creationTimestamp)" 2>/dev/null || echo "")
        echo "   Son Revision: $LATEST_REVISION"
        echo "   Image: $REVISION_IMAGE"
        echo "   Oluşturulma: $REVISION_CREATED"
    fi
else
    echo "❌ Servis bulunamadı: $SERVICE_NAME"
    echo "   Servis henüz oluşturulmamış olabilir."
fi
echo ""

# 4. Artifact Registry Kontrolü
echo "📋 4. Artifact Registry Kontrolü"
echo "-------------------"
if gcloud artifacts repositories describe "$REPOSITORY" --location="$REGION" &>/dev/null; then
    echo "✅ Repository mevcut: $REPOSITORY"
    
    # Son image'ları listele
    echo "   Son image'lar:"
    gcloud artifacts docker images list \
        "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}" \
        --limit=3 \
        --format="table(package,version,create_time)" 2>/dev/null || echo "   Image bulunamadı"
else
    echo "⚠️  Repository bulunamadı: $REPOSITORY"
fi
echo ""

# 5. Cloud Build Son Durumlar
echo "📋 5. Son Cloud Build Durumları"
echo "-------------------"
echo "   Son 5 build:"
gcloud builds list \
    --limit=5 \
    --format="table(id,status,createTime,logUrl)" \
    --sort-by=~createTime 2>/dev/null || echo "   Build bulunamadı"
echo ""

# 6. Cloud SQL Bağlantı Kontrolü
echo "📋 6. Cloud SQL Bağlantı Kontrolü"
echo "-------------------"
SQL_INSTANCES=$(gcloud sql instances list --format="value(name)" 2>/dev/null || echo "")
if [ -n "$SQL_INSTANCES" ]; then
    echo "✅ Cloud SQL instance'ları:"
    echo "$SQL_INSTANCES" | while read -r instance; do
        if [ -n "$instance" ]; then
            CONNECTION_NAME=$(gcloud sql instances describe "$instance" \
                --format="value(connectionName)" 2>/dev/null || echo "")
            echo "   - $instance"
            echo "     Connection: $CONNECTION_NAME"
        fi
    done
else
    echo "⚠️  Cloud SQL instance bulunamadı"
fi
echo ""

# 7. Health Check
echo "📋 7. Health Check"
echo "-------------------"
if [ -n "$SERVICE_URL" ]; then
    echo "   Servis URL'sine istek gönderiliyor..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" || echo "000")
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
        echo "✅ Servis yanıt veriyor (HTTP $HTTP_CODE)"
    else
        echo "⚠️  Servis yanıt vermiyor (HTTP $HTTP_CODE)"
    fi
else
    echo "⚠️  Servis URL'si bulunamadı, health check yapılamadı"
fi
echo ""

# 8. Özet ve Öneriler
echo "📋 8. Özet ve Öneriler"
echo "-------------------"
echo ""
echo "✅ Kontrol tamamlandı!"
echo ""
echo "🔧 Deployment yapmak için:"
echo "   gcloud builds submit \\"
echo "     --config=deploy/cloud_run/cloudbuild.yaml \\"
echo "     --region=$REGION \\"
echo "     --substitutions=_SERVICE=$SERVICE_NAME"
echo ""
echo "📊 Logları görüntülemek için:"
echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=50"
echo ""
echo "🔄 Servis bilgilerini görmek için:"
echo "   gcloud run services describe $SERVICE_NAME --region=$REGION"
echo ""
SCRIPT_EOF
    chmod +x deploy/check_cloud_shell_connection.sh
    echo "✅ check_cloud_shell_connection.sh oluşturuldu"
else
    echo "✅ check_cloud_shell_connection.sh mevcut"
    chmod +x deploy/check_cloud_shell_connection.sh
fi

# test_deployment.sh kontrolü
if [ ! -f "deploy/test_deployment.sh" ]; then
    echo "⚠️  test_deployment.sh bulunamadı, oluşturuluyor..."
    cat > deploy/test_deployment.sh << 'TEST_EOF'
#!/bin/bash
# Deployment Test ve Doğrulama Scripti
# Bu script deployment'ın başarılı olup olmadığını kontrol eder

set -e

PROJECT_ID="${PROJECT_ID:-finasis-478502}"
REGION="${REGION:-europe-west1}"
SERVICE_NAME="${SERVICE_NAME:-finasis-prod}"

echo "🧪 Deployment Test ve Doğrulama"
echo "================================"
echo ""

# 1. Servis URL'sini al
echo "📋 1. Servis URL'sini Alıyorum..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" 2>/dev/null || echo "")

if [ -z "$SERVICE_URL" ]; then
    echo "❌ Servis bulunamadı: $SERVICE_NAME"
    exit 1
fi

echo "✅ Servis URL: $SERVICE_URL"
echo ""

# 2. Son revision'ı kontrol et
echo "📋 2. Son Revision Bilgileri"
echo "-------------------"
LATEST_REVISION=$(gcloud run revisions list \
    --service="$SERVICE_NAME" \
    --region="$REGION" \
    --limit=1 \
    --sort-by=~metadata.creationTimestamp \
    --format="value(metadata.name)" 2>/dev/null || echo "")

if [ -n "$LATEST_REVISION" ]; then
    echo "✅ Son Revision: $LATEST_REVISION"
    
    REVISION_IMAGE=$(gcloud run revisions describe "$LATEST_REVISION" \
        --region="$REGION" \
        --format="value(spec.containers[0].image)" 2>/dev/null || echo "")
    REVISION_CREATED=$(gcloud run revisions describe "$LATEST_REVISION" \
        --region="$REGION" \
        --format="value(metadata.creationTimestamp)" 2>/dev/null || echo "")
    REVISION_STATUS=$(gcloud run revisions describe "$LATEST_REVISION" \
        --region="$REGION" \
        --format="value(status.conditions[0].status)" 2>/dev/null || echo "")
    
    echo "   Image: $REVISION_IMAGE"
    echo "   Oluşturulma: $REVISION_CREATED"
    echo "   Durum: $REVISION_STATUS"
    
    # Image tag'ini kontrol et
    if echo "$REVISION_IMAGE" | grep -q ":latest"; then
        echo "   ⚠️  Image 'latest' tag'i kullanıyor (timestamp tag önerilir)"
    fi
else
    echo "❌ Revision bulunamadı"
    exit 1
fi
echo ""

# 3. Health Check
echo "📋 3. Health Check"
echo "-------------------"
echo "   Servis URL'sine istek gönderiliyor: $SERVICE_URL"
HTTP_CODE=$(curl -s -o /tmp/health_check_response.txt -w "%{http_code}" \
    --max-time 10 \
    "$SERVICE_URL" || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Servis yanıt veriyor (HTTP 200)"
elif [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Servis yönlendirme yapıyor (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "❌ Servis yanıt vermiyor (timeout veya bağlantı hatası)"
    exit 1
else
    echo "⚠️  Servis beklenmeyen yanıt veriyor (HTTP $HTTP_CODE)"
    echo "   Yanıt içeriği:"
    head -20 /tmp/health_check_response.txt 2>/dev/null || echo "   Yanıt okunamadı"
fi
echo ""

# 4. Log Kontrolü
echo "📋 4. Son Loglar"
echo "-------------------"
echo "   Son 10 log satırı:"
gcloud run services logs read "$SERVICE_NAME" \
    --region="$REGION" \
    --limit=10 \
    --format="table(timestamp,severity,textPayload)" 2>/dev/null || echo "   Log okunamadı"
echo ""

# 5. Environment Variables Kontrolü
echo "📋 5. Environment Variables"
echo "-------------------"
ENV_VARS=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(spec.template.spec.containers[0].env[].name)" 2>/dev/null || echo "")

if [ -n "$ENV_VARS" ]; then
    echo "✅ Environment variables mevcut:"
    echo "$ENV_VARS" | while read -r var; do
        if [ -n "$var" ]; then
            echo "   - $var"
        fi
    done
else
    echo "⚠️  Environment variables bulunamadı"
fi
echo ""

# 6. Build Durumu Kontrolü
echo "📋 6. Son Build Durumu"
echo "-------------------"
LAST_BUILD=$(gcloud builds list \
    --limit=1 \
    --sort-by=~createTime \
    --format="value(id,status,createTime)" 2>/dev/null || echo "")

if [ -n "$LAST_BUILD" ]; then
    BUILD_ID=$(echo "$LAST_BUILD" | cut -d' ' -f1)
    BUILD_STATUS=$(echo "$LAST_BUILD" | cut -d' ' -f2)
    BUILD_TIME=$(echo "$LAST_BUILD" | cut -d' ' -f3-)
    
    echo "   Son Build ID: $BUILD_ID"
    echo "   Durum: $BUILD_STATUS"
    echo "   Zaman: $BUILD_TIME"
    
    if [ "$BUILD_STATUS" = "SUCCESS" ]; then
        echo "   ✅ Build başarılı"
    elif [ "$BUILD_STATUS" = "FAILURE" ]; then
        echo "   ❌ Build başarısız"
        echo "   Detaylar için: gcloud builds log $BUILD_ID"
    else
        echo "   ⚠️  Build durumu: $BUILD_STATUS"
    fi
else
    echo "   ⚠️  Build bulunamadı"
fi
echo ""

# 7. Özet
echo "📋 7. Test Özeti"
echo "-------------------"
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    if [ "$REVISION_STATUS" = "True" ]; then
        echo "✅ Deployment başarılı görünüyor!"
        echo "   - Servis çalışıyor"
        echo "   - Revision aktif"
        echo "   - Health check başarılı"
    else
        echo "⚠️  Deployment tamamlanmış ancak revision durumu kontrol edilmeli"
    fi
else
    echo "❌ Deployment sorunlu görünüyor"
    echo "   - Servis yanıt vermiyor veya hata veriyor"
    echo "   - Logları kontrol edin: gcloud run services logs read $SERVICE_NAME --region=$REGION"
fi
echo ""
TEST_EOF
    chmod +x deploy/test_deployment.sh
    echo "✅ test_deployment.sh oluşturuldu"
else
    echo "✅ test_deployment.sh mevcut"
    chmod +x deploy/test_deployment.sh
fi

echo ""
echo "✅ Tüm scriptler hazır!"
echo ""
echo "🚀 Şimdi bağlantı kontrolünü çalıştırabilirsiniz:"
echo "   bash deploy/check_cloud_shell_connection.sh"
echo ""

