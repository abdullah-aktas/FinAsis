#!/bin/bash
# FinAsis veritabanı geçişleri (migrations) oluşturma betiği
# Bu betik, proje uygulamalarının veritabanı geçişlerini oluşturur.

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Proje dizinine git
cd "$(dirname "$0")/.."

# Sanal ortamın aktif olup olmadığını kontrol et
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Sanal ortam aktif değil. Aktifleştiriliyor...${NC}"
    
    # İşletim sistemine göre sanal ortam etkinleştirme komutları
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows için
        if [ -d "venv" ]; then
            source venv/Scripts/activate
        elif [ -d ".venv" ]; then
            source .venv/Scripts/activate
        else
            echo -e "${RED}Sanal ortam bulunamadı. Önce sanal ortam oluşturun.${NC}"
            exit 1
        fi
    else
        # Linux/macOS için
        if [ -d "venv" ]; then
            source venv/bin/activate
        elif [ -d ".venv" ]; then
            source .venv/bin/activate
        else
            echo -e "${RED}Sanal ortam bulunamadı. Önce sanal ortam oluşturun.${NC}"
            exit 1
        fi
    fi
fi

# Parametre kontrolü
if [ "$#" -eq 0 ]; then
    # Tüm uygulamalar için geçiş oluştur
    APPS=("users" "finance" "accounting" "integrations.efatura" "integrations.bank_integration")
else
    # Belirtilen uygulamalar için geçiş oluştur
    APPS=("$@")
fi

echo -e "${GREEN}Veritabanı geçişleri oluşturuluyor...${NC}"

# Her uygulama için geçiş oluştur
for app in "${APPS[@]}"; do
    echo -e "${YELLOW}Uygulama: apps.${app}${NC}"
    python manage.py makemigrations ${app}
    
    # Hata kontrolü
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ apps.${app} için geçişler oluşturuldu.${NC}"
    else
        echo -e "${RED}✗ apps.${app} için geçiş oluşturulurken hata oluştu.${NC}"
    fi
done

# Migrasyon kontrolü
echo -e "\n${YELLOW}Bekleyen migrasyonlar kontrol ediliyor...${NC}"
python manage.py showmigrations

echo -e "\n${GREEN}İşlem tamamlandı.${NC}"
echo -e "${YELLOW}Geçişleri uygulamak için: python manage.py migrate${NC}" 