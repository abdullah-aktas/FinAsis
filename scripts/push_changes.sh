#!/bin/bash

# Renk tanımları
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}FinAsis değişikliklerini uzak depoya gönderme${NC}"

# Proje dizinine git
cd "$(dirname "$0")/.."

# Git durumunu kontrol et
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}Gönderilecek değişiklik yok.${NC}"
    exit 0
fi

# Değişiklikleri göster
echo -e "\n${YELLOW}Değişiklikler:${NC}"
git status

# Tüm değişiklikleri stage'e ekle
git add .

# Commit mesajı al
echo -e "\n${YELLOW}Commit mesajını girin:${NC}"
read -r commit_message

# Commit oluştur
if git commit -m "$commit_message"; then
    echo -e "${GREEN}Commit başarıyla oluşturuldu.${NC}"
else
    echo -e "${RED}Commit oluşturulurken hata oluştu.${NC}"
    exit 1
fi

# Uzak depoya gönder
if git push origin main; then
    echo -e "${GREEN}Değişiklikler başarıyla gönderildi.${NC}"
else
    echo -e "${RED}Push işlemi sırasında hata oluştu.${NC}"
    exit 1
fi
