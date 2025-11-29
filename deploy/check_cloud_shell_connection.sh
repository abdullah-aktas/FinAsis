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
        --sort-by=~metadata.creationTimestamp \
        --format="value(metadata.name)" 2>/dev/null || echo "")
    
    if [ -n "$LATEST_REVISION" ]; then
        REVISION_IMAGE=$(gcloud run revisions describe "$LATEST_REVISION" \
            --region="$REGION" \
            --format="value(spec.containers[0].image)" 2>/dev/null || echo "")
        REVISION_CREATED=$(gcloud run revisions describe "$LATEST_REVISION" \
            --region="$REGION" \
            --format="value(metadata.creationTimestamp)" 2>/dev/null || echo "")
        REVISION_STATUS=$(gcloud run revisions describe "$LATEST_REVISION" \
            --region="$REGION" \
            --format="value(status.conditions[0].status)" 2>/dev/null || echo "")
        echo "   Son Revision: $LATEST_REVISION"
        echo "   Image: $REVISION_IMAGE"
        echo "   Oluşturulma: $REVISION_CREATED"
        echo "   Durum: $REVISION_STATUS"
    fi
    
    # Environment variables kontrolü
    echo ""
    echo "   Environment Variables:"
    ENV_VARS=$(gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="get(spec.template.spec.containers[0].env)" 2>/dev/null || echo "")
    if [ -n "$ENV_VARS" ] && [ "$ENV_VARS" != "[]" ]; then
        gcloud run services describe "$SERVICE_NAME" \
            --region="$REGION" \
            --format="table(spec.template.spec.containers[0].env[].name,spec.template.spec.containers[0].env[].value)" 2>/dev/null | head -20 || echo "   Env vars okunamadı"
    else
        echo "   ⚠️  Environment variables bulunamadı"
    fi
else
    echo "❌ Servis bulunamadı: $SERVICE_NAME"
    echo "   Servis henüz oluşturulmamış olabilir."
    SERVICE_URL=""
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

# Başarısız build varsa detaylarını göster
FAILED_BUILD=$(gcloud builds list \
    --limit=1 \
    --filter="status=FAILURE" \
    --sort-by=~createTime \
    --format="value(id)" 2>/dev/null || echo "")

if [ -n "$FAILED_BUILD" ]; then
    echo "   ⚠️  Son başarısız build bulundu: $FAILED_BUILD"
    echo "   Detaylar için: gcloud builds log $FAILED_BUILD"
    echo ""
fi

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
    echo "   Servis URL'sine istek gönderiliyor: $SERVICE_URL"
    HTTP_CODE=$(curl -s -o /tmp/health_check_response.txt -w "%{http_code}" \
        --max-time 10 \
        "$SERVICE_URL" 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Servis yanıt veriyor (HTTP 200)"
    elif [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
        echo "✅ Servis yönlendirme yapıyor (HTTP $HTTP_CODE)"
    elif [ "$HTTP_CODE" = "400" ]; then
        echo "❌ Servis HTTP 400 hatası veriyor"
        echo "   Bu genellikle ALLOWED_HOSTS veya yapılandırma sorunu anlamına gelir"
        echo "   Yanıt içeriği:"
        head -10 /tmp/health_check_response.txt 2>/dev/null || echo "   Yanıt okunamadı"
        echo ""
        echo "   🔧 Çözüm önerileri:"
        echo "   1. ALLOWED_HOSTS environment variable'ını kontrol edin"
        echo "   2. Servis URL'sini ALLOWED_HOSTS'e ekleyin"
        echo "   3. DJANGO_DEBUG=False olduğundan emin olun"
    elif [ "$HTTP_CODE" = "000" ]; then
        echo "❌ Servis yanıt vermiyor (timeout veya bağlantı hatası)"
    else
        echo "⚠️  Servis beklenmeyen yanıt veriyor (HTTP $HTTP_CODE)"
        echo "   Yanıt içeriği:"
        head -10 /tmp/health_check_response.txt 2>/dev/null || echo "   Yanıt okunamadı"
    fi
else
    echo "⚠️  Servis URL'si bulunamadı, health check yapılamadı"
fi
echo ""

# 8. Son Loglar
echo "📋 8. Son Loglar (Hata Varsa)"
echo "-------------------"
if [ -n "$SERVICE_URL" ] && [ "$HTTP_CODE" != "200" ] && [ "$HTTP_CODE" != "301" ] && [ "$HTTP_CODE" != "302" ]; then
    echo "   Son 10 log satırı:"
    gcloud run services logs read "$SERVICE_NAME" \
        --region="$REGION" \
        --limit=10 \
        --format="table(timestamp,severity,textPayload)" 2>/dev/null || echo "   Log okunamadı"
else
    echo "   Servis çalışıyor, log kontrolü atlanıyor"
fi
echo ""

# 9. Özet ve Öneriler
echo "📋 9. Özet ve Öneriler"
echo "-------------------"
echo ""

if [ "$HTTP_CODE" = "400" ]; then
    echo "❌ SORUN TESPİT EDİLDİ: HTTP 400 Hatası"
    echo ""
    echo "🔧 Hemen Yapılması Gerekenler:"
    echo ""
    echo "1. ALLOWED_HOSTS'i kontrol edin ve güncelleyin:"
    echo "   gcloud run services describe $SERVICE_NAME \\"
    echo "     --region=$REGION \\"
    echo "     --format='value(spec.template.spec.containers[0].env)'"
    echo ""
    echo "2. Servis URL'sini ALLOWED_HOSTS'e ekleyin:"
    SERVICE_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')
    echo "   gcloud run services update $SERVICE_NAME \\"
    echo "     --region=$REGION \\"
    echo "     --update-env-vars=\"DJANGO_ALLOWED_HOSTS=finasis.com.tr,www.finasis.com.tr,$SERVICE_HOST\""
    echo ""
elif [ -n "$FAILED_BUILD" ]; then
    echo "⚠️  Son build başarısız!"
    echo "   Build loglarını kontrol edin:"
    echo "   gcloud builds log $FAILED_BUILD"
    echo ""
fi

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
