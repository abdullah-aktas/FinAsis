#!/bin/bash
set -e

# Renkli çıktı için ANSI renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonksiyonlar
function show_usage {
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${BLUE}   FinAsis - Canlı Ortamı Geri Alma Betiği      ${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo -e "Kullanım: $0 [YEDEK_TARIH] [SLACK_WEBHOOK_URL]"
    echo -e "YEDEK_TARIH formatı: YYYYMMDD_HHMMSS"
    echo -e "Örnek: $0 20230515_120000 https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"
    echo -e "${BLUE}=================================================${NC}"
}

function slack_notification {
    local message=$1
    local webhook_url=$2
    
    if [ -n "$webhook_url" ]; then
        curl -s -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $webhook_url > /dev/null
    fi
}

# Parametreleri kontrol et
if [ "$#" -lt 1 ]; then
    show_usage
    exit 1
fi

BACKUP_DATE=$1
SLACK_WEBHOOK=$2
BACKUP_DIR="backups"

# Başlık
echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}   FinAsis - Canlı Ortamı Geri Alma Betiği      ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "${YELLOW}UYARI: Bu işlem canlı ortamınızı belirtilen yedek ile değiştirecektir!${NC}"
echo -e "${YELLOW}Geri alma tarihi: $BACKUP_DATE${NC}"
read -p "Devam etmek istiyor musunuz? (e/h): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ee]$ ]]; then
    echo -e "${RED}Geri alma işlemi iptal edildi.${NC}"
    exit 1
fi

# Yedek dosyalarını kontrol et
BACKUP_FILE="$BACKUP_DIR/db_backup_$BACKUP_DATE.sql"
STATIC_BACKUP="$BACKUP_DIR/static_$BACKUP_DATE.tar.gz"
MEDIA_BACKUP="$BACKUP_DIR/media_$BACKUP_DATE.tar.gz"
SQLITE_BACKUP="$BACKUP_DIR/db.sqlite3.$BACKUP_DATE"

if [ -f "$BACKUP_FILE" ]; then
    echo -e "${GREEN}PostgreSQL yedek dosyası bulundu: $BACKUP_FILE${NC}"
    DB_TYPE="postgres"
elif [ -f "$SQLITE_BACKUP" ]; then
    echo -e "${GREEN}SQLite yedek dosyası bulundu: $SQLITE_BACKUP${NC}"
    DB_TYPE="sqlite"
else
    echo -e "${RED}Hata: Belirtilen tarih için veritabanı yedeği bulunamadı!${NC}"
    echo -e "${YELLOW}Mevcut yedekler: $(ls -l $BACKUP_DIR | grep db_backup)${NC}"
    exit 1
fi

# Bildirim gönder - başlangıç
if [ -n "$SLACK_WEBHOOK" ]; then
    slack_notification ":warning: *FinAsis Geri Alma İşlemi Başlatıldı*\nYedek Tarihi: $BACKUP_DATE" $SLACK_WEBHOOK
fi

# Canlı ortamı durdur
echo -e "${YELLOW}Canlı ortam konteynırları durduruluyor...${NC}"
docker-compose -f docker-compose.prod.yml down
echo -e "${GREEN}Konteynırlar durduruldu.${NC}"

# Veritabanını geri yükle
if [ "$DB_TYPE" = "postgres" ]; then
    echo -e "${YELLOW}PostgreSQL veritabanı geri yükleniyor...${NC}"
    source .env.prod
    
    # Veritabanını yeniden oluştur
    docker-compose -f docker-compose.prod.yml up -d db
    sleep 10 # Veritabanının başlaması için bekle
    
    docker-compose -f docker-compose.prod.yml exec db psql -U $DB_USER -c "DROP DATABASE IF EXISTS ${DB_NAME};"
    docker-compose -f docker-compose.prod.yml exec db psql -U $DB_USER -c "CREATE DATABASE ${DB_NAME};"
    
    # Yedekten geri yükle
    cat $BACKUP_FILE | docker-compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER -d $DB_NAME
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}PostgreSQL veritabanı başarıyla geri yüklendi.${NC}"
    else
        echo -e "${RED}PostgreSQL veritabanı geri yükleme başarısız!${NC}"
        if [ -n "$SLACK_WEBHOOK" ]; then
            slack_notification ":x: *Geri Alma Başarısız*\nPostgreSQL veritabanı geri yükleme işlemi başarısız oldu." $SLACK_WEBHOOK
        fi
        exit 1
    fi
