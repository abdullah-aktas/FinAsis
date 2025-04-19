#!/bin/bash

# FinAsis rollback script
# Kullanım: ./rollback.sh [YEDEK_TARIH] [SLACK_WEBHOOK_URL (opsiyonel)]
# Örnek: ./rollback.sh 20231225_120000 https://hooks.slack.com/services/xxx/xxx/xxx

set -e

# Renk tanımları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parametreleri al
BACKUP_DATE=${1:-$(ls -t backup_*.sql | head -n1 | sed 's/backup_\(.*\).sql/\1/')}
SLACK_WEBHOOK_URL=$2

# Ortam değişkenlerini yükle
if [ -f ".env" ]; then
    echo -e "${BLUE}[BİLGİ]${NC} Ortam değişkenleri .env dosyasından yükleniyor..."
    source .env
else
    echo -e "${YELLOW}[UYARI]${NC} .env dosyası bulunamadı, devam edilecek..."
fi

# Slack'e bildirim gönderme fonksiyonu
send_slack_notification() {
    local status=$1
    local message=$2
    
    # Webhook URL kontrol et
    if [ -z "$SLACK_WEBHOOK_URL" ]; then
        echo -e "${YELLOW}[UYARI]${NC} Slack webhook URL'si belirtilmediği için bildirim gönderilmiyor."
        return 0
    fi
    
    # Emojileri ve renkleri ayarla
    local emoji="❌"
    local color="#FF0000"
    
    if [ "$status" == "success" ]; then
        emoji="✅"
        color="#36a64f"
    elif [ "$status" == "warning" ]; then
        emoji="⚠️"
        color="#FFA500"
    fi
    
    # Slack payload
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
                    }
                ],
                \"footer\": \"FinAsis Teknik Operasyon Ekibi\",
                \"ts\": $(date +%s)
            }
        ]
    }"
    
    # Slack'e gönder
    curl -s -X POST -H 'Content-type: application/json' --data "$payload" $SLACK_WEBHOOK_URL > /dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[BAŞARILI]${NC} Slack bildirimi gönderildi."
    else
        echo -e "${RED}[HATA]${NC} Slack bildirimi gönderilemedi."
    fi
}

echo -e "${BLUE}[BİLGİ]${NC} FinAsis rollback işlemi başlatılıyor..."
echo -e "${BLUE}[BİLGİ]${NC} Kullanılacak yedek tarihi: $BACKUP_DATE"

# Yedek dosyasının varlığını kontrol et
BACKUP_FILE="backup_${BACKUP_DATE}.sql"
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}[HATA]${NC} Belirtilen yedek dosyası bulunamadı: $BACKUP_FILE"
    send_slack_notification "error" "Rollback başarısız! Belirtilen yedek dosyası ($BACKUP_FILE) bulunamadı."
    exit 1
fi

# Önceki durumu yedekle
echo -e "${BLUE}[BİLGİ]${NC} Mevcut durumun yedeği alınıyor..."
CURRENT_BACKUP="backup_before_rollback_$(date +%Y%m%d_%H%M%S).sql"
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U $DB_USER $DB_NAME > $CURRENT_BACKUP

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[UYARI]${NC} Mevcut durumun yedeğini alırken bir sorun oluştu, rollback işlemine devam ediliyor..."
    send_slack_notification "warning" "Mevcut durumun yedeğini alırken bir sorun oluştu, rollback işlemine devam ediliyor. ⚠️"
else
    echo -e "${GREEN}[BAŞARILI]${NC} Mevcut durum yedeği alındı: $CURRENT_BACKUP"
fi

# Docker image'ı etiketleme
PREVIOUS_IMAGE=$(docker images | grep finasis | grep -v latest | head -n1 | awk '{print $1":"$2}')
if [ -n "$PREVIOUS_IMAGE" ]; then
    echo -e "${BLUE}[BİLGİ]${NC} Önceki Docker image: $PREVIOUS_IMAGE"
    docker tag $PREVIOUS_IMAGE finasis:rollback
    docker tag $PREVIOUS_IMAGE finasis:latest
    echo -e "${GREEN}[BAŞARILI]${NC} Docker image etiketlendi."
else
    echo -e "${YELLOW}[UYARI]${NC} Önceki Docker image bulunamadı, rollback için mevcut image kullanılacak..."
    send_slack_notification "warning" "Önceki Docker image bulunamadı, rollback için mevcut image kullanılacak. ⚠️"
fi

# Servisleri durdur
echo -e "${BLUE}[BİLGİ]${NC} Servisler durduruluyor..."
docker-compose -f docker-compose.prod.yml down

# Veritabanını geri yükle
echo -e "${BLUE}[BİLGİ]${NC} Veritabanı geri yükleniyor: $BACKUP_FILE"
docker-compose -f docker-compose.prod.yml up -d db
sleep 10 # Veritabanının başlamasını bekliyoruz

# Veritabanını temizle ve geri yükle
docker-compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" $DB_NAME
docker-compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER $DB_NAME < $BACKUP_FILE

if [ $? -ne 0 ]; then
    echo -e "${RED}[HATA]${NC} Veritabanı geri yükleme başarısız!"
    send_slack_notification "error" "Veritabanı geri yükleme başarısız! Teknik ekiple iletişime geçiniz."
    exit 1
else
    echo -e "${GREEN}[BAŞARILI]${NC} Veritabanı geri yüklendi."
fi

# Servisleri başlat
echo -e "${BLUE}[BİLGİ]${NC} Servisler yeniden başlatılıyor..."
docker-compose -f docker-compose.prod.yml up -d

# Sağlık kontrolü
echo -e "${BLUE}[BİLGİ]${NC} Sağlık kontrolü yapılıyor..."
for i in {1..6}; do
    if curl -s -f http://localhost:8000/health/ > /dev/null; then
        echo -e "${GREEN}[BAŞARILI]${NC} Sağlık kontrolü başarılı!"
        send_slack_notification "success" "Rollback işlemi başarıyla tamamlandı. Sistem $BACKUP_DATE tarihindeki durumuna geri döndürüldü."
        exit 0
    fi
    echo -e "${YELLOW}[UYARI]${NC} Deneme $i başarısız, 10 saniye bekleniyor..."
    sleep 10
done

echo -e "${RED}[HATA]${NC} Sağlık kontrolü başarısız! Servisler düzgün çalışmıyor olabilir."
send_slack_notification "error" "Rollback işlemi tamamlandı ancak sağlık kontrolü başarısız! Servisler düzgün çalışmıyor olabilir."
exit 1 