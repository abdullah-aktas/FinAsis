#!/bin/bash
# =============================================================================
# 50K Users Deployment - Quota Limitlerine Uygun Versiyon
# Cloud Run quota limitleri: Max 50 instances, 200 vCPU, 400GB memory
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
SERVICE_NAME="${SERVICE_NAME:-finasis-prod}"
REGION="${REGION:-europe-west1}"
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo '')

if [ -z "$PROJECT_ID" ]; then
    print_error "Google Cloud projesi ayarlanmamış!"
    exit 1
fi

print_header "🚀 50K Users Deployment (Quota Uyumlu)"
print_info "Proje: $PROJECT_ID"
print_info "Bölge: $REGION"
print_info "Servis: $SERVICE_NAME"
echo ""

# Quota bilgileri
print_info "📊 Cloud Run Quota Limitleri:"
echo "  • Max Instances: 50 (bölgesel limit)"
echo "  • Max CPU: 200 vCPU (bölgesel limit)"
echo "  • Max Memory: 400GB (bölgesel limit)"
echo ""

# Optimize edilmiş yapılandırma
print_info "🎯 Optimize Edilmiş Yapılandırma (50K users için):"
echo "  • Instances: 10-50 (max quota)"
echo "  • Memory: 3GB per instance (50 × 3GB = 150GB < 400GB limit)"
echo "  • CPU: 4 vCPU per instance (50 × 4 = 200 vCPU = limit)"
echo "  • Concurrency: 200 per instance (50 × 200 = 10,000 eşzamanlı)"
echo "  • Toplam Kapasite: 10,000 eşzamanlı request"
echo ""

print_warning "Not: 50K eşzamanlı kullanıcı için quota artırımı gerekebilir"
print_info "Alternatif: Concurrency'yi artırarak daha az instance ile daha fazla yük kaldırabiliriz"
echo ""

# Onay
read -p "Devam etmek istiyor musunuz? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "İşlem iptal edildi"
    exit 0
fi

# =============================================================================
# Quota Uyumlu Deployment
# =============================================================================
print_header "🚀 Cloud Run Servis Güncelleniyor"

# Mevcut servisi kontrol et
if ! gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" 2>/dev/null; then
    print_error "Servis bulunamadı: $SERVICE_NAME"
    exit 1
fi

# Quota uyumlu ayarlar
print_info "Quota limitlerine uygun ayarlarla güncelleniyor..."

gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --memory=3Gi \
    --cpu=4 \
    --timeout=300 \
    --concurrency=200 \
    --min-instances=10 \
    --max-instances=50 \
    --cpu-boost \
    --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    print_success "Servis başarıyla güncellendi!"
else
    print_error "Deployment başarısız oldu"
    echo ""
    print_info "Quota artırımı için:"
    echo "  1. Google Cloud Console → IAM & Admin → Quotas"
    echo "  2. 'Cloud Run API' filtrele"
    echo "  3. 'CPU allocation per project per region' quota'sını artır"
    echo "  4. 'Memory allocation per project per region' quota'sını artır"
    exit 1
fi

# =============================================================================
# Environment Variables
# =============================================================================
print_header "⚙️  Environment Variables Ayarlanıyor"

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID")

CLOUD_RUN_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')

# jq yüklü mü kontrol et
if ! command -v jq &> /dev/null; then
    print_info "jq yükleniyor..."
    sudo apt-get update -qq && sudo apt-get install -y jq > /dev/null 2>&1
fi

# Mevcut env vars'ı al
ENV_JSON=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="json" \
    --project="$PROJECT_ID")

# Geçici dosya
ENV_FILE=$(mktemp)
echo "$ENV_JSON" | jq -r '.spec.template.spec.containers[0].env[]? | "\(.name)=\(.value)"' > "$ENV_FILE"

# ALLOWED_HOSTS güncelle
ALLOWED_HOSTS="127.0.0.1,localhost,finasis.com.tr,www.finasis.com.tr,$CLOUD_RUN_HOST"
if grep -q "^DJANGO_ALLOWED_HOSTS=" "$ENV_FILE"; then
    sed -i "s|^DJANGO_ALLOWED_HOSTS=.*|DJANGO_ALLOWED_HOSTS=$ALLOWED_HOSTS|" "$ENV_FILE"
else
    echo "DJANGO_ALLOWED_HOSTS=$ALLOWED_HOSTS" >> "$ENV_FILE"
fi

# Diğer env vars
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

# Güncelle
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --env-vars-file="$ENV_FILE" \
    --project="$PROJECT_ID"

rm -f "$ENV_FILE"

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
        spec.template.spec.timeoutSeconds
    )" \
    --project="$PROJECT_ID"

echo ""
print_success "Servis quota limitlerine uygun şekilde güncellendi!"
print_info "Servis URL: $SERVICE_URL"
echo ""
print_info "📋 Yapılan Değişiklikler:"
echo "  ✅ Memory: 3Gi per instance"
echo "  ✅ CPU: 4 per instance"
echo "  ✅ Concurrency: 200 per instance"
echo "  ✅ Min Instances: 10"
echo "  ✅ Max Instances: 50 (quota limiti)"
echo "  ✅ Toplam Kapasite: 10,000 eşzamanlı request"
echo ""
print_warning "⚠️  50K eşzamanlı kullanıcı için quota artırımı gerekli!"
echo ""
print_info "📈 Quota Artırımı İçin:"
echo "  1. Google Cloud Console → IAM & Admin → Quotas"
echo "  2. Filtre: 'Cloud Run API'"
echo "  3. Artırılacak quota'lar:"
echo "     • CPU allocation per project per region: 200 → 2000+"
echo "     • Memory allocation per project per region: 400GB → 2000GB+"
echo "     • Max instances per service: 50 → 500+"
echo ""
print_info "Alternatif: Multi-region deployment düşünülebilir"

