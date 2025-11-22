#!/bin/bash
# =============================================================================
# 50K Users Production Deployment - Cloud Shell Versiyonu
# Proje dosyaları yoksa doğrudan Cloud Shell'de çalıştırılabilir
# =============================================================================

set -euo pipefail

# Renkli çıktı
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Ayarlar
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo '')
REGION="${REGION:-europe-west1}"
SERVICE_NAME="${SERVICE_NAME:-finasis-api}"
DB_INSTANCE_NAME="${DB_INSTANCE_NAME:-finasis-prod-db}"
REDIS_INSTANCE_NAME="${REDIS_INSTANCE_NAME:-finasis-redis}"

if [ -z "$PROJECT_ID" ]; then
    print_error "Google Cloud projesi ayarlanmamış!"
    exit 1
fi

print_header "🚀 50,000 Eşzamanlı Kullanıcı için Production Deployment"
print_info "Proje: $PROJECT_ID"
print_info "Bölge: $REGION"
print_info "Servis: $SERVICE_NAME"
echo ""

# Onay
read -p "Devam etmek istiyor musunuz? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "İşlem iptal edildi"
    exit 0
fi

# =============================================================================
# 1. Gerekli API'leri Etkinleştir
# =============================================================================
print_header "📦 Gerekli API'ler Etkinleştiriliyor"

gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  compute.googleapis.com \
  storage-component.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  --project="$PROJECT_ID" 2>/dev/null || print_warning "Bazı API'ler zaten etkin"

print_success "API'ler etkinleştirildi"

# =============================================================================
# 2. Cloud SQL (PostgreSQL) - Sadece bilgi ver
# =============================================================================
print_header "🗄️  Cloud SQL (PostgreSQL)"

if gcloud sql instances describe "$DB_INSTANCE_NAME" --project="$PROJECT_ID" 2>/dev/null; then
    print_success "Cloud SQL instance mevcut: $DB_INSTANCE_NAME"
    CLOUD_SQL_CONNECTION=$(gcloud sql instances describe "$DB_INSTANCE_NAME" \
        --format="value(connectionName)" \
        --project="$PROJECT_ID")
else
    print_warning "Cloud SQL instance bulunamadı: $DB_INSTANCE_NAME"
    print_info "Cloud SQL instance oluşturmak için:"
    echo "  gcloud sql instances create $DB_INSTANCE_NAME \\"
    echo "    --database-version=POSTGRES_15 \\"
    echo "    --tier=db-highmem-16 \\"
    echo "    --region=$REGION \\"
    echo "    --storage-size=500GB \\"
    echo "    --project=$PROJECT_ID"
    echo ""
    read -p "Cloud SQL instance oluşturmak istiyor musunuz? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud sql instances create "$DB_INSTANCE_NAME" \
            --database-version=POSTGRES_15 \
            --tier=db-highmem-16 \
            --region="$REGION" \
            --storage-size=500GB \
            --storage-auto-increase \
            --backup-start-time=02:00 \
            --enable-bin-log \
            --availability-type=REGIONAL \
            --deletion-protection \
            --project="$PROJECT_ID"
        
        gcloud sql databases create finasis \
            --instance="$DB_INSTANCE_NAME" \
            --project="$PROJECT_ID"
        
        DB_PASSWORD=$(openssl rand -base64 32)
        gcloud sql users create finasis-app \
            --instance="$DB_INSTANCE_NAME" \
            --password="$DB_PASSWORD" \
            --project="$PROJECT_ID"
        
        echo -n "$DB_PASSWORD" | gcloud secrets create DJANGO_DB_PASSWORD \
            --data-file=- \
            --replication-policy="automatic" \
            --project="$PROJECT_ID" 2>/dev/null || \
        echo -n "$DB_PASSWORD" | gcloud secrets versions add DJANGO_DB_PASSWORD \
            --data-file=- \
            --project="$PROJECT_ID"
        
        CLOUD_SQL_CONNECTION=$(gcloud sql instances describe "$DB_INSTANCE_NAME" \
            --format="value(connectionName)" \
            --project="$PROJECT_ID")
        print_success "Cloud SQL instance oluşturuldu"
    else
        CLOUD_SQL_CONNECTION=""
    fi
fi

# =============================================================================
# 3. Cloud Run Servis Güncelleme (50K Users için)
# =============================================================================
print_header "🚀 Cloud Run Servis Güncelleniyor (50K Users)"

# Mevcut servisi kontrol et
if ! gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" 2>/dev/null; then
    print_error "Servis bulunamadı: $SERVICE_NAME"
    print_info "Önce servisi deploy etmeniz gerekiyor"
    exit 1
fi

# Servis URL'sini al
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID")

CLOUD_RUN_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')

print_info "Servis URL: $SERVICE_URL"
print_info "Hostname: $CLOUD_RUN_HOST"

