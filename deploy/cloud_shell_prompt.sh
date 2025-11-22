#!/bin/bash
# =============================================================================
# FinAsis Cloud Shell Diagnostic & Setup Script
# Google Cloud Shell için hızlı diagnostic ve setup komutları
# =============================================================================

set -euo pipefail

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Proje bilgileri
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null || echo 'NOT_SET')}"
REGION="${REGION:-europe-west4}"
SERVICE_NAME="${SERVICE_NAME:-finasis-api}"
REPOSITORY="${REPOSITORY:-finasis-app}"

# =============================================================================
# Yardımcı Fonksiyonlar
# =============================================================================

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

# =============================================================================
# 1. Proje Durumu Kontrolü
# =============================================================================

check_project_status() {
    print_header "📊 Proje Durumu Kontrolü"
    
    if [ "$PROJECT_ID" = "NOT_SET" ]; then
        print_error "Google Cloud projesi ayarlanmamış!"
        echo "Lütfen şu komutu çalıştırın:"
        echo "  gcloud config set project YOUR_PROJECT_ID"
        return 1
    fi
    
    print_success "Aktif Proje: $PROJECT_ID"
    print_info "Bölge: $REGION"
    print_info "Servis: $SERVICE_NAME"
    
    # Proje bilgilerini göster
    echo ""
    gcloud config list --format="table(name,value)" 2>/dev/null || print_warning "gcloud config okunamadı"
}

# =============================================================================
# 2. Cloud Run Servis Durumu
# =============================================================================

check_cloud_run_status() {
    print_header "🚀 Cloud Run Servis Durumu"
    
    if ! gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null; then
        print_warning "Cloud Run servisi bulunamadı: $SERVICE_NAME"
        echo "Servis oluşturulmamış olabilir veya farklı bir isimle kayıtlı."
        return 1
    fi
    
    print_success "Servis bulundu!"
    echo ""
    
    # Servis detaylarını göster
    gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="table(
            metadata.name,
            status.url,
            status.conditions[0].status,
            spec.template.spec.containers[0].image,
            spec.template.spec.containers[0].resources.limits.memory,
            spec.template.spec.containers[0].resources.limits.cpu
        )" 2>/dev/null || print_error "Servis bilgileri alınamadı"
}

# =============================================================================
# 3. Son Logları Görüntüleme
# =============================================================================

view_logs() {
    print_header "📋 Cloud Run Logları (Son 50 satır)"
    
    local lines="${1:-50}"
    
    print_info "Son $lines satır log görüntüleniyor..."
    echo ""
    
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
        --limit="$lines" \
        --format="table(timestamp,severity,textPayload)" \
        --project="$PROJECT_ID" 2>/dev/null || {
        print_error "Loglar alınamadı"
        print_info "Alternatif komut:"
        echo "  gcloud logging read \"resource.type=cloud_run_revision\" --limit=$lines --project=$PROJECT_ID"
    }
}

# =============================================================================
# 4. Hata Loglarını Filtreleme
# =============================================================================

view_error_logs() {
    print_header "🔴 Hata Logları (Son 30 satır)"
    
    print_info "Sadece ERROR ve CRITICAL seviyesindeki loglar gösteriliyor..."
    echo ""
    
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND (severity>=ERROR)" \
        --limit=30 \
        --format="table(timestamp,severity,textPayload)" \
        --project="$PROJECT_ID" 2>/dev/null || {
        print_error "Hata logları alınamadı"
    }
}

# =============================================================================
# 5. Servis Metrikleri
# =============================================================================

view_metrics() {
    print_header "📈 Servis Metrikleri"
    
    print_info "Son 1 saatlik metrikler görüntüleniyor..."
    echo ""
    
    # Request sayısı
    echo "📊 İstek Sayısı:"
    gcloud monitoring time-series list \
        --filter='metric.type="run.googleapis.com/request_count" AND resource.labels.service_name="'$SERVICE_NAME'"' \
        --interval=1h \
        --project="$PROJECT_ID" 2>/dev/null || print_warning "Metrikler alınamadı (Monitoring API etkin olmayabilir)"
    
    echo ""
    echo "💾 Memory Kullanımı:"
    gcloud monitoring time-series list \
        --filter='metric.type="run.googleapis.com/container/memory/utilizations" AND resource.labels.service_name="'$SERVICE_NAME'"' \
        --interval=1h \
        --project="$PROJECT_ID" 2>/dev/null || print_warning "Memory metrikleri alınamadı"
}

# =============================================================================
# 6. Environment Variables Kontrolü
# =============================================================================

check_env_vars() {
    print_header "🔧 Environment Variables"
    
    print_info "Cloud Run servisindeki environment variables:"
    echo ""
    
    gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="value(spec.template.spec.containers[0].env)" 2>/dev/null | \
        tr ';' '\n' | \
        sed 's/^/  /' || print_warning "Environment variables alınamadı"
}

