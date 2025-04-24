# FinAsis Canlı Ortam Kurulum Rehberi

Bu rehber, FinAsis uygulamasının canlı ortamda (production) kurulumu ve çalıştırılması için gerekli adımları içermektedir.

## 1. Sistem Gereksinimleri

### 1.1 Minimum Gereksinimler
- **İşletim Sistemi**: Ubuntu 22.04 LTS veya daha yeni (önerilen)
- **CPU**: En az 4 çekirdek (önerilen 8+)
- **RAM**: En az 16GB (önerilen 32GB+)
- **Disk**: En az 200GB SSD (önerilen 500GB+)
- **Ağ**: Sabit IP adresi ve domain adı
- **Bant Genişliği**: En az 100Mbps (önerilen 1Gbps)

### 1.2 Önerilen Gereksinimler
- **İşletim Sistemi**: Ubuntu 22.04 LTS
- **CPU**: 8+ çekirdek
- **RAM**: 32GB+
- **Disk**: 500GB+ NVMe SSD
- **Ağ**: 1Gbps bağlantı
- **Yedeklilik**: RAID 10 veya RAID 5
- **UPS**: En az 1 saat kesintisiz güç

## 2. Ön Gereksinimler

### 2.1 Temel Yazılımlar
- Docker 24.0+ ve Docker Compose 2.20+
- Git 2.40+
- Nginx 1.25+ (Docker dışında, ana host üzerinde)
- Certbot 2.6+
- Python 3.11+
- Node.js 18+ (frontend build için)
- Redis 7.0+
- PostgreSQL 15+

### 2.2 Güvenlik Yazılımları
- UFW (Uncomplicated Firewall)
- Fail2ban
- ClamAV (antivirüs)
- Rkhunter (rootkit tarayıcı)
- Lynis (güvenlik denetimi)

### 2.3 İzleme Araçları
- Prometheus 2.45+
- Grafana 10.0+
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Zabbix 6.4+
- Netdata

## 3. Kurulum Adımları

### 3.1 Sistem Hazırlığı

```bash
# Sistem güncellemeleri
sudo apt update && sudo apt upgrade -y

# Temel paketler
sudo apt install -y curl wget git unzip build-essential libssl-dev \
    libffi-dev python3-dev python3-pip python3-venv nginx certbot \
    ufw fail2ban clamav rkhunter lynis

# Güvenlik duvarı yapılandırması
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# Docker kurulumu
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker

# Docker Compose kurulumu
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3.2 Depoyu Klonlama ve Hazırlık

```bash
# Depoyu klonlama
git clone https://github.com/your-username/finasis.git
cd finasis

# Güvenlik denetimi
rkhunter --check
lynis audit system

# Dosya izinleri
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
find . -name "*.sh" -exec chmod +x {} \;
```

### 3.3 Ortam Değişkenlerini Ayarlama

`.env.example` dosyasını `.env` olarak kopyalayın ve değerleri kendi ortamınıza göre düzenleyin:

```bash
cp .env.example .env
nano .env
```

Aşağıdaki değerleri kendi ortamınıza göre ayarlayın:
- DJANGO_SECRET_KEY (en az 50 karakter)
- DJANGO_ALLOWED_HOSTS
- Veritabanı bilgileri
- Email ayarları
- AWS S3 bilgileri
- OpenAI API Key
- Şirket bilgileri
- Redis bağlantı bilgileri
- Celery ayarları
- Monitoring API anahtarları
- Backup ayarları

### 3.4 Docker ile Çalıştırma

Üretim ortamı için docker-compose.prod.yml dosyasını kullanın:

```bash
# Docker imajlarını oluştur
docker-compose -f docker-compose.prod.yml build --no-cache

# Servisleri başlat
docker-compose -f docker-compose.prod.yml up -d

# Servis durumunu kontrol et
docker-compose -f docker-compose.prod.yml ps
```

### 3.5 Veritabanı Migrasyonları ve Başlangıç Ayarları

```bash
# Veritabanı migrasyonları
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Statik dosyaları topla
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input

