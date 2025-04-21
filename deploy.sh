#!/bin/bash
set -e

# Renkli çıktı için ANSI renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Başlık
echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}   FinAsis - Üretim Ortamına Dağıtım Betiği      ${NC}"
echo -e "${BLUE}=================================================${NC}"

# Yapılandırma dosyasını kontrol et
if [ ! -f ".env.prod" ]; then
    echo -e "${RED}Hata: .env.prod dosyası bulunamadı!${NC}"
    echo -e "${YELLOW}İpucu: .env.prod.example dosyasını .env.prod olarak kopyalayın ve düzenleyin.${NC}"
    exit 1
fi

# Docker ve Docker Compose varlığını kontrol et
if ! [ -x "$(command -v docker)" ]; then
  echo -e "${RED}Hata: Docker yüklü değil.${NC}" >&2
  exit 1
fi

if ! [ -x "$(command -v docker-compose)" ]; then
  echo -e "${RED}Hata: Docker Compose yüklü değil.${NC}" >&2
  exit 1
fi

# Sistem gereksinimleri kontrolü
echo -e "${YELLOW}Sistem gereksinimleri kontrol ediliyor...${NC}"
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
if [ $TOTAL_MEM -lt 4 ]; then
    echo -e "${RED}Uyarı: Sistem belleği 4GB'dan az! En az 4GB RAM önerilir.${NC}"
    read -p "Devam etmek istiyor musunuz? (e/h): " -n 1 -r
    echo    
    if [[ ! $REPLY =~ ^[Ee]$ ]]; then
        exit 1
    fi
fi

# Yedekleme
echo -e "${YELLOW}Veritabanı yedekleniyor...${NC}"
BACKUP_DIR="backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

if [ -f "db.sqlite3" ]; then
    echo -e "${GREEN}SQLite veritabanı yedekleniyor...${NC}"
    cp db.sqlite3 "$BACKUP_DIR/db.sqlite3.$TIMESTAMP"
    echo -e "${GREEN}SQLite veritabanı yedeklendi: $BACKUP_DIR/db.sqlite3.$TIMESTAMP${NC}"
else
    echo -e "${YELLOW}PostgreSQL veritabanı yedekleniyor...${NC}"
    # PostgreSQL yedekleme - Docker Compose kullanıyor
    source .env.prod
    docker-compose exec db pg_dump -U $DB_USER -d $DB_NAME > $BACKUP_FILE
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}PostgreSQL veritabanı yedeklendi: $BACKUP_FILE${NC}"
    else
        echo -e "${RED}PostgreSQL veritabanı yedeklenemedi!${NC}"
        exit 1
    fi
fi

# Statik dosyaları ve medya dosyalarını yedekle
echo -e "${YELLOW}Statik ve medya dosyaları yedekleniyor...${NC}"
if [ -d "static" ]; then
    tar -czf "$BACKUP_DIR/static_$TIMESTAMP.tar.gz" static
    echo -e "${GREEN}Statik dosyalar yedeklendi: $BACKUP_DIR/static_$TIMESTAMP.tar.gz${NC}"
fi

if [ -d "media" ]; then
    tar -czf "$BACKUP_DIR/media_$TIMESTAMP.tar.gz" media
    echo -e "${GREEN}Medya dosyaları yedeklendi: $BACKUP_DIR/media_$TIMESTAMP.tar.gz${NC}"
fi

# Git değişikliklerini kontrol et
echo -e "${YELLOW}Git değişiklikleri kontrol ediliyor...${NC}"
if [ -d ".git" ]; then
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${RED}Uyarı: Kaydedilmemiş git değişiklikleri var!${NC}"
        git status
        read -p "Devam etmek istiyor musunuz? (e/h): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ee]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}Git deposu temiz.${NC}"
    fi
else
    echo -e "${YELLOW}Bu dizin bir git deposu değil.${NC}"
fi

# Docker imajlarını oluştur ve başlat
echo -e "${YELLOW}Docker imajları oluşturuluyor ve konteynırlar başlatılıyor...${NC}"
docker-compose -f docker-compose.prod.yml down --remove-orphans
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Kurulum durumunu kontrol et
echo -e "${YELLOW}Kurulum durumu kontrol ediliyor...${NC}"
sleep 10  # Servislerin başlaması için bekleyin
if [ $(docker-compose -f docker-compose.prod.yml ps | grep -c "Up") -gt 3 ]; then
    echo -e "${GREEN}Konteynırlar başarıyla çalışıyor:${NC}"
    docker-compose -f docker-compose.prod.yml ps
else
    echo -e "${RED}Bazı konteynırlar başlatılamadı!${NC}"
    docker-compose -f docker-compose.prod.yml ps
    echo -e "${YELLOW}Hata günlükleri kontrol ediliyor:${NC}"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi

# Sağlık kontrolü
echo -e "${YELLOW}Sistem sağlık kontrolü yapılıyor...${NC}"
source .env.prod
DOMAIN_URL=${DOMAIN:-finasis.com.tr}
sleep 10  # Web servisinin tamamen başlaması için bekleyin

# curl ile web uygulamasına erişmeyi dene
if curl -s --head "http://localhost:8000/health/" | grep "200 OK" > /dev/null; then
    echo -e "${GREEN}Sağlık kontrolü başarılı!${NC}"
else
    echo -e "${RED}Sağlık kontrolü başarısız! Web uygulaması yanıt vermiyor.${NC}"
    echo -e "${YELLOW}Web servis günlükleri kontrol ediliyor:${NC}"
    docker-compose -f docker-compose.prod.yml logs web
    echo -e "${YELLOW}Devam etmek istiyor musunuz? (e/h):${NC}"
    read -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ee]$ ]]; then
        echo -e "${YELLOW}Dağıtım iptal ediliyor...${NC}"
        exit 1
    fi
fi

# Tamamlandı
echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}   FinAsis başarıyla dağıtıldı!                  ${NC}"
echo -e "${GREEN}=================================================${NC}"
echo -e "${BLUE}Web uygulaması: https://$DOMAIN_URL${NC}"
echo -e "${BLUE}Yönetim Paneli: https://$DOMAIN_URL/admin/${NC}"
echo -e "${BLUE}Grafana: https://grafana.$DOMAIN_URL${NC}"
echo -e "${BLUE}Prometheus: https://metrics.$DOMAIN_URL${NC}"
echo -e "${BLUE}Traefik Dashboard: https://traefik.$DOMAIN_URL${NC}"
echo -e "${BLUE}cAdvisor: https://cadvisor.$DOMAIN_URL${NC}"
echo -e "${GREEN}=================================================${NC}"

exit 0 