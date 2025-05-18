#!/bin/bash

# Renk tanımlamaları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}GitIgnore Kontrol Aracı${NC}"
echo "=========================="

# Dizin kontrolü
if [ ! -f ".gitignore" ]; then
    echo -e "${RED}Hata: .gitignore dosyası bulunamadı!${NC}"
    exit 1
fi

# Sözdizimi kontrolü
echo -e "\n${YELLOW}1. Sözdizimi Kontrolü${NC}"
if git check-ignore --no-index * > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Sözdizimi kontrolü başarılı${NC}"
else
    echo -e "${RED}✗ Sözdizimi hatası tespit edildi${NC}"
fi

# Hassas dosya kontrolü
echo -e "\n${YELLOW}2. Hassas Dosya Kontrolü${NC}"
SENSITIVE_FILES=$(git ls-files | grep -i "secret\|password\|key\|credential" 2>/dev/null)
if [ -z "$SENSITIVE_FILES" ]; then
    echo -e "${GREEN}✓ Hassas dosya tespit edilmedi${NC}"
else
    echo -e "${RED}✗ Dikkat: Potansiyel hassas dosyalar:${NC}"
    echo "$SENSITIVE_FILES"
fi

# Tekrarlanan kuralların kontrolü
echo -e "\n${YELLOW}3. Tekrarlanan Kural Kontrolü${NC}"
DUPLICATES=$(sort .gitignore | uniq -d)
if [ -z "$DUPLICATES" ]; then
    echo -e "${GREEN}✓ Tekrarlanan kural bulunamadı${NC}"
else
    echo -e "${RED}✗ Tekrarlanan kurallar:${NC}"
    echo "$DUPLICATES"
fi

# Global ve local ignore dosyalarının kontrolü
echo -e "\n${YELLOW}4. Ignore Dosyaları Tutarlılık Kontrolü${NC}"
for file in .gitignore .gitignore.local .gitignore_global; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file mevcut${NC}"
    else
        echo -e "${YELLOW}! $file bulunamadı${NC}"
    fi
done

# Performans kontrolü
echo -e "\n${YELLOW}5. Performans Kontrolü${NC}"
RULE_COUNT=$(grep -v '^#' .gitignore | grep -v '^$' | wc -l)
if [ $RULE_COUNT -gt 100 ]; then
    echo -e "${YELLOW}! Uyarı: $RULE_COUNT kural mevcut (100'den fazla)${NC}"
else
    echo -e "${GREEN}✓ Kural sayısı optimal ($RULE_COUNT kural)${NC}"
fi

# Önerilen güncellemeler
echo -e "\n${YELLOW}6. Önerilen Güncellemeler${NC}"
COMMON_MISSING=(
    "node_modules/"
    ".env"
    "*.log"
    "dist/"
    "build/"
)

for pattern in "${COMMON_MISSING[@]}"; do
    if ! grep -q "^$pattern$" .gitignore; then
        echo -e "${YELLOW}! Öneri: '$pattern' eklenebilir${NC}"
    fi
done

# Özet rapor
echo -e "\n${YELLOW}Özet Rapor${NC}"
echo "=========================="
echo "Toplam Kural Sayısı: $RULE_COUNT"
echo "Son Güncelleme: $(stat -f %Sm .gitignore)"
echo "Dosya Boyutu: $(ls -lh .gitignore | awk '{print $5}')"

# Bakım önerileri
echo -e "\n${YELLOW}Bakım Önerileri${NC}"
echo "=========================="
echo "1. Düzenli olarak 'git status' kontrolü yapın"
echo "2. Yeni teknolojiler için kuralları güncelleyin"
echo "3. Güvenlik kontrollerini periyodik olarak tekrarlayın"
echo "4. Takım üyelerinden geri bildirim alın"

exit 0 