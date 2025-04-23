#!/bin/bash

# FinAsis rollback script
# Kullanım: ./rollback.sh [YEDEK_TARIH] [SLACK_WEBHOOK_URL (opsiyonel)]
# Örnek: ./rollback.sh 20231225_120000 https://hooks.slack.com/services/xxx/xxx/xxx

set -euo pipefail
IFS=$'\n\t'

# Renk tanımları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Sabitler
MAX_RETRIES=6
RETRY_DELAY=10
HEALTH_CHECK_TIMEOUT=60
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="backups"
LOG_DIR="logs"
ROLLBACK_LOG="$LOG_DIR/rollback_$(date +%Y%m%d_%H%M%S).log"

# Dizinleri oluştur
mkdir -p "$BACKUP_DIR" "$LOG_DIR"

# Fonksiyonlar
log_info() {
    local message="$1"
    echo -e "${BLUE}[BİLGİ]${NC} $message" | tee -a "$ROLLBACK_LOG"
}

log_success() {
    local message="$1"
    echo -e "${GREEN}[BAŞARILI]${NC} $message" | tee -a "$ROLLBACK_LOG"
}

log_warning() {
    local message="$1"
    echo -e "${YELLOW}[UYARI]${NC} $message" | tee -a "$ROLLBACK_LOG"
}

log_error() {
    local message="$1"
    echo -e "${RED}[HATA]${NC} $message" | tee -a "$ROLLBACK_LOG"
}

# Hata yakalama
trap 'handle_error $LINENO' ERR

handle_error() {
    local line=$1
    log_error "Hata oluştu (Satır: $line)"
    send_slack_notification "error" "Rollback işlemi sırasında beklenmeyen bir hata oluştu (Satır: $line)"
    exit 1
}

# Parametreleri al
BACKUP_DATE=${1:-$(ls -t "$BACKUP_DIR"/backup_*.sql | head -n1 | sed 's/.*backup_\(.*\).sql/\1/')}
SLACK_WEBHOOK_URL=${2:-}

# Ortam değişkenlerini yükle
if [ -f ".env" ]; then
    log_info "Ortam değişkenleri .env dosyasından yükleniyor..."
    set -a
    source .env
    set +a
else
    log_warning ".env dosyası bulunamadı, devam edilecek..."
fi

# Slack'e bildirim gönderme fonksiyonu
send_slack_notification() {
    local status=$1
    local message=$2
    
    if [ -z "$SLACK_WEBHOOK_URL" ]; then
        log_warning "Slack webhook URL'si belirtilmediği için bildirim gönderilmiyor."
        return 0
    fi
    
    local emoji="❌"
    local color="#FF0000"
    
    case "$status" in
        "success")
            emoji="✅"
            color="#36a64f"
            ;;
        "warning")
            emoji="⚠️"
            color="#FFA500"
            ;;
    esac
    
    local payload="{
        \"attachments\": [
            {
                \"color\": \"$color\",
                \"title\": \"$emoji FinAsis Rollback Bildirimi\",
                \"text\": \"$message\",
                \"fields\": [
                    {
                        \"title\": \"Yedek Tarihi\",
                        \"value\": \"$BACKUP_DATE\",
                        \"short\": true
                    },
                    {
                        \"title\": \"Sunucu\",
                        \"value\": \"$(hostname)\",
                        \"short\": true
                    },
                    {
                        \"title\": \"Kullanıcı\",
                        \"value\": \"$(whoami)\",
                        \"short\": true
                    },
                    {
                        \"title\": \"Log Dosyası\",
                        \"value\": \"$ROLLBACK_LOG\",
                        \"short\": false
                    }
                ],
                \"footer\": \"FinAsis Teknik Operasyon Ekibi\",
                \"ts\": $(date +%s)
            }
        ]
    }"
    
    if curl -s -X POST -H 'Content-type: application/json' --data "$payload" "$SLACK_WEBHOOK_URL" > /dev/null; then
        log_success "Slack bildirimi gönderildi."
    else
        log_error "Slack bildirimi gönderilemedi."
    fi
}

# Yedek dosyasının varlığını kontrol et
BACKUP_FILE="$BACKUP_DIR/backup_${BACKUP_DATE}.sql"
if [ ! -f "$BACKUP_FILE" ]; then
    log_error "Belirtilen yedek dosyası bulunamadı: $BACKUP_FILE"
    send_slack_notification "error" "Rollback başarısız! Belirtilen yedek dosyası ($BACKUP_FILE) bulunamadı."
    exit 1
