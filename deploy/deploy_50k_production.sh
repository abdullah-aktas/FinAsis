#!/bin/bash
# =============================================================================
# 50,000 Eşzamanlı Kullanıcı için Production Deployment Script
# =============================================================================
# Bu script tüm gerekli servisleri oluşturur ve production'a deploy eder
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
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null || echo '')}"
REGION="${REGION:-europe-west1}"
SERVICE_NAME="${SERVICE_NAME:-finasis-api}"
DB_INSTANCE_NAME="${DB_INSTANCE_NAME:-finasis-prod-db}"
REDIS_INSTANCE_NAME="${REDIS_INSTANCE_NAME:-finasis-redis}"

if [ -z "$PROJECT_ID" ]; then
    print_error "Google Cloud projesi ayarlanmamış!"
    echo "Lütfen şu komutu çalıştırın:"
    echo "  export GOOGLE_CLOUD_PROJECT=your-project-id"
    echo "  veya"
    echo "  gcloud config set project your-project-id"
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
# 2. Cloud SQL (PostgreSQL) Oluştur
# =============================================================================
print_header "🗄️  Cloud SQL (PostgreSQL) Oluşturuluyor"

if gcloud sql instances describe "$DB_INSTANCE_NAME" --project="$PROJECT_ID" 2>/dev/null; then
    print_warning "Cloud SQL instance zaten mevcut: $DB_INSTANCE_NAME"
    CLOUD_SQL_CONNECTION=$(gcloud sql instances describe "$DB_INSTANCE_NAME" \
        --format="value(connectionName)" \
        --project="$PROJECT_ID")
else
    print_info "Cloud SQL instance oluşturuluyor (bu işlem 5-10 dakika sürebilir)..."
    
    gcloud sql instances create "$DB_INSTANCE_NAME" \
        --database-version=POSTGRES_15 \
        --tier=db-highmem-16 \
        --region="$REGION" \
        --storage-type=SSD \
        --storage-size=500GB \
        --storage-auto-increase \
        --backup-start-time=02:00 \
        --enable-bin-log \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=03 \
        --availability-type=REGIONAL \
        --deletion-protection \
        --project="$PROJECT_ID"
    
    print_success "Cloud SQL instance oluşturuldu"
    
    # Database oluştur
    print_info "Database oluşturuluyor..."
    gcloud sql databases create finasis \
        --instance="$DB_INSTANCE_NAME" \
        --project="$PROJECT_ID" || print_warning "Database zaten mevcut"
    
    # Kullanıcı oluştur
    DB_PASSWORD=$(openssl rand -base64 32)
    print_info "Database kullanıcısı oluşturuluyor..."
    gcloud sql users create finasis-app \
        --instance="$DB_INSTANCE_NAME" \
        --password="$DB_PASSWORD" \
        --project="$PROJECT_ID" || print_warning "Kullanıcı zaten mevcut"
    
    # Password'ü secret'a kaydet
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
fi

print_success "Cloud SQL hazır: $CLOUD_SQL_CONNECTION"

# =============================================================================
# 3. Redis (Memorystore) Oluştur
# =============================================================================
print_header "💾 Redis (Memorystore) Oluşturuluyor"

if gcloud redis instances describe "$REDIS_INSTANCE_NAME" --region="$REGION" --project="$PROJECT_ID" 2>/dev/null; then
    print_warning "Redis instance zaten mevcut: $REDIS_INSTANCE_NAME"
    REDIS_HOST=$(gcloud redis instances describe "$REDIS_INSTANCE_NAME" \
        --region="$REGION" \
        --format="value(host)" \
        --project="$PROJECT_ID")
    REDIS_PORT=$(gcloud redis instances describe "$REDIS_INSTANCE_NAME" \
        --region="$REGION" \
        --format="value(port)" \
        --project="$PROJECT_ID")
else
    print_info "Redis instance oluşturuluyor (bu işlem 5-10 dakika sürebilir)..."
    
    gcloud redis instances create "$REDIS_INSTANCE_NAME" \
        --size=4 \
        --region="$REGION" \
        --redis-version=redis_7_0 \
        --tier=standard \
        --network=projects/$PROJECT_ID/global/networks/default \
        --connect-mode=PRIVATE_SERVICE_ACCESS \
        --enable-auth \
        --project="$PROJECT_ID"
    
    REDIS_HOST=$(gcloud redis instances describe "$REDIS_INSTANCE_NAME" \
        --region="$REGION" \
        --format="value(host)" \
        --project="$PROJECT_ID")
    REDIS_PORT=$(gcloud redis instances describe "$REDIS_INSTANCE_NAME" \
        --region="$REGION" \
        --format="value(port)" \
        --project="$PROJECT_ID")
    
    print_success "Redis instance oluşturuldu"
