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
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S"

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

# Deployment öncesi kontrol listesi
pre_deploy_checks() {
    log "INFO" "Deployment öncesi kontroller yapılıyor..."
    
    # Debug kontrolü
    if grep -q "DEBUG = True" config/settings/production.py; then
        handle_error 1 "DEBUG modu açık! Lütfen production.py'da DEBUG = False olarak ayarlayın."
    fi
    
    # Güvenlik kontrolleri
    if ! grep -q "SECURE_SSL_REDIRECT = True" config/settings/production.py; then
        log "WARNING" "${YELLOW}SSL yönlendirme kapalı. Güvenlik için açmanız önerilir.${NC}"
    fi
    
    # Veritabanı bağlantı kontrolü 
    if ! docker-compose -f docker-compose.prod.yml exec db pg_isready &>/dev/null; then
        handle_error 1 "Veritabanı bağlantısı başarısız!"
    fi

    # Disk alanı kontrolü
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 80 ]; then
        log "WARNING" "${YELLOW}Disk kullanımı %80'in üzerinde! (%$DISK_USAGE)${NC}"
    fi

    log "INFO" "${GREEN}✓ Ön kontroller başarılı.${NC}"
}

# Git başlatma ve yapılandırma
git init
git add .
git commit -m "Initial commit"

# Remote repo ekleme
git remote add origin https://github.com/abdullah-aktas/FinAsis.git
git branch -M main
git push -u origin main

# Ana fonksiyon
main() {
    print_header
    check_dependencies
    check_config
    pre_deploy_checks    # Yeni eklenen kontrol
    perform_backup
    check_git
    handle_docker
    perform_migrations   # Yeni eklenen migrasyon işlemi
    perform_health_check
    
    log "INFO" "\n${GREEN}=================================================${NC}"
    log "INFO" "${GREEN}   FinAsis başarıyla dağıtıldı!                  ${NC}"
    log "INFO" "${GREEN}=================================================${NC}"
    
    # Gerekli bilgileri görüntüle
    display_info
}

# Migrasyon işlemleri için yeni fonksiyon
perform_migrations() {
    log "INFO" "Veritabanı migrasyonları uygulanıyor..."
    
    if ! docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput; then
        handle_error 1 "Migrasyon işlemi başarısız!"
    fi
    
    if ! docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput; then
        handle_error 1 "Statik dosya toplama işlemi başarısız!"
    fi
    
    log "INFO" "${GREEN}✓ Migrasyonlar başarıyla uygulandı.${NC}"
}

# Bilgileri görüntülemek için yeni fonksiyon
display_info() {
    source .env.prod
    DOMAIN_URL=${DOMAIN:-finasis.com.tr}
    
    log "INFO" "${BLUE}Web uygulaması: https://$DOMAIN_URL${NC}"
    log "INFO" "${BLUE}Yönetim Paneli: https://$DOMAIN_URL/admin/${NC}"
    log "INFO" "${BLUE}API Dokümantasyonu: https://$DOMAIN_URL/api/docs/${NC}"
    log "INFO" "${BLUE}Sağlık Durumu: https://$DOMAIN_URL/health/${NC}"
    log "INFO" "${BLUE}Metrics: https://$DOMAIN_URL/metrics/${NC}"
    log "INFO" "${GREEN}=================================================${NC}"
    
    # Log dosyası konumu
    log "INFO" "Detaylı log dosyası: $LOG_FILE"
}

# Betiği çalıştır
main "$@"
#!/bin/bash

echo "🚀 FinAsis Tüm Modüller Yayına Alınıyor..."

# 1. Ortam Değişkenlerini Yükle
echo "🔐 Ortam değişkenleri yükleniyor..."
export $(cat .env.prod | xargs)

# 2. Migration işlemleri
echo "📂 Migration işlemleri başlatılıyor..."
python manage.py makemigrations --settings=finasis.settings.prod
python manage.py migrate --settings=finasis.settings.prod

# 3. Statik dosyalar
echo "🧱 Statik dosyalar toplanıyor..."
python manage.py collectstatic --noinput --settings=finasis.settings.prod

# 4. Servisleri yeniden başlat
echo "♻️ Gunicorn ve Nginx yeniden başlatılıyor..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 5. SMTP Testi
echo "📧 E-posta gönderim testi yapılıyor..."
python manage.py sendtestemail your_email@example.com --settings=finasis.settings.prod

# 6. Canlı log izleme (opsiyonel)
echo "📜 Son 20 log satırı:"
journalctl -u finasis -n 20 --no-pager

# 7. Uygunluk Testi (HTTP response kodu beklenir)
echo "🧪 Sağlık kontrolü yapılıyor..."
curl -I https://finasis.com.tr

echo "✅ FinAsis tüm modüllerle birlikte başarıyla yayına alındı!"
echo "🔗 Web uygulaması: https://finasis.com.tr"