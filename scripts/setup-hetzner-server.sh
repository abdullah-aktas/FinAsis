#!/bin/bash
# Hetzner Sunucu İlk Kurulum Scripti
# Bu script, Hetzner sunucusunu FinAsis için hazırlar

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

# Root kontrolü
if [ "$EUID" -ne 0 ]; then 
    log_error "Bu script root olarak çalıştırılmalı!"
    exit 1
fi

log_info "🚀 Hetzner sunucu kurulumu başlatılıyor..."

# 1. Sistem güncellemesi
log_step "1. Sistem güncelleniyor..."
apt update && apt upgrade -y

# 2. Temel paketler
log_step "2. Temel paketler kuruluyor..."
apt install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    ufw \
    fail2ban \
    unattended-upgrades

# 3. Docker kurulumu
log_step "3. Docker kuruluyor..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    log_info "✅ Docker kuruldu"
else
    log_info "✅ Docker zaten kurulu"
fi

# Docker Compose kurulumu
if ! command -v docker compose &> /dev/null; then
    apt install docker-compose-plugin -y
    log_info "✅ Docker Compose kuruldu"
else
    log_info "✅ Docker Compose zaten kurulu"
fi

# Docker servisini başlat
systemctl enable docker
systemctl start docker

# 4. Nginx kurulumu
log_step "4. Nginx kuruluyor..."
if ! command -v nginx &> /dev/null; then
    apt install nginx -y
    systemctl enable nginx
    systemctl start nginx
    log_info "✅ Nginx kuruldu"
else
    log_info "✅ Nginx zaten kurulu"
fi

# 5. Certbot kurulumu (SSL için)
log_step "5. Certbot kuruluyor..."
if ! command -v certbot &> /dev/null; then
    apt install certbot python3-certbot-nginx -y
    log_info "✅ Certbot kuruldu"
else
    log_info "✅ Certbot zaten kurulu"
fi

# 6. Firewall yapılandırması
log_step "6. Firewall yapılandırılıyor..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable
log_info "✅ Firewall yapılandırıldı"

# 7. Fail2ban yapılandırması
log_step "7. Fail2ban yapılandırılıyor..."
systemctl enable fail2ban
systemctl start fail2ban
log_info "✅ Fail2ban aktif"

# 8. Otomatik güncellemeler
log_step "8. Otomatik güncellemeler yapılandırılıyor..."
echo 'Unattended-Upgrade::Automatic-Reboot "false";' >> /etc/apt/apt.conf.d/50unattended-upgrades
systemctl enable unattended-upgrades
log_info "✅ Otomatik güncellemeler aktif"

# 9. Proje dizini oluşturma
log_step "9. Proje dizini oluşturuluyor..."
mkdir -p /opt/finasis
log_info "✅ Proje dizini: /opt/finasis"

# 10. Backup dizini
log_step "10. Backup dizini oluşturuluyor..."
mkdir -p /opt/backups
log_info "✅ Backup dizini: /opt/backups"

# 11. Kullanıcı oluşturma (opsiyonel)
log_step "11. Deployment kullanıcısı oluşturuluyor..."
if ! id "finasis" &>/dev/null; then
    useradd -m -s /bin/bash finasis
    usermod -aG docker finasis
    log_info "✅ 'finasis' kullanıcısı oluşturuldu"
else
    log_info "✅ 'finasis' kullanıcısı zaten var"
fi

log_info ""
log_info "✅ Sunucu kurulumu tamamlandı!"
log_info ""
log_info "📝 Sonraki adımlar:"
log_info "1. Projeyi /opt/finasis dizinine yükleyin"
log_info "2. .env dosyasını oluşturun (env.example'dan kopyalayın)"
log_info "3. docker-compose.hetzner.yml dosyasını kullanarak deploy edin"
log_info "4. Nginx yapılandırmasını oluşturun"
log_info "5. SSL sertifikası alın: certbot --nginx -d finasis.com.tr -d www.finasis.com.tr"
log_info ""
log_info "💡 Deployment için:"
log_info "   cd /opt/finasis"
log_info "   bash scripts/deploy-hetzner.sh"

