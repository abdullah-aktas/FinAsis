#!/bin/bash
# deploy.sh - FinAsis Üretim Ortamına Dağıtım Betiği
set -euo pipefail

# Renk tanımlamaları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Log dosyası
LOG_FILE="deploy_$(date +%Y%m%d_%H%M%S).log"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Log fonksiyonu
log() {
    local level=$1
    local message=$2
    echo -e "[$TIMESTAMP] [$level] $message" | tee -a "$LOG_FILE"
}

# Hata yönetimi
handle_error() {
    local error_code=$1
    local error_message=$2
    log "ERROR" "${RED}$error_message${NC}"
    exit $error_code
}

# Başlık yazdırma
print_header() {
    echo -e "\n${BLUE}=================================================${NC}"
    echo -e "${BLUE}   FinAsis - Üretim Ortamına Dağıtım Betiği      ${NC}"
    echo -e "${BLUE}=================================================${NC}\n"
}

# Bağımlılık kontrolü
check_dependencies() {
    log "INFO" "Bağımlılıklar kontrol ediliyor..."
    
    # Docker kontrolü
    if ! command -v docker &> /dev/null; then
        handle_error 1 "Docker yüklü değil!\nLütfen Docker'ı yükleyin:\n  curl -fsSL https://get.docker.com | sh"
    fi
    
    # Docker Compose kontrolü
    if ! command -v docker-compose &> /dev/null; then
        handle_error 1 "Docker Compose yüklü değil!\nLütfen Docker Compose'u yükleyin:\n  sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose\n  sudo chmod +x /usr/local/bin/docker-compose"
    fi
    
    # Sistem gereksinimleri
    log "INFO" "Sistem gereksinimleri kontrol ediliyor..."
    TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_MEM" -lt 4 ]; then
        log "WARNING" "${YELLOW}Uyarı: Sistem belleği 4GB'dan az! En az 4GB RAM önerilir.${NC}"
        read -p "Devam etmek istiyor musunuz? (e/h): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ee]$ ]]; then
            exit 1
        fi
    fi
    
    log "INFO" "${GREEN}✓ Tüm bağımlılıklar mevcut.${NC}"
}

# Yapılandırma kontrolü
check_config() {
    log "INFO" "Yapılandırma dosyaları kontrol ediliyor..."
    
    if [ ! -f ".env.prod" ]; then
        handle_error 1 ".env.prod dosyası bulunamadı!\nİpucu: .env.prod.example dosyasını .env.prod olarak kopyalayın ve düzenleyin."
    fi
    
    if [ ! -f "docker-compose.prod.yml" ]; then
        handle_error 1 "docker-compose.prod.yml dosyası bulunamadı!"
    fi
    
    log "INFO" "${GREEN}✓ Yapılandırma dosyaları mevcut.${NC}"
}

# Yedekleme işlemleri
perform_backup() {
    log "INFO" "Yedekleme işlemleri başlatılıyor..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Veritabanı yedekleme
    if [ -f "db.sqlite3" ]; then
        log "INFO" "SQLite veritabanı yedekleniyor..."
        cp db.sqlite3 "$BACKUP_DIR/db.sqlite3"
    else
        log "INFO" "PostgreSQL veritabanı yedekleniyor..."
        source .env.prod
        docker-compose exec db pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_DIR/db_backup.sql"
    fi
    
    # Dosya yedekleme
    log "INFO" "Statik ve medya dosyaları yedekleniyor..."
    [ -d "static" ] && tar -czf "$BACKUP_DIR/static.tar.gz" static
    [ -d "media" ] && tar -czf "$BACKUP_DIR/media.tar.gz" media
    
    log "INFO" "${GREEN}✓ Yedekleme tamamlandı: $BACKUP_DIR${NC}"
}

# Git kontrolü
check_git() {
    log "INFO" "Git durumu kontrol ediliyor..."
    
    if [ -d ".git" ]; then
        if [ -n "$(git status --porcelain)" ]; then
            log "WARNING" "${YELLOW}Kaydedilmemiş git değişiklikleri var!${NC}"
            git status
            read -p "Devam etmek istiyor musunuz? (e/h): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Ee]$ ]]; then
                exit 1
            fi
        else
            log "INFO" "${GREEN}✓ Git deposu temiz.${NC}"
        fi
    else
        log "WARNING" "${YELLOW}Bu dizin bir git deposu değil.${NC}"
    fi
}

# Docker işlemleri
handle_docker() {
    log "INFO" "Docker işlemleri başlatılıyor..."
    
    # Eski konteynırları temizle
    log "INFO" "Eski konteynırlar temizleniyor..."
    docker-compose -f docker-compose.prod.yml down --remove-orphans
    
    # İmajları oluştur
    log "INFO" "Docker imajları oluşturuluyor..."
    docker-compose -f docker-compose.prod.yml build --no-cache --pull
    
    # Konteynırları başlat
    log "INFO" "Konteynırlar başlatılıyor..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # Durum kontrolü
    sleep 10
    if [ "$(docker-compose -f docker-compose.prod.yml ps | grep -c "Up")" -gt 3 ]; then
        log "INFO" "${GREEN}✓ Konteynırlar başarıyla çalışıyor.${NC}"
    else
        log "ERROR" "${RED}Bazı konteynırlar başlatılamadı!${NC}"
        docker-compose -f docker-compose.prod.yml logs
        handle_error 1 "Konteynır başlatma hatası!"
    fi
}

# Sağlık kontrolü
perform_health_check() {
    log "INFO" "Sistem sağlık kontrolü yapılıyor..."
    
    source .env.prod
    DOMAIN_URL=${DOMAIN:-finasis.com.tr}
    
    # Web uygulaması kontrolü
    if ! curl -s --head "http://localhost:8000/health/" | grep "200 OK" > /dev/null; then
        log "ERROR" "${RED}Web uygulaması yanıt vermiyor!${NC}"
        docker-compose -f docker-compose.prod.yml logs web
        handle_error 1 "Sağlık kontrolü başarısız!"
    fi
    
    # Veritabanı kontrolü
    if ! docker-compose -f docker-compose.prod.yml exec db pg_isready -U "$DB_USER" -d "$DB_NAME"; then
        log "ERROR" "${RED}Veritabanı bağlantısı başarısız!${NC}"
        handle_error 1 "Veritabanı kontrolü başarısız!"
    fi
    
    log "INFO" "${GREEN}✓ Sağlık kontrolü başarılı.${NC}"
}

# Ana fonksiyon
main() {
    print_header
    check_dependencies
    check_config
    perform_backup
    check_git
    handle_docker
    perform_health_check
    
    # Başarılı dağıtım bilgileri
    log "INFO" "\n${GREEN}=================================================${NC}"
    log "INFO" "${GREEN}   FinAsis başarıyla dağıtıldı!                  ${NC}"
    log "INFO" "${GREEN}=================================================${NC}"
    log "INFO" "${BLUE}Web uygulaması: https://$DOMAIN_URL${NC}"
    log "INFO" "${BLUE}Yönetim Paneli: https://$DOMAIN_URL/admin/${NC}"
    log "INFO" "${BLUE}Grafana: https://grafana.$DOMAIN_URL${NC}"
    log "INFO" "${BLUE}Prometheus: https://metrics.$DOMAIN_URL${NC}"
    log "INFO" "${BLUE}Traefik Dashboard: https://traefik.$DOMAIN_URL${NC}"
    log "INFO" "${BLUE}cAdvisor: https://cadvisor.$DOMAIN_URL${NC}"
    log "INFO" "${GREEN}=================================================${NC}"
}

# Betiği çalıştır
main "$@" 