# Süper kullanıcı oluştur
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# İlk verileri yükle
docker-compose -f docker-compose.prod.yml exec web python manage.py loaddata initial_data.json

# Cache'i temizle
docker-compose -f docker-compose.prod.yml exec web python manage.py clear_cache
```

### 3.6 Nginx Konfigürasyonu

`/etc/nginx/sites-available/finasis.conf` dosyasını oluşturun:

```nginx
# Ana sunucu bloğu
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # SSL yönlendirme
    location / {
        return 301 https://$host$request_uri;
    }
}

# SSL sunucu bloğu
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL sertifikaları
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL parametreleri
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # HSTS (31536000 saniye = 1 yıl)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Diğer güvenlik başlıkları
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data: https:; connect-src 'self' https:;";
    
    # Statik dosyalar
    location /static/ {
        alias /path/to/finasis/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
        access_log off;
    }
    
    # Media dosyaları
    location /media/ {
        alias /path/to/finasis/media/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
        access_log off;
    }
    
    # API istekleri
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # WebSocket desteği
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Proxy zaman aşımı
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;
    }
    
    # Sağlık kontrolü
    location /health/ {
        proxy_pass http://localhost:8000/health/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        access_log off;
        proxy_read_timeout 5s;
        proxy_connect_timeout 5s;
        proxy_send_timeout 5s;
    }
    
    # Metrikler
    location /metrics/ {
        proxy_pass http://localhost:8000/metrics/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        access_log off;
        auth_basic "Metrics";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}

# Rate limiting tanımı
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

### 3.7 SSL Sertifikası Alınması

Let's Encrypt ile SSL sertifikası oluşturun:

```bash
# Sertifika al
certbot --nginx -d your-domain.com -d www.your-domain.com \
    --email admin@your-domain.com \
    --agree-tos \
    --no-eff-email \
    --redirect \
    --hsts \
    --staple-ocsp \
    --must-staple

# Otomatik yenileme kontrolü
certbot renew --dry-run
```

## 4. Bakım ve İzleme

### 4.1 Otomatik Yedekleme

`backup.sh` betiğini cron ile çalıştırın:

```bash
# Yedekleme betiği
#!/bin/bash

# Tarih ve saat
DATE=$(date +%Y%m%d_%H%M%S)

# Yedekleme dizini
BACKUP_DIR="/backup/finasis"

# Veritabanı yedeği
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres finasis > $BACKUP_DIR/db_$DATE.sql

# Dosya yedeği
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /path/to/finasis

# S3'e yükle (opsiyonel)
aws s3 cp $BACKUP_DIR/db_$DATE.sql s3://your-bucket/backups/
aws s3 cp $BACKUP_DIR/files_$DATE.tar.gz s3://your-bucket/backups/

# Eski yedekleri temizle
find $BACKUP_DIR -type f -mtime +30 -delete
```

### 4.2 Log Yönetimi

```bash
# Log rotasyonu
sudo nano /etc/logrotate.d/finasis

# Log rotasyon konfigürasyonu
/path/to/finasis/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        docker-compose -f docker-compose.prod.yml restart web
    endscript
}
```

### 4.3 İzleme Sistemi

Prometheus ve Grafana kurulumları docker-compose.prod.yml içinde tanımlanmıştır:

```yaml
# Prometheus konfigürasyonu
prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--web.console.libraries=/usr/share/prometheus/console_libraries'
    - '--web.console.templates=/usr/share/prometheus/consoles'
  ports:
    - "9090:9090"
  restart: always

# Grafana konfigürasyonu
grafana:
  image: grafana/grafana:latest
  volumes:
    - grafana_data:/var/lib/grafana
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=your_secure_password
    - GF_USERS_ALLOW_SIGN_UP=false
  ports:
    - "3000:3000"
  restart: always
```

## 5. Güvenlik En İyi Uygulamaları

### 5.1 Sistem Güvenliği

