# 🚀 Hetzner'da FinAsis Deployment Rehberi

Bu rehber, finasis.com.tr'yi Google Cloud yerine Hetzner'da nasıl yayınlayacağınızı açıklar.

## 📋 Seçenekler

Hetzner'da iki ana seçenek var:

1. **Hetzner Cloud VPS** (Önerilen) - Esnek ve ölçeklenebilir
2. **Hetzner Dedicated Server** - Daha fazla performans için

## 🎯 Önerilen Yapılandırma

### Minimum Gereksinimler
- **CPU**: 2+ core
- **RAM**: 4GB+ (8GB önerilir)
- **Disk**: 50GB+ SSD
- **OS**: Ubuntu 22.04 LTS veya Debian 12

### Önerilen Sunucu
- **Hetzner Cloud CPX31**: 4 vCPU, 8GB RAM, 160GB SSD (~€15/ay)
- **Hetzner Cloud CPX41**: 8 vCPU, 16GB RAM, 240GB SSD (~€30/ay)

## 📦 Adım 1: Hetzner Sunucu Kurulumu

### 1.1 Sunucu Oluşturma

1. [Hetzner Cloud Console](https://console.hetzner.cloud/)'a giriş yapın
2. "Add Server" butonuna tıklayın
3. Şunları seçin:
   - **Location**: Nuremberg (Türkiye'ye yakın)
   - **Image**: Ubuntu 22.04
   - **Type**: CPX31 veya CPX41
   - **SSH Keys**: Kendi SSH anahtarınızı ekleyin
4. Sunucuyu oluşturun

### 1.2 İlk Bağlantı

```bash
ssh root@<sunucu-ip-adresi>
```

## 🔧 Adım 2: Sunucu Hazırlığı

### 2.1 Sistem Güncellemesi

```bash
apt update && apt upgrade -y
```

### 2.2 Docker Kurulumu

```bash
# Docker kurulumu
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose kurulumu
apt install docker-compose-plugin -y

# Docker servisini başlat
systemctl enable docker
systemctl start docker
```

### 2.3 PostgreSQL Kurulumu (Opsiyonel - Managed DB kullanabilirsiniz)

```bash
# PostgreSQL kurulumu
apt install postgresql postgresql-contrib -y

# PostgreSQL servisini başlat
systemctl enable postgresql
systemctl start postgresql

# Veritabanı oluştur
sudo -u postgres psql << EOF
CREATE DATABASE finasis;
CREATE USER finasis WITH PASSWORD 'güçlü-şifre-buraya';
GRANT ALL PRIVILEGES ON DATABASE finasis TO finasis;
\q
EOF
```

**Alternatif**: Hetzner Managed Database kullanabilirsiniz (önerilir).

### 2.4 Redis Kurulumu

```bash
apt install redis-server -y
systemctl enable redis-server
systemctl start redis-server
```

### 2.5 Nginx Kurulumu (Reverse Proxy için)

```bash
apt install nginx certbot python3-certbot-nginx -y
systemctl enable nginx
```

## 🐳 Adım 3: Docker ile Deployment

### 3.1 Proje Dizini Oluşturma

```bash
mkdir -p /opt/finasis
cd /opt/finasis
```

### 3.2 Docker Compose Dosyası Oluşturma

`docker-compose.yml` dosyası oluşturun:

```yaml
version: '3.8'

services:
  finasis:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: finasis-app
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:8080"  # Sadece localhost'tan erişilebilir (Nginx üzerinden)
    environment:
      # Django Ayarları
      - DJANGO_SETTINGS_MODULE=config.settings
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - DJANGO_DEBUG=False
      - DJANGO_ALLOWED_HOSTS=finasis.com.tr,www.finasis.com.tr
      - DJANGO_SITE_BASE_URL=https://finasis.com.tr
      - DJANGO_CSRF_TRUSTED_ORIGINS=https://finasis.com.tr,https://www.finasis.com.tr
      
      # Veritabanı
      - DJANGO_DB_ENGINE=django.db.backends.postgresql
      - DJANGO_DB_NAME=finasis
      - DJANGO_DB_USER=finasis
      - DJANGO_DB_PASSWORD=${DJANGO_DB_PASSWORD}
      - DJANGO_DB_HOST=db
      - DJANGO_DB_PORT=5432
      - DJANGO_DB_CONN_MAX_AGE=60
      
      # Redis
      - USE_REDIS=True
      - REDIS_URL=redis://redis:6379/0
      
      # Port
      - PORT=8080
      
      # Diğer
      - PYTHONUNBUFFERED=1
      - MPLCONFIGDIR=/tmp/matplotlib-cache
    volumes:
      - ./media:/app/media
      - ./staticfiles:/app/staticfiles
    depends_on:
      - db
      - redis
    networks:
      - finasis-network

  db:
    image: postgres:15-alpine
    container_name: finasis-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=finasis
      - POSTGRES_USER=finasis
      - POSTGRES_PASSWORD=${DJANGO_DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - finasis-network

  redis:
    image: redis:7-alpine
    container_name: finasis-redis
    restart: unless-stopped
    networks:
      - finasis-network

volumes:
  postgres_data:

networks:
  finasis-network:
    driver: bridge
```

### 3.3 Environment Dosyası Oluşturma

`.env` dosyası oluşturun:

```bash
nano /opt/finasis/.env
```

İçeriği:

```env
DJANGO_SECRET_KEY=çok-güçlü-ve-uzun-bir-secret-key-buraya
DJANGO_DB_PASSWORD=güçlü-veritabanı-şifresi-buraya
```

**Önemli**: Secret key'i güvenli bir şekilde oluşturun:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 3.4 Proje Dosyalarını Yükleme

#### Seçenek A: Git ile (Önerilen)

```bash
# Git kurulumu
apt install git -y

# Projeyi klonlayın
cd /opt/finasis
git clone <repository-url> .

# Veya mevcut projeyi SCP ile yükleyin
```

#### Seçenek B: SCP ile Dosya Transferi

Yerel bilgisayarınızdan:

```bash
scp -r /path/to/FinAsis root@<sunucu-ip>:/opt/finasis/
```

### 3.5 Docker Image Oluşturma ve Başlatma

```bash
cd /opt/finasis
docker compose build
docker compose up -d
```

### 3.6 Logları Kontrol Etme

```bash
docker compose logs -f finasis
```

## 🌐 Adım 4: Nginx Reverse Proxy Kurulumu

### 4.1 Nginx Yapılandırması

```bash
nano /etc/nginx/sites-available/finasis.com.tr
```

İçeriği:

```nginx
# HTTP'den HTTPS'e yönlendirme
server {
    listen 80;
    listen [::]:80;
    server_name finasis.com.tr www.finasis.com.tr;
    
    # Let's Encrypt doğrulama için
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS yapılandırması
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name finasis.com.tr www.finasis.com.tr;

    # SSL sertifikaları (Let's Encrypt ile otomatik oluşturulacak)
    ssl_certificate /etc/letsencrypt/live/finasis.com.tr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/finasis.com.tr/privkey.pem;
    
    # SSL ayarları
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Gzip sıkıştırma
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # Client body size limit (dosya yükleme için)
    client_max_body_size 100M;

    # Static dosyalar
    location /static/ {
        alias /opt/finasis/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media dosyalar
    location /media/ {
        alias /opt/finasis/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Django uygulaması
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # WebSocket desteği (gerekirse)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeout ayarları
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

### 4.2 Nginx'i Aktif Etme

```bash
ln -s /etc/nginx/sites-available/finasis.com.tr /etc/nginx/sites-enabled/
nginx -t  # Yapılandırmayı test et
systemctl reload nginx
```

## 🔒 Adım 5: SSL Sertifikası (Let's Encrypt)

### 5.1 Domain DNS Ayarları

Domain'inizi Hetzner sunucunuzun IP adresine yönlendirin:

```
A Record: finasis.com.tr → <sunucu-ip>
A Record: www.finasis.com.tr → <sunucu-ip>
```

### 5.2 SSL Sertifikası Oluşturma

```bash
certbot --nginx -d finasis.com.tr -d www.finasis.com.tr
```

Sertifika otomatik olarak yenilenecek (cron job ile).

## 🔄 Adım 6: Otomatik Deployment (Opsiyonel)

### 6.1 GitHub Actions ile Otomatik Deploy

`.github/workflows/deploy-hetzner.yml` dosyası oluşturun:

```yaml
name: Deploy to Hetzner

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Hetzner
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HETZNER_HOST }}
          username: root
          key: ${{ secrets.HETZNER_SSH_KEY }}
          script: |
            cd /opt/finasis
            git pull
            docker compose build
            docker compose up -d
            docker compose exec finasis python manage.py collectstatic --noinput
            docker compose exec finasis python manage.py migrate
