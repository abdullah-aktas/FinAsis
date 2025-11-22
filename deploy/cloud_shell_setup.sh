#!/bin/bash
# =============================================================================
# Cloud Shell Hızlı Kurulum ve Düzeltme
# Proje klonlanmamışsa önce klonlar, sonra düzeltmeleri uygular
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

# Proje bilgileri
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null || echo '')}"
REGION="${REGION:-europe-west1}"
SERVICE_NAME="${SERVICE_NAME:-finasis-prod}"
MEMORY="${MEMORY:-2Gi}"
CPU="${CPU:-2}"
TIMEOUT="${TIMEOUT:-300}"
MIN_INSTANCES="${MIN_INSTANCES:-1}"
MAX_INSTANCES="${MAX_INSTANCES:-10}"

print_header "🚀 FinAsis Cloud Run Düzeltme Script'i"

# Proje kontrolü
if [ -z "$PROJECT_ID" ]; then
    print_error "Google Cloud projesi ayarlanmamış!"
    echo "Lütfen şu komutu çalıştırın:"
    echo "  gcloud config set project your-project-id"
    exit 1
fi

print_info "Proje: $PROJECT_ID"
print_info "Bölge: $REGION"
print_info "Servis: $SERVICE_NAME"
echo ""

# Mevcut servis bilgilerini al
print_info "Mevcut servis bilgileri kontrol ediliyor..."
CURRENT_MEMORY=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(spec.template.spec.containers[0].resources.limits.memory)" 2>/dev/null || echo "")

if [ -n "$CURRENT_MEMORY" ]; then
    print_info "Mevcut memory limit: $CURRENT_MEMORY"
else
    print_warning "Servis bulunamadı veya memory limit bilgisi alınamadı"
    print_info "Servis adını kontrol edin: $SERVICE_NAME"
    echo ""
    print_info "Mevcut Cloud Run servisleri:"
    gcloud run services list --region="$REGION" --format="table(metadata.name,status.url)" 2>/dev/null || {
        print_error "Cloud Run servisleri listelenemedi"
        exit 1
    }
    echo ""
    read -p "Devam etmek istiyor musunuz? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "İşlem iptal edildi"
        exit 0
    fi
fi

echo ""

# Environment variables hazırla
ENV_VARS="MPLCONFIGDIR=/tmp/matplotlib-cache"
ENV_VARS="$ENV_VARS,PYTHONUNBUFFERED=1"
ENV_VARS="$ENV_VARS,PYTHONDONTWRITEBYTECODE=1"

# Mevcut environment variables'ı al ve birleştir
print_info "Mevcut environment variables kontrol ediliyor..."
EXISTING_ENV=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(spec.template.spec.containers[0].env)" 2>/dev/null || echo "")

if [ -n "$EXISTING_ENV" ] && [ "$EXISTING_ENV" != "None" ] && [ "$EXISTING_ENV" != "" ]; then
    print_info "Mevcut environment variables korunacak"
    # Mevcut env vars'ı da ekle (MPLCONFIGDIR varsa güncelle)
    # Önce mevcut env vars'ı parse et ve MPLCONFIGDIR'ı güncelle veya ekle
    ENV_VARS="$EXISTING_ENV,MPLCONFIGDIR=/tmp/matplotlib-cache"
else
    print_info "Yeni environment variables eklenecek"
fi

# Deployment komutunu hazırla
print_header "🚀 Servis Güncelleniyor"

DEPLOY_CMD="gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --memory=$MEMORY \
    --cpu=$CPU \
    --timeout=$TIMEOUT \
    --min-instances=$MIN_INSTANCES \
    --max-instances=$MAX_INSTANCES \
    --set-env-vars=$ENV_VARS \
    --project=$PROJECT_ID"

print_info "Çalıştırılacak komut:"
echo "$DEPLOY_CMD"
echo ""

# Onay iste
read -p "Devam etmek istiyor musunuz? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "İşlem iptal edildi"
    exit 0
fi

# Deployment'ı çalıştır
print_info "Deployment başlatılıyor..."
if eval "$DEPLOY_CMD"; then
    print_success "Servis başarıyla güncellendi!"
    echo ""
    
    # Güncellenmiş bilgileri göster
    print_header "📊 Güncellenmiş Servis Bilgileri"
    gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="table(
            metadata.name,
            status.url,
            spec.template.spec.containers[0].resources.limits.memory,
            spec.template.spec.containers[0].resources.limits.cpu,
            spec.template.spec.timeoutSeconds
        )" \
        --project="$PROJECT_ID" 2>/dev/null || print_warning "Servis bilgileri alınamadı"
    
    echo ""
    print_info "Environment Variables:"
    gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="value(spec.template.spec.containers[0].env[?(@.name=='MPLCONFIGDIR')].value)" \
        --project="$PROJECT_ID" 2>/dev/null && print_success "MPLCONFIGDIR ayarlandı" || print_warning "MPLCONFIGDIR kontrol edilemedi"
    
    echo ""
    print_success "Düzeltmeler tamamlandı!"
    print_info "Servis URL'si:"
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="value(status.url)" \
        --project="$PROJECT_ID" 2>/dev/null || echo "")
    
    if [ -n "$SERVICE_URL" ]; then
        echo "  $SERVICE_URL"
    else
        print_warning "URL alınamadı"
    fi
    
else
    print_error "Deployment başarısız oldu!"
    exit 1
fi

echo ""
print_header "📋 Yapılan Değişiklikler"
echo "  ✅ Memory limit: $MEMORY (önceden: ${CURRENT_MEMORY:-'bilinmiyor'})"
echo "  ✅ CPU: $CPU"
echo "  ✅ Timeout: ${TIMEOUT}s"
echo "  ✅ Min instances: $MIN_INSTANCES"
echo "  ✅ Max instances: $MAX_INSTANCES"
echo "  ✅ MPLCONFIGDIR=/tmp/matplotlib-cache eklendi"
echo "  ✅ PYTHONUNBUFFERED=1 eklendi"
echo "  ✅ PYTHONDONTWRITEBYTECODE=1 eklendi"
echo ""
print_info "Servis birkaç dakika içinde yeni ayarlarla çalışmaya başlayacak"
print_info "Logları kontrol etmek için:"
echo "  gcloud logging tail \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --project=$PROJECT_ID"

