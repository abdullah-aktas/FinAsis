#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Renkli çıktı için ANSI renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Yapılandırma
CONFIG_FILE=".rollback.conf"
LOG_FILE="rollback.log"
BACKUP_DIR="backups"
TEMP_DIR="/tmp/finasis_rollback"
LOCK_FILE="/tmp/finasis_rollback.lock"
MAX_RETRY=3
HEALTH_CHECK_TIMEOUT=300

# Log fonksiyonu
log() {
    local level=$1
    shift
    local message=$@
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
    
    if [ "$level" = "ERROR" ]; then
        echo -e "${RED}$message${NC}"
    elif [ "$level" = "INFO" ]; then
        echo -e "${GREEN}$message${NC}"
    elif [ "$level" = "WARN" ]; then
        echo -e "${YELLOW}$message${NC}"
    fi
}

# Slack bildirimi gönderme
slack_notification() {
    local message=$1
    local webhook_url=$2
    local status=${3:-"info"}
    
    if [ -n "$webhook_url" ]; then
        local color
        case $status in
            "success") color="#36a64f" ;;
            "error") color="#ff0000" ;;
            "warning") color="#ffcc00" ;;
            *) color="#808080" ;;
        esac
        
        local payload=$(cat <<EOF
{
    "attachments": [
        {
            "color": "${color}",
            "title": "FinAsis Geri Alma İşlemi",
            "text": "${message}",
            "fields": [
                {
                    "title": "Ortam",
                    "value": "$(hostname)",
                    "short": true
                },
                {
                    "title": "Tarih",
                    "value": "$(date '+%Y-%m-%d %H:%M:%S')",
                    "short": true
                }
            ]
        }
    ]
}
EOF
)
        curl -s -X POST -H 'Content-type: application/json' --data "$payload" $webhook_url
    fi
}

# Temizlik işlemleri
cleanup() {
    log "INFO" "Temizlik işlemleri başlatılıyor..."
    rm -f "$LOCK_FILE"
    rm -rf "$TEMP_DIR"
}

# Hata yakalama
error_handler() {
    local line_no=$1
    local error_code=$2
    log "ERROR" "Satır $line_no'da hata oluştu (Kod: $error_code)"
    slack_notification "Geri alma işlemi sırasında hata oluştu: Satır $line_no (Kod: $error_code)" "$SLACK_WEBHOOK" "error"
    cleanup
    exit 1
}

trap 'error_handler ${LINENO} $?' ERR
trap cleanup EXIT

# Kullanım bilgisi
show_usage() {
    cat << EOF
${BLUE}=================================================${NC}
${BLUE}   FinAsis - Canlı Ortamı Geri Alma Betiği      ${NC}
${BLUE}=================================================${NC}

Kullanım: $0 [seçenekler] YEDEK_TARIH

Seçenekler:
    -h, --help              Bu yardım mesajını göster
    -s, --slack-webhook URL Slack webhook URL'si
    -f, --force            Onay istemeden devam et
    -v, --verbose          Detaylı çıktı göster
    -c, --config DOSYA     Özel yapılandırma dosyası kullan
    --dry-run              Simülasyon modu (gerçek değişiklik yapmaz)
    --skip-health-check    Sağlık kontrolünü atla
    
YEDEK_TARIH formatı: YYYYMMDD_HHMMSS
Örnek: $0 20230515_120000 -s https://hooks.slack.com/services/XXX/YYY/ZZZ

${BLUE}=================================================${NC}
EOF
}

# Parametre ayrıştırma
FORCE=0
VERBOSE=0
DRY_RUN=0
SKIP_HEALTH_CHECK=0

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -s|--slack-webhook)
            SLACK_WEBHOOK="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=1
            shift
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --skip-health-check)
            SKIP_HEALTH_CHECK=1
            shift
            ;;
        *)
            BACKUP_DATE="$1"
            shift
            ;;
    esac
done

# Kilit kontrolü
if [ -f "$LOCK_FILE" ]; then
    log "ERROR" "Başka bir geri alma işlemi devam ediyor. Lütfen bekleyin veya kilidi silin: $LOCK_FILE"
    exit 1