```

### 6.2 Manuel Deployment Script

`deploy.sh` dosyası oluşturun:

```bash
#!/bin/bash
set -e

cd /opt/finasis

echo "🔄 Pulling latest changes..."
git pull

echo "🏗️ Building Docker image..."
docker compose build

echo "🔄 Running migrations..."
docker compose run --rm finasis python manage.py migrate

echo "📦 Collecting static files..."
docker compose run --rm finasis python manage.py collectstatic --noinput

echo "🚀 Restarting services..."
docker compose up -d

echo "✅ Deployment completed!"
```

Çalıştırılabilir yapın:

```bash
chmod +x /opt/finasis/deploy.sh
```

## 📊 Adım 7: Monitoring ve Backup

### 7.1 Log Takibi

```bash
# Uygulama logları
docker compose logs -f finasis

# Nginx logları
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 7.2 Veritabanı Yedekleme

`backup.sh` dosyası oluşturun:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Veritabanı yedeği
docker compose exec -T db pg_dump -U finasis finasis > $BACKUP_DIR/db_$DATE.sql

# Eski yedekleri temizle (7 günden eski)
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete

echo "✅ Backup completed: db_$DATE.sql"
```

Cron job ekleyin:

```bash
crontab -e
```

Ekle:

```
0 2 * * * /opt/finasis/backup.sh
```

## 🔧 Sorun Giderme

### Container Başlamıyor

```bash
docker compose logs finasis
docker compose ps
```

### Veritabanı Bağlantı Hatası

```bash
docker compose exec db psql -U finasis -d finasis
```

### Static Dosyalar Görünmüyor

```bash
docker compose exec finasis python manage.py collectstatic --noinput
```

### Nginx 502 Hatası

- Container'ın çalıştığını kontrol edin: `docker compose ps`
- Port'un doğru olduğunu kontrol edin: `netstat -tlnp | grep 8080`

## 📝 Önemli Notlar

1. **Güvenlik**: Firewall kurallarını yapılandırın (UFW önerilir)
2. **Performans**: Gunicorn worker sayısını CPU core sayısına göre ayarlayın
3. **Yedekleme**: Düzenli veritabanı yedekleri alın
4. **Monitoring**: Uptime monitoring servisi kullanın (UptimeRobot, Pingdom)
5. **Domain**: DNS ayarlarının doğru olduğundan emin olun

## 🔐 Güvenlik Önerileri

### Firewall Kurulumu

```bash
apt install ufw -y
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### Fail2Ban Kurulumu

```bash
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban
```

## 💰 Maliyet Tahmini

- **Hetzner Cloud CPX31**: ~€15/ay
- **Domain**: ~€10-15/yıl
- **Toplam**: ~€15-20/ay

Google Cloud Run'a göre çok daha ekonomik!

## 🆘 Destek

Sorun yaşarsanız:
1. Logları kontrol edin
2. Container durumunu kontrol edin
3. Nginx yapılandırmasını test edin
4. DNS ayarlarını doğrulayın

