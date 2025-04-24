#!/bin/bash
# compile_messages.sh - Django çeviri dosyalarını derler ve yönetir
set -euo pipefail

# Renk tanımlamaları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log dosyası
LOG_FILE="compile_messages.log"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

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
    echo -e "\n${BLUE}FinAsis Çeviri Yönetim Sistemi${NC}"
    echo -e "${BLUE}===============================${NC}\n"
}

# Bağımlılık kontrolü
check_dependencies() {
    log "INFO" "Bağımlılıklar kontrol ediliyor..."
    
    # Sanal ortam kontrolü
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        handle_error 1 "Sanal ortam (virtualenv) etkin değil!\nLütfen önce sanal ortamı etkinleştirin:\n  source venv/bin/activate    # Linux/macOS\n  venv\\Scripts\\activate       # Windows"
    fi
    
    # Django kontrolü
    if ! python -c "import django" &> /dev/null; then
        handle_error 1 "Django yüklü değil!\nLütfen önce gerekli paketleri yükleyin:\n  pip install -r requirements.txt"
    fi
    
    # gettext kontrolü
    if ! command -v msgfmt &> /dev/null; then
        handle_error 1 "gettext yüklü değil!\nLütfen gettext paketini yükleyin:\n  sudo apt-get install gettext    # Ubuntu/Debian\n  brew install gettext            # macOS\n  choco install gettext           # Windows (Chocolatey)"
    fi
    
    log "INFO" "${GREEN}✓ Tüm bağımlılıklar mevcut.${NC}"
}

# Çeviri dosyalarını derle
compile_messages() {
    log "INFO" "Çeviri dosyaları derleniyor..."
    
    if python manage.py compilemessages; then
        log "INFO" "${GREEN}✓ Çeviri dosyaları başarıyla derlendi.${NC}"
    else
        handle_error 1 "Çeviri dosyaları derlenirken bir hata oluştu!"
    fi
}

# Çevrilebilir metinleri çıkar
extract_messages() {
    local languages=("tr" "en" "ar" "ku" "de")
    local success=true
    
    log "INFO" "Çevrilebilir metinler çıkartılıyor..."
    
    for lang in "${languages[@]}"; do
        log "INFO" "Dil: $lang için metinler çıkartılıyor..."
        if ! python manage.py makemessages -l "$lang"; then
            log "WARNING" "${YELLOW}Uyarı: $lang dili için metin çıkarma başarısız oldu.${NC}"
            success=false
        fi
    done
    
    if $success; then
        log "INFO" "${GREEN}✓ Tüm diller için çevrilebilir metinler başarıyla çıkartıldı.${NC}"
    else
        log "WARNING" "${YELLOW}Bazı diller için metin çıkarma işlemi başarısız oldu.${NC}"
    fi
}

# Çeviri istatistiklerini hesapla
calculate_stats() {
    log "INFO" "Çeviri istatistikleri hesaplanıyor..."
    
    local total_messages=0
    local translated_messages=0
    local fuzzy_messages=0
    
    for po_file in $(find locale -name "*.po"); do
        local stats=$(msgfmt --statistics "$po_file" 2>&1)
        local messages=$(echo "$stats" | grep -o '[0-9]* translated messages' | grep -o '[0-9]*')
        local fuzzy=$(echo "$stats" | grep -o '[0-9]* fuzzy translations' | grep -o '[0-9]*')
        local untranslated=$(echo "$stats" | grep -o '[0-9]* untranslated messages' | grep -o '[0-9]*')
        
        total_messages=$((total_messages + messages + fuzzy + untranslated))
        translated_messages=$((translated_messages + messages))
        fuzzy_messages=$((fuzzy_messages + fuzzy))
    done
    
    local percentage=$((translated_messages * 100 / total_messages))
    
    log "INFO" "Çeviri İstatistikleri:"
    log "INFO" "- Toplam Mesaj: $total_messages"
    log "INFO" "- Çevrilen: $translated_messages (%$percentage)"
    log "INFO" "- Bulanık: $fuzzy_messages"
    log "INFO" "- Çevrilmemiş: $((total_messages - translated_messages - fuzzy_messages))"
}

# Ana fonksiyon
main() {
    print_header
    check_dependencies
    compile_messages
    extract_messages
    calculate_stats
    
    log "INFO" "\nÇeviri işlemleri tamamlandı."
    log "INFO" "Düzenlemeler için 'locale/' dizinindeki .po dosyalarını kontrol edin."
    log "INFO" "Düzenlemeleri tamamladıktan sonra bu betiği tekrar çalıştırın."
}

# Betiği çalıştır
main "$@" 