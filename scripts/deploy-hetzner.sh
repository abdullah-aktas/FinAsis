#!/bin/bash
# Hetzner Deployment Script
# Bu script, FinAsis uygulamasını Hetzner sunucusunda deploy eder

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

# Proje dizini
PROJECT_DIR="/opt/finasis"
COMPOSE_FILE="docker-compose.hetzner.yml"

# Dizine git
cd "$PROJECT_DIR" || {
    log_error "Proje dizini bulunamadı: $PROJECT_DIR"
    exit 1
}

log_info "🚀 FinAsis Hetzner Deployment başlatılıyor..."

# .env dosyası kontrolü
if [ ! -f "$PROJECT_DIR/.env" ]; then
    log_error ".env dosyası bulunamadı!"
    log_info "Lütfen .env dosyasını oluşturun:"
    log_info "  cp env.example .env"
    log_info "  nano .env"
    exit 1
fi

# Git pull (eğer git repo ise)
if [ -d "$PROJECT_DIR/.git" ]; then
    log_info "📥 Git'ten son değişiklikleri çekiliyor..."
    git pull || log_warn "Git pull başarısız, devam ediliyor..."
fi

# Docker Compose build
log_info "🏗️  Docker image'ları build ediliyor..."
docker compose -f "$COMPOSE_FILE" build --no-cache

# Veritabanı migration'ları
log_info "🔄 Veritabanı migration'ları çalıştırılıyor..."
docker compose -f "$COMPOSE_FILE" run --rm finasis python manage.py migrate --noinput

# Static dosyaları topla
log_info "📦 Static dosyalar toplanıyor..."
docker compose -f "$COMPOSE_FILE" run --rm finasis python manage.py collectstatic --noinput

# Container'ları yeniden başlat
log_info "🔄 Container'lar yeniden başlatılıyor..."
docker compose -f "$COMPOSE_FILE" down
docker compose -f "$COMPOSE_FILE" up -d

# Health check
log_info "🏥 Health check yapılıyor..."
sleep 10

if docker compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    log_info "✅ Deployment başarılı!"
    log_info "📊 Container durumu:"
    docker compose -f "$COMPOSE_FILE" ps
else
    log_error "❌ Deployment başarısız! Logları kontrol edin:"
    log_error "   docker compose -f $COMPOSE_FILE logs"
    exit 1
fi

log_info "🎉 FinAsis başarıyla deploy edildi!"
log_info "📝 Logları görmek için: docker compose -f $COMPOSE_FILE logs -f"

