#!/bin/bash
# =============================================================================
# Hızlı Production Deployment Script
# GitHub'a push yaptıktan sonra bu script ile canlıya alabilirsiniz
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
    echo "Lütfen şu komutu çalıştırın:"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

print_header "🚀 FinAsis Production Deployment"
print_info "Proje: $PROJECT_ID"
print_info "Bölge: $REGION"
print_info "Servis: $SERVICE_NAME"
echo ""

# Mevcut servis URL'sini al
CURRENT_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID" 2>/dev/null || echo "")

if [ -n "$CURRENT_URL" ]; then
    print_info "Mevcut servis URL: $CURRENT_URL"
fi

echo ""
read -p "Deployment'a devam etmek istiyor musunuz? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Deployment iptal edildi."
    exit 0
fi

# Cloud Build'i çalıştır
print_header "📦 Docker Image Build ve Push"
print_info "Cloud Build başlatılıyor..."

BUILD_ID=$(gcloud builds submit \
    --config=deploy/cloud_run/cloudbuild.yaml \
    --region="$REGION" \
    --substitutions="_SERVICE=$SERVICE_NAME" \
    --format="value(id)" \
    --project="$PROJECT_ID" 2>&1 | tee /tmp/build_output.log | grep -oP 'ID: \K[^\s]+' || echo "")

if [ -z "$BUILD_ID" ]; then
    # Alternatif: build output'tan ID çıkar
    BUILD_ID=$(gcloud builds list --limit=1 --format="value(id)" --project="$PROJECT_ID")
fi

if [ -n "$BUILD_ID" ]; then
    print_success "Build başlatıldı: $BUILD_ID"
    print_info "Build durumunu izlemek için:"
    echo "  gcloud builds log $BUILD_ID --project=$PROJECT_ID"
else
    print_error "Build ID alınamadı. Logları kontrol edin."
    exit 1
fi

# Build'in tamamlanmasını bekle (opsiyonel)
echo ""
read -p "Build'in tamamlanmasını beklemek istiyor musunuz? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Build tamamlanıyor, lütfen bekleyin..."
    gcloud builds wait "$BUILD_ID" --project="$PROJECT_ID"
    
    BUILD_STATUS=$(gcloud builds describe "$BUILD_ID" --format="value(status)" --project="$PROJECT_ID")
    
    if [ "$BUILD_STATUS" = "SUCCESS" ]; then
        print_success "Build başarıyla tamamlandı!"
    else
        print_error "Build başarısız oldu. Durum: $BUILD_STATUS"
        exit 1
    fi
fi

# Servis URL'sini göster
print_header "🌐 Deployment Tamamlandı"
NEW_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$PROJECT_ID" 2>/dev/null || echo "")

if [ -n "$NEW_URL" ]; then
    print_success "Servis URL: $NEW_URL"
    echo ""
    print_info "Test için:"
    echo "  curl $NEW_URL"
    echo ""
    print_info "Logları görüntülemek için:"
    echo "  gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=50"
else
    print_warning "Servis URL alınamadı. Manuel kontrol edin."
fi

echo ""
print_success "Deployment işlemi tamamlandı! 🎉"