else
    echo -e "${YELLOW}SQLite veritabanı geri yükleniyor...${NC}"
    if [ -f "db.sqlite3" ]; then
        cp "db.sqlite3" "db.sqlite3.current_backup"
        echo -e "${GREEN}Mevcut SQLite veritabanı yedeklendi: db.sqlite3.current_backup${NC}"
    fi
    cp "$SQLITE_BACKUP" "db.sqlite3"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}SQLite veritabanı başarıyla geri yüklendi.${NC}"
    else
        echo -e "${RED}SQLite veritabanı geri yükleme başarısız!${NC}"
        if [ -n "$SLACK_WEBHOOK" ]; then
            slack_notification ":x: *Geri Alma Başarısız*\nSQLite veritabanı geri yükleme işlemi başarısız oldu." $SLACK_WEBHOOK
        fi
        exit 1
    fi
fi

# Statik dosyaları geri yükle
if [ -f "$STATIC_BACKUP" ]; then
    echo -e "${YELLOW}Statik dosyalar geri yükleniyor...${NC}"
    rm -rf static
    mkdir -p static
    tar -xzf "$STATIC_BACKUP" -C .
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Statik dosyalar başarıyla geri yüklendi.${NC}"
    else
        echo -e "${RED}Statik dosyaları geri yükleme başarısız!${NC}"
    fi
fi

# Medya dosyaları geri yükle
if [ -f "$MEDIA_BACKUP" ]; then
    echo -e "${YELLOW}Medya dosyaları geri yükleniyor...${NC}"
    rm -rf media
    mkdir -p media
    tar -xzf "$MEDIA_BACKUP" -C .
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Medya dosyaları başarıyla geri yüklendi.${NC}"
    else
        echo -e "${RED}Medya dosyalarını geri yükleme başarısız!${NC}"
    fi
fi

# Konteynırları yeniden başlat
echo -e "${YELLOW}Konteynırlar yeniden başlatılıyor...${NC}"
docker-compose -f docker-compose.prod.yml up -d
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Konteynırlar başarıyla yeniden başlatıldı.${NC}"
else
    echo -e "${RED}Konteynırları yeniden başlatma başarısız!${NC}"
    if [ -n "$SLACK_WEBHOOK" ]; then
        slack_notification ":x: *Geri Alma Başarısız*\nKonteynırları yeniden başlatma işlemi başarısız oldu." $SLACK_WEBHOOK
    fi
    exit 1
fi

# Sağlık kontrolü
echo -e "${YELLOW}Sistem sağlık kontrolü yapılıyor...${NC}"
source .env.prod
DOMAIN_URL=${DOMAIN:-finasis.com.tr}
sleep 30  # Web servisinin tamamen başlaması için bekleyin

# curl ile web uygulamasına erişmeyi dene
if curl -s --head "http://localhost:8000/health/" | grep "200 OK" > /dev/null; then
    echo -e "${GREEN}Sağlık kontrolü başarılı!${NC}"
    if [ -n "$SLACK_WEBHOOK" ]; then
        slack_notification ":white_check_mark: *Geri Alma Başarılı*\nSistem başarıyla $BACKUP_DATE tarihli yedeğe geri alındı ve çalışıyor." $SLACK_WEBHOOK
    fi
else
    echo -e "${RED}Sağlık kontrolü başarısız! Web uygulaması yanıt vermiyor.${NC}"
    echo -e "${YELLOW}Web servis günlükleri kontrol ediliyor:${NC}"
    docker-compose -f docker-compose.prod.yml logs web
    if [ -n "$SLACK_WEBHOOK" ]; then
        slack_notification ":warning: *Geri Alma Tamamlandı, Ancak Sağlık Kontrolü Başarısız*\nLütfen manuel olarak kontrol edin." $SLACK_WEBHOOK
    fi
fi

# Tamamlandı
echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}   FinAsis başarıyla geri alındı!                ${NC}"
echo -e "${GREEN}=================================================${NC}"
echo -e "${BLUE}Web uygulaması: https://$DOMAIN_URL${NC}"
echo -e "${BLUE}Yönetim Paneli: https://$DOMAIN_URL/admin/${NC}"
echo -e "${BLUE}Grafana: https://grafana.$DOMAIN_URL${NC}"
echo -e "${BLUE}Prometheus: https://metrics.$DOMAIN_URL${NC}"
echo -e "${BLUE}Traefik Dashboard: https://traefik.$DOMAIN_URL${NC}"
echo -e "${BLUE}cAdvisor: https://cadvisor.$DOMAIN_URL${NC}"
echo -e "${GREEN}=================================================${NC}"

exit 0 