fi
touch "$LOCK_FILE"

# Yedek dosyalarını kontrol et
check_backup_files() {
    local backup_date=$1
    local files_ok=1
    
    declare -A backup_files=(
        ["postgres"]="$BACKUP_DIR/db_backup_$backup_date.sql"
        ["sqlite"]="$BACKUP_DIR/db.sqlite3.$backup_date"
        ["static"]="$BACKUP_DIR/static_$backup_date.tar.gz"
        ["media"]="$BACKUP_DIR/media_$backup_date.tar.gz"
        ["config"]="$BACKUP_DIR/config_$backup_date.tar.gz"
    )
    
    for type in "${!backup_files[@]}"; do
        local file="${backup_files[$type]}"
        if [ -f "$file" ]; then
            log "INFO" "$type yedek dosyası bulundu: $file"
            # Dosya bütünlüğü kontrolü
            if [ -f "$file.sha256" ]; then
                if sha256sum -c "$file.sha256" >/dev/null 2>&1; then
                    log "INFO" "$type yedek dosyası doğrulandı"
                else
                    log "ERROR" "$type yedek dosyası bozuk!"
                    files_ok=0
                fi
            fi
        elif [ "$type" = "postgres" ] && [ -f "${backup_files[sqlite]}" ]; then
            continue
        elif [ "$type" = "sqlite" ] && [ -f "${backup_files[postgres]}" ]; then
            continue
        else
            log "WARN" "$type yedek dosyası bulunamadı: $file"
            if [ "$type" = "config" ]; then
                log "WARN" "Yapılandırma yedeği olmadan devam ediliyor..."
            else
                files_ok=0
            fi
        fi
    done
    
    return $files_ok
}

# Veritabanı geri yükleme
restore_database() {
    local db_type=$1
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRY ]; do
        if [ "$db_type" = "postgres" ]; then
            log "INFO" "PostgreSQL veritabanı geri yükleniyor (Deneme: $((retry_count + 1)))"
            source .env.prod
            
            if [ $DRY_RUN -eq 0 ]; then
                docker-compose -f docker-compose.prod.yml up -d db
                sleep 10
                
                docker-compose -f docker-compose.prod.yml exec db psql -U $DB_USER -c "DROP DATABASE IF EXISTS ${DB_NAME};"
                docker-compose -f docker-compose.prod.yml exec db psql -U $DB_USER -c "CREATE DATABASE ${DB_NAME};"
                
                if cat $BACKUP_FILE | docker-compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER -d $DB_NAME; then
                    log "INFO" "PostgreSQL veritabanı başarıyla geri yüklendi"
                    return 0
                fi
            else
                log "INFO" "[DRY-RUN] PostgreSQL geri yükleme simüle edildi"
                return 0
            fi
        else
            log "INFO" "SQLite veritabanı geri yükleniyor (Deneme: $((retry_count + 1)))"
            if [ $DRY_RUN -eq 0 ]; then
                if [ -f "db.sqlite3" ]; then
                    cp "db.sqlite3" "db.sqlite3.current_backup"
                fi
                if cp "$SQLITE_BACKUP" "db.sqlite3"; then
                    log "INFO" "SQLite veritabanı başarıyla geri yüklendi"
                    return 0
                fi
            else
                log "INFO" "[DRY-RUN] SQLite geri yükleme simüle edildi"
                return 0
            fi
        fi
        
        retry_count=$((retry_count + 1))
        log "WARN" "Veritabanı geri yükleme başarısız. Yeniden deneniyor..."
        sleep 5
    done
    
    log "ERROR" "Veritabanı geri yükleme $MAX_RETRY denemeden sonra başarısız oldu"
    return 1
}

# Sağlık kontrolü
check_health() {
    local start_time=$(date +%s)
    local end_time=$((start_time + HEALTH_CHECK_TIMEOUT))
    
    log "INFO" "Sistem sağlık kontrolü başlatılıyor..."
    
    while [ $(date +%s) -lt $end_time ]; do
        if curl -s --head "http://localhost:8000/health/" | grep "200 OK" > /dev/null; then
            log "INFO" "Sağlık kontrolü başarılı!"
            return 0
        fi
        sleep 5
    done
    
    log "ERROR" "Sağlık kontrolü zaman aşımına uğradı"
    return 1
}