# 50K users için optimize edilmiş ayarlar
print_info "50K users için servis güncelleniyor..."

gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --memory=4Gi \
    --cpu=4 \
    --timeout=300 \
    --concurrency=100 \
    --min-instances=10 \
    --max-instances=500 \
    --cpu-boost \
    --project="$PROJECT_ID"

print_success "Cloud Run servisi güncellendi (50K users için optimize edildi)"

# =============================================================================
# 4. Environment Variables (ALLOWED_HOSTS dahil)
# =============================================================================
print_header "⚙️  Environment Variables Ayarlanıyor"

# Mevcut env vars'ı al
ENV_JSON=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="json" \
    --project="$PROJECT_ID")

# jq yüklü mü kontrol et
if ! command -v jq &> /dev/null; then
    print_info "jq yükleniyor..."
    sudo apt-get update -qq && sudo apt-get install -y jq > /dev/null 2>&1
fi

# Geçici dosya oluştur
ENV_FILE=$(mktemp)

# Mevcut env vars'ı dosyaya yaz
echo "$ENV_JSON" | jq -r '.spec.template.spec.containers[0].env[]? | "\(.name)=\(.value)"' > "$ENV_FILE"

# ALLOWED_HOSTS'i güncelle
ALLOWED_HOSTS="127.0.0.1,localhost,finasis.com.tr,www.finasis.com.tr,$CLOUD_RUN_HOST"

if grep -q "^DJANGO_ALLOWED_HOSTS=" "$ENV_FILE"; then
    sed -i "s|^DJANGO_ALLOWED_HOSTS=.*|DJANGO_ALLOWED_HOSTS=$ALLOWED_HOSTS|" "$ENV_FILE"
else
    echo "DJANGO_ALLOWED_HOSTS=$ALLOWED_HOSTS" >> "$ENV_FILE"
fi

# Diğer önemli env vars
if ! grep -q "^CLOUD_RUN_HOST=" "$ENV_FILE"; then
    echo "CLOUD_RUN_HOST=$CLOUD_RUN_HOST" >> "$ENV_FILE"
fi
if ! grep -q "^MPLCONFIGDIR=" "$ENV_FILE"; then
    echo "MPLCONFIGDIR=/tmp/matplotlib-cache" >> "$ENV_FILE"
fi
if ! grep -q "^PYTHONUNBUFFERED=" "$ENV_FILE"; then
    echo "PYTHONUNBUFFERED=1" >> "$ENV_FILE"
fi
if ! grep -q "^PYTHONDONTWRITEBYTECODE=" "$ENV_FILE"; then
    echo "PYTHONDONTWRITEBYTECODE=1" >> "$ENV_FILE"
fi
if ! grep -q "^DJANGO_DB_CONN_MAX_AGE=" "$ENV_FILE"; then
    echo "DJANGO_DB_CONN_MAX_AGE=600" >> "$ENV_FILE"
fi
if ! grep -q "^GUNICORN_WORKERS=" "$ENV_FILE"; then
    echo "GUNICORN_WORKERS=4" >> "$ENV_FILE"
fi
if ! grep -q "^GUNICORN_THREADS=" "$ENV_FILE"; then
    echo "GUNICORN_THREADS=8" >> "$ENV_FILE"
fi

# Cloud SQL connection (varsa)
if [ -n "$CLOUD_SQL_CONNECTION" ]; then
    if ! grep -q "^CLOUD_SQL_CONNECTION_NAME=" "$ENV_FILE"; then
        echo "CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION" >> "$ENV_FILE"
    fi
fi

# Env vars'ı güncelle
print_info "Environment variables güncelleniyor..."
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --env-vars-file="$ENV_FILE" \
    --project="$PROJECT_ID"

# Temizlik
rm -f "$ENV_FILE"

print_success "Environment variables ayarlandı"

# =============================================================================
# Özet
# =============================================================================
print_header "✅ Deployment Tamamlandı!"

echo "📊 Güncellenmiş Servis Bilgileri:"
gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="table(
        metadata.name,
        status.url,
        spec.template.spec.containers[0].resources.limits.memory,
        spec.template.spec.containers[0].resources.limits.cpu,
        spec.template.spec.containerConcurrency,
        spec.template.spec.timeoutSeconds,
        status.conditions[0].status
    )" \
    --project="$PROJECT_ID"

echo ""
print_success "Servis 50,000 eşzamanlı kullanıcı için optimize edildi!"
print_info "Servis URL: $SERVICE_URL"
echo ""
print_info "📋 Yapılan Değişiklikler:"
echo "  ✅ Memory: 4Gi"
echo "  ✅ CPU: 4"
echo "  ✅ Concurrency: 100"
echo "  ✅ Min Instances: 10"
echo "  ✅ Max Instances: 500"
echo "  ✅ Timeout: 300s"
echo "  ✅ ALLOWED_HOSTS güncellendi"
echo "  ✅ Environment variables ayarlandı"

