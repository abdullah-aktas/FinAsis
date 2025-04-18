#!/bin/bash
# PostgreSQL Kurulum ve Ayarlama Scripti

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== FinAsis PostgreSQL Kurulum ve Ayarlama Scripti =====${NC}"

# 1. PostgreSQL kurulumunu kontrol et
echo -e "\n${YELLOW}PostgreSQL kurulumu kontrol ediliyor...${NC}"
if command -v psql >/dev/null 2>&1; then
    echo -e "${GREEN}PostgreSQL zaten kurulu.${NC}"
else
    echo -e "${RED}PostgreSQL kurulu değil.${NC}"
    echo -e "${YELLOW}PostgreSQL kurulumu yapılıyor...${NC}"
    
    # İşletim sistemini algıla
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Debian/Ubuntu
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update
            sudo apt-get install -y postgresql postgresql-contrib
        # RHEL/CentOS/Fedora
        elif command -v dnf >/dev/null 2>&1; then
            sudo dnf install -y postgresql postgresql-server
            sudo postgresql-setup --initdb
            sudo systemctl enable postgresql
            sudo systemctl start postgresql
        else
            echo -e "${RED}Desteklenmeyen Linux dağıtımı. Lütfen PostgreSQL'i manuel olarak kurun.${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew >/dev/null 2>&1; then
            brew install postgresql
            brew services start postgresql
        else
            echo -e "${RED}Homebrew kurulu değil. Lütfen önce Homebrew'i kurun.${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows
        echo -e "${RED}Windows için otomatik kurulum desteklenmiyor. Lütfen https://www.postgresql.org/download/windows/ adresinden manuel olarak kurun.${NC}"
        exit 1
    else
        echo -e "${RED}Desteklenmeyen işletim sistemi.${NC}"
        exit 1
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}PostgreSQL başarıyla kuruldu.${NC}"
    else
        echo -e "${RED}PostgreSQL kurulumu başarısız oldu.${NC}"
        exit 1
    fi
fi

# 2. .env dosyasını kontrol et ve oluştur
echo -e "\n${YELLOW}.env dosyası kontrol ediliyor...${NC}"
if [ -f .env ]; then
    echo -e "${GREEN}.env dosyası zaten mevcut.${NC}"
else
    echo -e "${YELLOW}.env dosyası oluşturuluyor...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}.env dosyası .env.example'dan kopyalandı.${NC}"
    else
        echo -e "${RED}.env.example dosyası bulunamadı. Lütfen manuel olarak bir .env dosyası oluşturun.${NC}"
        exit 1
    fi
fi

# 3. .env dosyasından veritabanı bilgilerini oku
echo -e "\n${YELLOW}Veritabanı bilgileri okunuyor...${NC}"
if [ -f .env ]; then
    # .env dosyasını oku ve değişkenleri ayarla
    source .env
    DB_NAME=${DB_NAME:-finasis}
    DB_USER=${DB_USER:-postgres}
    DB_PASSWORD=${DB_PASSWORD:-postgres}
    DB_HOST=${DB_HOST:-localhost}
    DB_PORT=${DB_PORT:-5432}
    
    echo -e "Veritabanı: ${GREEN}${DB_NAME}${NC}"
    echo -e "Kullanıcı: ${GREEN}${DB_USER}${NC}"
    echo -e "Host: ${GREEN}${DB_HOST}${NC}"
    echo -e "Port: ${GREEN}${DB_PORT}${NC}"
else
    echo -e "${RED}.env dosyası bulunamadı. Lütfen manuel olarak bir .env dosyası oluşturun.${NC}"
    exit 1
fi

# 4. PostgreSQL veritabanı ve kullanıcı oluştur
echo -e "\n${YELLOW}Veritabanı ve kullanıcı oluşturuluyor...${NC}"

# PostgreSQL'e bağlanma komutu
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    PG_CMD="sudo -u postgres psql"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    PG_CMD="psql postgres"
else
    # Windows veya diğer
    PG_CMD="psql -U postgres"
fi

# Veritabanı ve kullanıcı oluşturma ve yetkilendirme
$PG_CMD <<EOF
-- Kullanıcıyı oluştur
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
        CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWORD}' CREATEDB;
    END IF;
END
\$\$;

-- Veritabanını oluştur
SELECT 'CREATE DATABASE ${DB_NAME} WITH OWNER ${DB_USER}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}');

-- Yetkileri ata
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Veritabanı ve kullanıcı başarıyla oluşturuldu.${NC}"
else
    echo -e "${RED}Veritabanı ve kullanıcı oluşturulurken hata oluştu.${NC}"
    exit 1
fi

# 5. Django migrasyonlarını çalıştır
echo -e "\n${YELLOW}Django migrasyonları çalıştırılıyor...${NC}"
python manage.py migrate

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Migrasyonlar başarıyla tamamlandı.${NC}"
else
    echo -e "${RED}Migrasyon sırasında hata oluştu.${NC}"
    exit 1
fi

# 6. Superuser oluştur
echo -e "\n${YELLOW}Django superuser oluşturmak ister misiniz? (e/h)${NC}"
read -r create_superuser

if [[ $create_superuser == "e" || $create_superuser == "E" ]]; then
    echo -e "${YELLOW}Superuser oluşturuluyor...${NC}"
    python manage.py createsuperuser
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Superuser başarıyla oluşturuldu.${NC}"
    else
        echo -e "${RED}Superuser oluşturulurken hata oluştu.${NC}"
    fi
fi

echo -e "\n${GREEN}===== FinAsis PostgreSQL Kurulum ve Ayarlama İşlemi Tamamlandı =====${NC}"
echo -e "${YELLOW}Django development sunucusunu başlatmak için: ${NC}python manage.py runserver"
echo -e "${YELLOW}Docker ile tüm servisleri başlatmak için: ${NC}docker-compose up -d" 