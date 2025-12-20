#!/bin/bash
# Hetzner + Cloudflare Deployment Script
# Bu script, FinAsis uygulamasını Hetzner sunucusunda Cloudflare ile deploy eder

set -euo pipefail

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Proje dizini
PROJECT_DIR="/opt/finasis"
COMPOSE_FILE="docker-compose.hetzner.yml"

# Dizine git
cd "$PROJECT_DIR" || {
    log_error "Proje dizini bulunamadı: $PROJECT_DIR"
    exit 1
}

log_info "☁️  FinAsis Hetzner + Cloudflare Deployment başlatılıyor..."

# .env dosyası kontrolü
if [ ! -f "$PROJECT_DIR/.env" ]; then
    log_error ".env dosyası bulunamadı!"
    log_info "Lütfen .env dosyasını oluşturun:"
    log_info "  cp env.example .env"
    log_info "  nano .env"
    exit 1
fi

# Cloudflare IP listesini güncelle
log_step "1. Cloudflare IP listesi güncelleniyor..."
if [ -f "$PROJECT_DIR/scripts/setup-cloudflare-ips.sh" ]; then
    bash "$PROJECT_DIR/scripts/setup-cloudflare-ips.sh"
else
    log_warn "Cloudflare IP script bulunamadı, atlanıyor..."
fi

# Git pull (eğer git repo ise)
if [ -d "$PROJECT_DIR/.git" ]; then
    log_step "2. Git'ten son değişiklikler çekiliyor..."
    git pull || log_warn "Git pull başarısız, devam ediliyor..."
fi

# Docker Compose build
log_step "3. Docker image'ları build ediliyor..."
docker compose -f "$COMPOSE_FILE" build --no-cache

# Veritabanı migration'ları
log_step "4. Veritabanı migration'ları çalıştırılıyor..."
docker compose -f "$COMPOSE_FILE" run --rm finasis python manage.py migrate --noinput

# Static dosyaları topla
log_step "5. Static dosyalar toplanıyor..."
docker compose -f "$COMPOSE_FILE" run --rm finasis python manage.py collectstatic --noinput

# Nginx yapılandırmasını kontrol et
log_step "6. Nginx yapılandırması kontrol ediliyor..."
if [ -f "/etc/nginx/sites-available/finasis.com.tr" ]; then
    log_info "Nginx config mevcut"
    nginx -t || log_warn "Nginx config hatası, kontrol edin!"
else
    log_warn "Nginx config bulunamadı!"
    log_info "Cloudflare için config yükleyin:"
    log_info "  cp $PROJECT_DIR/deploy/nginx/finasis.com.tr.cloudflare.conf /etc/nginx/sites-available/finasis.com.tr"
    log_info "  ln -s /etc/nginx/sites-available/finasis.com.tr /etc/nginx/sites-enabled/"
fi

# Container'ları yeniden başlat
log_step "7. Container'lar yeniden başlatılıyor..."
docker compose -f "$COMPOSE_FILE" down
docker compose -f "$COMPOSE_FILE" up -d

# Health check
log_step "8. Health check yapılıyor..."
sleep 10

if docker compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    log_info "✅ Deployment başarılı!"
    log_info ""
    log_info "📊 Container durumu:"
    docker compose -f "$COMPOSE_FILE" ps
    log_info ""
    log_info "☁️  Cloudflare Kontrol Listesi:"
    log_info "  [ ] DNS kayıtları Cloudflare'de Proxied (☁️) olmalı"
    log_info "  [ ] SSL/TLS mode: Full (strict)"
    log_info "  [ ] Origin Certificate yüklü olmalı"
    log_info "  [ ] Page Rules yapılandırıldı mı?"
    log_info ""
    log_info "📝 Logları görmek için:"
    log_info "   docker compose -f $COMPOSE_FILE logs -f"
else
    log_error "❌ Deployment başarısız! Logları kontrol edin:"
    log_error "   docker compose -f $COMPOSE_FILE logs"
    exit 1
fi

log_info ""
log_info "🎉 FinAsis başarıyla deploy edildi (Hetzner + Cloudflare)!"