fi

# Önceki durumu yedekle
log_info "Mevcut durumun yedeği alınıyor..."
CURRENT_BACKUP="$BACKUP_DIR/backup_before_rollback_$(date +%Y%m%d_%H%M%S).sql"
if ! docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db pg_dump -U "$DB_USER" "$DB_NAME" > "$CURRENT_BACKUP"; then
    log_warning "Mevcut durumun yedeğini alırken bir sorun oluştu, rollback işlemine devam ediliyor..."
    send_slack_notification "warning" "Mevcut durumun yedeğini alırken bir sorun oluştu, rollback işlemine devam ediliyor. ⚠️"
else
    log_success "Mevcut durum yedeği alındı: $CURRENT_BACKUP"
fi

# Docker image'ı etiketleme
PREVIOUS_IMAGE=$(docker images | grep finasis | grep -v latest | head -n1 | awk '{print $1":"$2}')
if [ -n "$PREVIOUS_IMAGE" ]; then
    log_info "Önceki Docker image: $PREVIOUS_IMAGE"
    docker tag "$PREVIOUS_IMAGE" finasis:rollback
    docker tag "$PREVIOUS_IMAGE" finasis:latest
    log_success "Docker image etiketlendi."
else
    log_warning "Önceki Docker image bulunamadı, rollback için mevcut image kullanılacak..."
    send_slack_notification "warning" "Önceki Docker image bulunamadı, rollback için mevcut image kullanılacak. ⚠️"
fi

# Servisleri durdur
log_info "Servisler durduruluyor..."
docker-compose -f "$DOCKER_COMPOSE_FILE" down

# Veritabanını geri yükle
log_info "Veritabanı geri yükleniyor: $BACKUP_FILE"
docker-compose -f "$DOCKER_COMPOSE_FILE" up -d db

# Veritabanının başlamasını bekle
log_info "Veritabanının başlaması bekleniyor..."
for i in $(seq 1 $MAX_RETRIES); do
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db pg_isready -U "$DB_USER" -d "$DB_NAME"; then
        log_success "Veritabanı başlatıldı."
        break
    fi
    if [ $i -eq $MAX_RETRIES ]; then
        log_error "Veritabanı başlatılamadı!"
        send_slack_notification "error" "Veritabanı başlatılamadı! Teknik ekiple iletişime geçiniz."
        exit 1
    fi
    log_warning "Deneme $i başarısız, $RETRY_DELAY saniye bekleniyor..."
    sleep $RETRY_DELAY
done

# Veritabanını temizle ve geri yükle
log_info "Veritabanı temizleniyor..."
if ! docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db psql -U "$DB_USER" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" "$DB_NAME"; then
    log_error "Veritabanı temizleme başarısız!"
    send_slack_notification "error" "Veritabanı temizleme başarısız! Teknik ekiple iletişime geçiniz."
    exit 1
fi

log_info "Veritabanı geri yükleniyor..."
if ! docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db psql -U "$DB_USER" "$DB_NAME" < "$BACKUP_FILE"; then
    log_error "Veritabanı geri yükleme başarısız!"
    send_slack_notification "error" "Veritabanı geri yükleme başarısız! Teknik ekiple iletişime geçiniz."
    exit 1
else
    log_success "Veritabanı geri yüklendi."
fi

# Servisleri başlat
log_info "Servisler yeniden başlatılıyor..."
docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

# Sağlık kontrolü
log_info "Sağlık kontrolü yapılıyor..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -s -f --max-time $HEALTH_CHECK_TIMEOUT http://localhost:8000/health/ > /dev/null; then
        log_success "Sağlık kontrolü başarılı!"
        send_slack_notification "success" "Rollback işlemi başarıyla tamamlandı. Sistem $BACKUP_DATE tarihindeki durumuna geri döndürüldü."
        exit 0
    fi
    log_warning "Deneme $i başarısız, $RETRY_DELAY saniye bekleniyor..."
    sleep $RETRY_DELAY
done

log_error "Sağlık kontrolü başarısız! Servisler düzgün çalışmıyor olabilir."
send_slack_notification "error" "Rollback işlemi tamamlandı ancak sağlık kontrolü başarısız! Servisler düzgün çalışmıyor olabilir."
exit 1 