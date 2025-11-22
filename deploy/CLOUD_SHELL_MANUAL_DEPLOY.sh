#!/bin/bash
# =============================================================================
# Manuel Deployment Script - Cloud Shell için
# Bu script'i Cloud Shell'de çalıştırarak son değişiklikleri canlıya alabilirsiniz
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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Ayarlar
SERVICE_NAME="${SERVICE_NAME:-finasis-prod}"
REGION="${REGION:-europe-west1}"
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo '')

if [ -z "$PROJECT_ID" ]; then
    print_error "Google Cloud projesi ayarlanmamış!"
    echo "Lütfen şu komutu çalıştırın:"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

print_header "🚀 FinAsis Manuel Deployment"
print_info "Proje: $PROJECT_ID"
print_info "Bölge: $REGION"
print_info "Servis: $SERVICE_NAME"
echo ""

# Repository kontrolü
if [ ! -d "FinAsis" ]; then
    print_info "Repository clone ediliyor..."
    git clone https://github.com/abdullah-aktas/FinAsis.git
    cd FinAsis
else
    print_info "Repository güncelleniyor..."
    cd FinAsis
    git pull origin main
fi

# Son commit bilgisi
LAST_COMMIT=$(git log -1 --oneline)
print_info "Son commit: $LAST_COMMIT"
echo ""

# Deployment başlat
print_header "📦 Cloud Build Başlatılıyor"
print_info "Build ve deployment işlemi başlatılıyor..."
echo ""

gcloud builds submit \
    --config=deploy/cloud_run/cloudbuild.yaml \
    --region="$REGION" \
    --substitutions="_SERVICE=$SERVICE_NAME" \
    --project="$PROJECT_ID"

# Deployment sonrası kontrol
print_header "✅ Deployment Tamamlandı"

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    print_success "Servis URL: $SERVICE_URL"
    echo ""
    print_info "Test için:"
    echo "  curl $SERVICE_URL"
    echo ""
    print_info "Logları görüntülemek için:"
    echo "  gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=50"
else
    print_error "Servis URL alınamadı!"
fi

echo ""
print_success "Deployment işlemi tamamlandı! 🎉"