# Ana işlem
main() {
    log "INFO" "Geri alma işlemi başlatılıyor: $BACKUP_DATE"
    slack_notification "Geri alma işlemi başlatıldı: $BACKUP_DATE" "$SLACK_WEBHOOK" "info"
    
    # Yedek dosyalarını kontrol et
    if ! check_backup_files "$BACKUP_DATE"; then
        log "ERROR" "Gerekli yedek dosyaları eksik veya bozuk"
        exit 1
    fi
    
    # Kullanıcı onayı
    if [ $FORCE -eq 0 ] && [ $DRY_RUN -eq 0 ]; then
        read -p "Devam etmek istiyor musunuz? (e/h): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ee]$ ]]; then
            log "INFO" "İşlem kullanıcı tarafından iptal edildi"
            exit 0
        fi
    fi
    
    # Servisleri durdur
    log "INFO" "Servisler durduruluyor..."
    if [ $DRY_RUN -eq 0 ]; then
        docker-compose -f docker-compose.prod.yml down
    fi
    
    # Veritabanını geri yükle
    if [ -f "$BACKUP_FILE" ]; then
        restore_database "postgres" || exit 1
    else
        restore_database "sqlite" || exit 1
    fi
    
    # Statik ve medya dosyalarını geri yükle
    if [ -f "$STATIC_BACKUP" ]; then
        log "INFO" "Statik dosyalar geri yükleniyor..."
        if [ $DRY_RUN -eq 0 ]; then
            rm -rf static
            mkdir -p static
            tar -xzf "$STATIC_BACKUP" -C .
        fi
    fi
    
    if [ -f "$MEDIA_BACKUP" ]; then
        log "INFO" "Medya dosyaları geri yükleniyor..."
        if [ $DRY_RUN -eq 0 ]; then
            rm -rf media
            mkdir -p media
            tar -xzf "$MEDIA_BACKUP" -C .
        fi
    fi
    
    # Servisleri başlat
    log "INFO" "Servisler yeniden başlatılıyor..."
    if [ $DRY_RUN -eq 0 ]; then
        docker-compose -f docker-compose.prod.yml up -d
    fi
    
    # Sağlık kontrolü
    if [ $SKIP_HEALTH_CHECK -eq 0 ] && [ $DRY_RUN -eq 0 ]; then
        if ! check_health; then
            log "ERROR" "Sağlık kontrolü başarısız"
            slack_notification "Geri alma tamamlandı fakat sağlık kontrolü başarısız" "$SLACK_WEBHOOK" "warning"
            exit 1
        fi
    fi
    
    log "INFO" "Geri alma işlemi başarıyla tamamlandı"
    slack_notification "Geri alma işlemi başarıyla tamamlandı" "$SLACK_WEBHOOK" "success"
    
    # Özet bilgileri göster
    show_summary
}

# Özet bilgileri göster
show_summary() {
    source .env.prod
    DOMAIN_URL=${DOMAIN:-finasis.com.tr}
    
    cat << EOF
${GREEN}=================================================${NC}
${GREEN}   FinAsis başarıyla geri alındı!                ${NC}
${GREEN}=================================================${NC}
${BLUE}Web uygulaması: https://$DOMAIN_URL${NC}
${BLUE}Yönetim Paneli: https://$DOMAIN_URL/admin/${NC}
${BLUE}Grafana: https://grafana.$DOMAIN_URL${NC}
${BLUE}Prometheus: https://metrics.$DOMAIN_URL${NC}
${BLUE}Traefik Dashboard: https://traefik.$DOMAIN_URL${NC}
${BLUE}cAdvisor: https://cadvisor.$DOMAIN_URL${NC}
${GREEN}=================================================${NC}

Geri alma işlemi detayları için log dosyasını kontrol edin:
$LOG_FILE
EOF
}

# Ana programı başlat
main 