# =============================================================================
# 7. Database Bağlantı Kontrolü (Cloud SQL)
# =============================================================================

check_database() {
    print_header "🗄️  Database Bağlantı Kontrolü"
    
    # Cloud SQL instance'larını listele
    print_info "Cloud SQL instance'ları:"
    gcloud sql instances list --format="table(name,region,databaseVersion,status)" 2>/dev/null || {
        print_warning "Cloud SQL instance bulunamadı veya erişim yok"
    }
    
    echo ""
    print_info "Cloud Run servisinin Cloud SQL bağlantıları:"
    gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="value(spec.template.spec.containers[0].env[?(@.name=='CLOUD_SQL_CONNECTION_NAME')].value)" 2>/dev/null || {
        print_warning "Cloud SQL bağlantı bilgisi bulunamadı"
    }
}

# =============================================================================
# 8. Deployment Hazırlık Kontrolü
# =============================================================================

check_deployment_readiness() {
    print_header "🔍 Deployment Hazırlık Kontrolü"
    
    # Proje dizininde miyiz?
    if [ ! -f "manage.py" ]; then
        print_error "manage.py bulunamadı. Lütfen proje kök dizininde çalıştırın."
        return 1
    fi
    
    print_success "Proje dizini doğrulandı"
    
    # Python versiyonu
    echo ""
    print_info "Python versiyonu:"
    python3 --version || print_error "Python bulunamadı"
    
    # Django kontrolü
    echo ""
    print_info "Django sistem kontrolleri:"
    python3 manage.py check --deploy 2>&1 | head -20 || print_warning "Django check başarısız"
    
    # Migration durumu
    echo ""
    print_info "Migration durumu:"
    python3 manage.py showmigrations --plan 2>&1 | grep -E "\[ \]|\[X\]" | tail -10 || print_warning "Migration bilgisi alınamadı"
}

# =============================================================================
# 9. Hızlı Diagnostic (Tüm Kontroller)
# =============================================================================

full_diagnostic() {
    print_header "🔬 Tam Diagnostic Raporu"
    
    check_project_status
    echo ""
    check_cloud_run_status
    echo ""
    check_env_vars
    echo ""
    check_database
    echo ""
    view_error_logs
    echo ""
    print_success "Diagnostic tamamlandı!"
}

# =============================================================================
# 10. Hızlı Komutlar Menüsü
# =============================================================================

show_menu() {
    print_header "🎯 FinAsis Cloud Shell Komutları"
    
    echo "Kullanım: ./cloud_shell_prompt.sh [komut]"
    echo ""
    echo "Mevcut komutlar:"
    echo "  status          - Proje ve servis durumu"
    echo "  logs            - Son logları görüntüle (varsayılan: 50 satır)"
    echo "  errors          - Hata loglarını görüntüle"
    echo "  metrics         - Servis metrikleri"
    echo "  env             - Environment variables"
    echo "  db              - Database bağlantı kontrolü"
    echo "  ready           - Deployment hazırlık kontrolü"
    echo "  diagnostic      - Tam diagnostic raporu"
    echo "  tail            - Canlı log takibi (tail -f benzeri)"
    echo ""
    echo "Örnekler:"
    echo "  ./cloud_shell_prompt.sh status"
    echo "  ./cloud_shell_prompt.sh logs 100"
    echo "  ./cloud_shell_prompt.sh diagnostic"
    echo ""
}

# =============================================================================
# 11. Canlı Log Takibi
# =============================================================================

tail_logs() {
    print_header "📺 Canlı Log Takibi (Ctrl+C ile çıkış)"
    
    print_info "Loglar canlı olarak görüntüleniyor..."
    echo ""
    
    gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
        --format="table(timestamp,severity,textPayload)" \
        --project="$PROJECT_ID" 2>/dev/null || {
        print_error "Canlı log takibi başlatılamadı"
    }
}

# =============================================================================
# Ana Menü
# =============================================================================

main() {
    case "${1:-menu}" in
        status)
            check_project_status
            check_cloud_run_status
            ;;
        logs)
            view_logs "${2:-50}"
            ;;
        errors)
            view_error_logs
            ;;
        metrics)
            view_metrics
            ;;
        env)
            check_env_vars
            ;;
        db)
            check_database
            ;;
        ready)
            check_deployment_readiness
            ;;
        diagnostic)
            full_diagnostic
            ;;
        tail)
            tail_logs
            ;;
        menu|help|--help|-h)
            show_menu
            ;;
        *)
            print_error "Bilinmeyen komut: $1"
            echo ""
            show_menu
            exit 1
            ;;
    esac
}

# Script çalıştırılıyor
main "$@"