fi

print_success "Redis hazır: $REDIS_HOST:$REDIS_PORT"

# =============================================================================
# 4. Secrets Oluştur
# =============================================================================
print_header "🔐 Secrets Oluşturuluyor"

# Django Secret Key
if ! gcloud secrets describe DJANGO_SECRET_KEY --project="$PROJECT_ID" 2>/dev/null; then
    echo -n "$(openssl rand -base64 64)" | \
        gcloud secrets create DJANGO_SECRET_KEY \
        --data-file=- \
        --replication-policy="automatic" \
        --project="$PROJECT_ID"
    print_success "DJANGO_SECRET_KEY oluşturuldu"
else
    print_warning "DJANGO_SECRET_KEY zaten mevcut"
fi

# =============================================================================
# 5. Cloud Storage Buckets
# =============================================================================
print_header "📦 Cloud Storage Buckets Oluşturuluyor"

# Static files bucket
if ! gsutil ls -b "gs://$PROJECT_ID-static" 2>/dev/null; then
    gsutil mb -p "$PROJECT_ID" -c STANDARD -l "$REGION" "gs://$PROJECT_ID-static"
    print_success "Static files bucket oluşturuldu"
else
    print_warning "Static files bucket zaten mevcut"
fi

# Media files bucket
if ! gsutil ls -b "gs://$PROJECT_ID-media" 2>/dev/null; then
    gsutil mb -p "$PROJECT_ID" -c STANDARD -l "$REGION" "gs://$PROJECT_ID-media"
    print_success "Media files bucket oluşturuldu"
else
    print_warning "Media files bucket zaten mevcut"
fi

# =============================================================================
# 6. Cloud Run Deployment
# =============================================================================
print_header "🚀 Cloud Run Deployment Başlatılıyor"

print_info "Cloud Build ile deployment başlatılıyor..."
print_warning "Bu işlem 15-30 dakika sürebilir..."

gcloud builds submit \
  --config=deploy/production_50k_users.yaml \
  --substitutions="_CLOUD_SQL_CONNECTION=$CLOUD_SQL_CONNECTION" \
  --project="$PROJECT_ID"

print_success "Cloud Run deployment tamamlandı"

# =============================================================================
# 7. Environment Variables Ayarla
# =============================================================================
print_header "⚙️  Environment Variables Ayarlanıyor"

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    CLOUD_RUN_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')
    
    print_info "Servis URL: $SERVICE_URL"
    print_info "Cloud Run Host: $CLOUD_RUN_HOST"
    
    # Environment variables'ı güncelle
    gcloud run services update "$SERVICE_NAME" \
        --region="$REGION" \
        --update-env-vars="
            CLOUD_RUN_HOST=$CLOUD_RUN_HOST,
            REDIS_HOST=$REDIS_HOST,
            REDIS_PORT=$REDIS_PORT,
            DJANGO_DB_CONN_MAX_AGE=600
        " \
        --project="$PROJECT_ID" 2>/dev/null || print_warning "Environment variables güncellenemedi"
    
    print_success "Environment variables ayarlandı"
else
    print_warning "Servis URL alınamadı, environment variables manuel ayarlanmalı"
fi

# =============================================================================
# Özet
# =============================================================================
print_header "✅ Deployment Tamamlandı!"

echo "📊 Deployment Özeti:"
echo "  ✅ Cloud SQL: $CLOUD_SQL_CONNECTION"
echo "  ✅ Redis: $REDIS_HOST:$REDIS_PORT"
echo "  ✅ Cloud Run: $SERVICE_URL"
echo ""
echo "📋 Sonraki Adımlar:"
echo "  1. Database migrations çalıştırın"
echo "  2. Static files collect edin"
echo "  3. Load testing yapın"
echo "  4. Monitoring dashboards oluşturun"
echo ""
print_info "Detaylı bilgi için: deploy/PRODUCTION_50K_DEPLOYMENT.md"

