#!/bin/bash
# Cloudflare IP listesini indir ve Nginx formatına dönüştür
# Bu script, Cloudflare'in güncel IP adreslerini Nginx yapılandırmasına ekler

set -euo pipefail

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Root kontrolü
if [ "$EUID" -ne 0 ]; then 
    log_error "Bu script root olarak çalıştırılmalı!"
    exit 1
fi

log_info "☁️  Cloudflare IP listesi güncelleniyor..."

# Geçici dosyalar
TMP_V4="/tmp/cloudflare-ips-v4.txt"
TMP_V6="/tmp/cloudflare-ips-v6.txt"
NGINX_V4="/etc/nginx/cloudflare-ips-v4.conf"
NGINX_V6="/etc/nginx/cloudflare-ips-v6.conf"

# IPv4 IP'lerini indir
log_info "📥 IPv4 IP listesi indiriliyor..."
if curl -s -f https://www.cloudflare.com/ips-v4 > "$TMP_V4"; then
    log_info "✅ IPv4 IP listesi indirildi"
else
    log_error "❌ IPv4 IP listesi indirilemedi!"
    exit 1
fi

# IPv6 IP'lerini indir
log_info "📥 IPv6 IP listesi indiriliyor..."
if curl -s -f https://www.cloudflare.com/ips-v6 > "$TMP_V6"; then
    log_info "✅ IPv6 IP listesi indirildi"
else
    log_warn "⚠️  IPv6 IP listesi indirilemedi (opsiyonel)"
    touch "$TMP_V6"
fi

# Nginx formatına dönüştür (IPv4)
log_info "🔄 IPv4 IP'leri Nginx formatına dönüştürülüyor..."
{
    echo "# Cloudflare IPv4 IP Listesi"
    echo "# Otomatik güncellenir - manuel düzenleme yapmayın"
    echo "# Son güncelleme: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    echo ""
    sed 's/^/set_real_ip_from /' "$TMP_V4" | sed 's/$/;/'
    echo ""
    echo "# Gerçek IP header'ı"
    echo "real_ip_header CF-Connecting-IP;"
} > "$NGINX_V4"

log_info "✅ IPv4 yapılandırması oluşturuldu: $NGINX_V4"

# Nginx formatına dönüştür (IPv6)
if [ -s "$TMP_V6" ]; then
    log_info "🔄 IPv6 IP'leri Nginx formatına dönüştürülüyor..."
    {
        echo "# Cloudflare IPv6 IP Listesi"
        echo "# Otomatik güncellenir - manuel düzenleme yapmayın"
        echo "# Son güncelleme: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
        echo ""
        sed 's/^/set_real_ip_from /' "$TMP_V6" | sed 's/$/;/'
        echo ""
        echo "# Gerçek IP header'ı (IPv6 için de aynı)"
    } > "$NGINX_V6"
    
    log_info "✅ IPv6 yapılandırması oluşturuldu: $NGINX_V6"
else
    log_warn "⚠️  IPv6 yapılandırması oluşturulmadı (boş liste)"
    touch "$NGINX_V6"
fi

# Geçici dosyaları temizle
rm -f "$TMP_V4" "$TMP_V6"

# Nginx yapılandırmasını test et
log_info "🧪 Nginx yapılandırması test ediliyor..."
if nginx -t 2>/dev/null; then
    log_info "✅ Nginx yapılandırması geçerli"
    
    # Nginx'i reload et
    log_info "🔄 Nginx yeniden yükleniyor..."
    if systemctl reload nginx; then
        log_info "✅ Nginx başarıyla yeniden yüklendi"
    else
        log_error "❌ Nginx yeniden yüklenemedi!"
        exit 1
    fi
else
    log_error "❌ Nginx yapılandırması geçersiz!"
    log_error "Lütfen yapılandırmayı kontrol edin: nginx -t"
    exit 1
fi

# İstatistikler
V4_COUNT=$(grep -c "set_real_ip_from" "$NGINX_V4" || echo "0")
V6_COUNT=$(grep -c "set_real_ip_from" "$NGINX_V6" || echo "0")

log_info ""
log_info "📊 Özet:"
log_info "  IPv4 IP sayısı: $V4_COUNT"
log_info "  IPv6 IP sayısı: $V6_COUNT"
log_info "  Yapılandırma dosyaları:"
log_info "    - $NGINX_V4"
log_info "    - $NGINX_V6"
log_info ""
log_info "✅ Cloudflare IP listesi başarıyla güncellendi!"