```bash
# Fail2ban yapılandırması
sudo nano /etc/fail2ban/jail.local

[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

# ClamAV güncelleme ve tarama
sudo freshclam
sudo clamscan -r /path/to/finasis
```

### 5.2 Uygulama Güvenliği

```python
# settings/prod.py

# Güvenlik ayarları
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_KEY_PREFIX = 'ratelimit'

# Güvenli şifre politikası
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

## 6. Performans Optimizasyonu

### 6.1 Veritabanı Optimizasyonu

```sql
-- PostgreSQL optimizasyonları
ALTER SYSTEM SET max_connections = '200';
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET checkpoint_completion_target = '0.9';
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = '100';
ALTER SYSTEM SET random_page_cost = '1.1';
ALTER SYSTEM SET effective_io_concurrency = '200';
ALTER SYSTEM SET work_mem = '10485kB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';

-- Önemli indeksler
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_transactions_date ON transactions(transaction_date);
```

### 6.2 Önbellek Optimizasyonu

```python
# settings/prod.py

# Redis önbellek yapılandırması
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'RETRY_ON_TIMEOUT': True,
            'MAX_CONNECTIONS': 1000,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        }
    }
}

# Session backend
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

## 7. Ölçeklendirme Stratejisi

### 7.1 Yatay Ölçeklendirme

```yaml
# docker-compose.prod.yml

services:
  web:
    image: finasis-web:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    networks:
      - finasis-network
    depends_on:
      - redis
      - db

  celery:
    image: finasis-celery:latest
    deploy:
      replicas: 2
    networks:
      - finasis-network
    depends_on:
      - redis
      - db
```

### 7.2 Veritabanı Replikasyonu

```sql
-- Ana veritabanı
ALTER SYSTEM SET wal_level = replica;
ALTER SYSTEM SET max_wal_senders = 10;
ALTER SYSTEM SET max_replication_slots = 10;

-- Replika veritabanı
CREATE PUBLICATION finasis_publication FOR ALL TABLES;
CREATE SUBSCRIPTION finasis_subscription 
CONNECTION 'host=primary-db port=5432 dbname=finasis user=replicator password=secret' 
PUBLICATION finasis_publication;
```

## 8. Sorun Giderme

### 8.1 Yaygın Hatalar ve Çözümleri

1. **500 Internal Server Error**
   ```bash
   # Logları kontrol et
   docker-compose -f docker-compose.prod.yml logs -f web
   
   # DEBUG modunu geçici olarak aç
   docker-compose -f docker-compose.prod.yml exec web python manage.py shell
   >>> from django.conf import settings
   >>> settings.DEBUG = True
   ```

2. **Veritabanı Bağlantı Hataları**
   ```bash
   # PostgreSQL loglarını kontrol et
   docker-compose -f docker-compose.prod.yml logs -f db
   
   # Bağlantıyı test et
   docker-compose -f docker-compose.prod.yml exec db psql -U postgres -c "\l"
   ```

3. **Performans Sorunları**
   ```bash
   # Slow query loglarını kontrol et
   docker-compose -f docker-compose.prod.yml exec db psql -U postgres -c "SELECT * FROM pg_stat_activity WHERE state = 'active'"
   
   # Cache hit oranını kontrol et
   docker-compose -f docker-compose.prod.yml exec redis redis-cli info | grep hit_rate
   ```

## 9. Destek ve İletişim

Herhangi bir sorunla karşılaşırsanız, aşağıdaki kanallardan destek alabilirsiniz:

- **Email**: support@finasis.com.tr
- **Telefon**: +90 212 123 4567
- **Destek Portalı**: https://destek.finasis.com.tr
- **Slack Kanalı**: #finasis-support
- **Zamanlanmış Toplantı**: https://calendly.com/finasis-support

---

Bu rehber, FinAsis uygulamasının başarılı bir şekilde canlıya alınması için temel bilgileri içermektedir. Daha detaylı bilgi için teknik dokümantasyona bakabilirsiniz: `docs/` klasörü 