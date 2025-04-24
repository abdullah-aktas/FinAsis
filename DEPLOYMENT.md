# FinAsis Deployment Rehberi

Bu rehber, FinAsis uygulamasının çeşitli platformlarda (Turhost, Google Cloud, AWS, Azure) nasıl çalıştırılacağını ve yönetileceğini açıklamaktadır.

## İçindekiler

1. [Gereksinimler](#gereksinimler)
2. [Güvenlik Kontrolleri](#güvenlik-kontrolleri)
3. [Turhost'ta Deployment](#turhostta-deployment)
4. [Google Cloud'da Deployment](#google-cloudda-deployment)
5. [AWS'de Deployment](#awsde-deployment)
6. [Azure'da Deployment](#azureda-deployment)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Monitoring ve Logging](#monitoring-ve-logging)
9. [Backup ve Recovery](#backup-ve-recovery)
10. [Performans Optimizasyonu](#performans-optimizasyonu)
11. [SLA ve Uptime](#sla-ve-uptime)

## Gereksinimler

### Minimum Gereksinimler
- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- Nginx 1.18+
- Docker 20.10+
- Docker Compose 2.0+

### Önerilen Gereksinimler
- 4+ CPU çekirdeği
- 8GB+ RAM
- 50GB+ SSD depolama
- 100Mbps+ ağ bağlantısı

### Yazılım Gereksinimleri
- Git 2.30+
- Node.js 16+ (frontend için)
- Yarn 1.22+ (frontend için)
- Certbot (SSL sertifikaları için)
- UFW (güvenlik duvarı için)
- Fail2ban (brute force koruması için)

## Güvenlik Kontrolleri

### Ön Dağıtım Kontrolleri
```bash
# Güvenlik taraması
python manage.py check --deploy

# Bağımlılık güvenlik kontrolü
safety check

# Kod kalitesi kontrolü
flake8 .
black --check .
mypy .
```

### Güvenlik Yapılandırmaları
```bash
# UFW kuralları
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# Fail2ban kurulumu
sudo apt-get install fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```

## Turhost'ta Deployment

### 1. Sistem Hazırlığı

```bash
# Sistem güncellemeleri
sudo apt update && sudo apt upgrade -y

# Gerekli paketler
sudo apt install -y python3-pip python3-venv nginx redis-server postgresql postgresql-contrib certbot python3-certbot-nginx ufw fail2ban

# Docker kurulumu
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

### 2. Uygulama Kurulumu

```bash
# Uygulama dizini
sudo mkdir -p /var/www/finasis
sudo chown $USER:$USER /var/www/finasis
cd /var/www/finasis

# Git ile klonlama
git clone https://github.com/kullaniciadi/finasis.git .

# Virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Bağımlılıklar
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 3. Veritabanı Yapılandırması

```bash
# PostgreSQL kullanıcı ve veritabanı oluşturma
sudo -u postgres psql
CREATE DATABASE finasis_db;
CREATE USER finasis_user WITH PASSWORD 'guclu_sifre';
GRANT ALL PRIVILEGES ON DATABASE finasis_db TO finasis_user;
ALTER USER finasis_user CREATEDB;
```

### 4. Çevre Değişkenleri

`.env` dosyası:

```ini
# Django
DJANGO_SETTINGS_MODULE=config.settings.prod
DJANGO_SECRET_KEY=guclu_bir_secret_key_girin
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=finasis.com.tr,www.finasis.com.tr
DJANGO_CSRF_TRUSTED_ORIGINS=https://finasis.com.tr,https://www.finasis.com.tr

# Veritabanı
DB_ENGINE=django.db.backends.postgresql
DB_NAME=finasis_db
DB_USER=finasis_user
DB_PASSWORD=guclu_sifre
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_URL=redis://localhost:6379/1
REDIS_QUEUE_URL=redis://localhost:6379/2

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=user@example.com
EMAIL_HOST_PASSWORD=email_sifre
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=user@example.com

# Güvenlik
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY

# Monitoring
SENTRY_DSN=https://sentry.io/your-dsn
PROMETHEUS_METRICS=True
```

### 5. Gunicorn Yapılandırması

`gunicorn.conf.py`:

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 2
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
```

### 6. Systemd Servisleri

`/etc/systemd/system/finasis.service`:

```ini
[Unit]
Description=FinAsis Gunicorn Service
After=network.target postgresql.service redis-server.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/finasis
Environment="PATH=/var/www/finasis/.venv/bin"
EnvironmentFile=/var/www/finasis/.env
ExecStart=/var/www/finasis/.venv/bin/gunicorn config.wsgi:application --config gunicorn.conf.py
Restart=on-failure
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/finasis-celery.service`:

```ini
[Unit]
Description=FinAsis Celery Service
After=network.target postgresql.service redis-server.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/finasis
Environment="PATH=/var/www/finasis/.venv/bin"
EnvironmentFile=/var/www/finasis/.env
ExecStart=/var/www/finasis/.venv/bin/celery -A config worker -l info
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 7. Nginx Yapılandırması

`/etc/nginx/sites-available/finasis`:

```nginx
# HTTP sunucusu
server {
    listen 80;
    server_name finasis.com.tr www.finasis.com.tr;
    return 301 https://$host$request_uri;
}

# HTTPS sunucusu
server {
    listen 443 ssl http2;
    server_name finasis.com.tr www.finasis.com.tr;

    # SSL sertifikaları
    ssl_certificate /etc/letsencrypt/live/finasis.com.tr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/finasis.com.tr/privkey.pem;
    
    # SSL yapılandırması
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # OCSP Stapling
    ssl_trusted_certificate /etc/letsencrypt/live/finasis.com.tr/chain.pem;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    
    # Güvenlik başlıkları
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.finasis.com.tr; frame-ancestors 'none';" always;
    
    # Gzip sıkıştırma
    gzip on;
    gzip_comp_level 5;
    gzip_min_length 256;
    gzip_proxied any;
    gzip_vary on;
    gzip_types
        application/atom+xml
        application/javascript
        application/json
        application/ld+json
        application/manifest+json
        application/rss+xml
        application/vnd.geo+json
        application/vnd.ms-fontobject
        application/x-font-ttf
        application/x-web-app-manifest+json
        application/xhtml+xml
        application/xml
        font/opentype
        image/bmp
        image/svg+xml
        image/x-icon
        text/cache-manifest
        text/css
        text/plain
        text/vcard
        text/vnd.rim.location.xloc
        text/vtt
        text/x-component
        text/x-cross-domain-policy;
    
    # Brotli sıkıştırma
    brotli on;
    brotli_comp_level 6;
    brotli_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Statik dosyalar
    location /static/ {
        alias /var/www/finasis/staticfiles/;
        expires 1M;
        access_log off;
        add_header Cache-Control "public";
        add_header X-Content-Type-Options nosniff;
    }
    
    # Medya dosyaları
    location /media/ {
        alias /var/www/finasis/media/;
        expires 1M;
        access_log off;
        add_header Cache-Control "public";
        add_header X-Content-Type-Options nosniff;
    }
    
    # Proxy ayarları
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 75s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
        proxy_temp_file_write_size 8k;
        proxy_redirect off;
    }
    
    # Hata sayfaları
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

### 8. SSL Sertifikası

```bash
# Let's Encrypt sertifikası al
sudo certbot --nginx -d finasis.com.tr -d www.finasis.com.tr

# Otomatik yenileme kontrolü
sudo systemctl status certbot.timer
```

## Google Cloud'da Deployment

### 1. App Engine Yapılandırması

`app.yaml`:

```yaml
runtime: python310
env: flex

env_variables:
  DJANGO_SETTINGS_MODULE: "config.settings.prod"
  DJANGO_SECRET_KEY: "guclu_bir_secret_key_girin"
  DJANGO_DEBUG: "False"
  DJANGO_ALLOWED_HOSTS: "finasis.com.tr,www.finasis.com.tr"
  
  # Cloud SQL
  DB_ENGINE: "django.db.backends.postgresql"
  DB_NAME: "finasis_db"
  DB_USER: "postgres"
  DB_PASSWORD: "veritabani_sifre"
  DB_HOST: "/cloudsql/your-project-id:region:instance-name"
  DB_PORT: ""
  
  # Memorystore
  REDIS_URL: "redis://10.0.0.1:6379/0"
  REDIS_CACHE_URL: "redis://10.0.0.1:6379/1"
  REDIS_QUEUE_URL: "redis://10.0.0.1:6379/2"

automatic_scaling:
  min_instances: 1
  max_instances: 5
  min_idle_instances: 1
  max_idle_instances: 1
  min_pending_latency: 30ms
  max_pending_latency: 200ms
  target_cpu_utilization: 0.65
  target_throughput_utilization: 0.6

resources:
  cpu: 1
  memory_gb: 2
  disk_size_gb: 10

network:
  session_affinity: true
  forwarded_ports:
    - 8000

health_check:
  enable_health_check: true
  check_interval_sec: 5
  timeout_sec: 4
  unhealthy_threshold: 2
  healthy_threshold: 2

liveness_check:
  path: "/health/"
  check_interval_sec: 30
  timeout_sec: 4
  failure_threshold: 2
  success_threshold: 2

readiness_check:
  path: "/ready/"
  check_interval_sec: 5
  timeout_sec: 4
  failure_threshold: 2
  success_threshold: 2

handlers:
- url: /static
  static_dir: staticfiles/
  secure: always
  http_headers:
    Strict-Transport-Security: "max-age=31536000; includeSubDomains; preload"
    X-Content-Type-Options: "nosniff"
    X-Frame-Options: "DENY"
    X-XSS-Protection: "1; mode=block"

- url: /media
  static_dir: media/
  secure: always
  http_headers:
    Strict-Transport-Security: "max-age=31536000; includeSubDomains; preload"
    X-Content-Type-Options: "nosniff"
    X-Frame-Options: "DENY"
    X-XSS-Protection: "1; mode=block"

- url: /.*
  script: auto
  secure: always
  http_headers:
    Strict-Transport-Security: "max-age=31536000; includeSubDomains; preload"
    X-Content-Type-Options: "nosniff"
    X-Frame-Options: "DENY"
    X-XSS-Protection: "1; mode=block"

entrypoint: gunicorn -b :$PORT config.wsgi:application --timeout=120 --workers=2 --threads=2
```

## AWS'de Deployment

### 1. ECS Task Definition

```json
{
  "family": "finasis",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account-id:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account-id:role/finasisTaskRole",
  "containerDefinitions": [
    {
      "name": "finasis",
      "image": "account-id.dkr.ecr.region.amazonaws.com/finasis:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DJANGO_SETTINGS_MODULE",
          "value": "config.settings.prod"
        }
      ],
      "secrets": [
        {
          "name": "DJANGO_SECRET_KEY",
          "valueFrom": "arn:aws:ssm:region:account-id:parameter/finasis/django-secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/finasis",
          "awslogs-region": "region",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health/ || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

## Azure'da Deployment

### 1. App Service Yapılandırması

`azure-pipelines.yml`:

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: finasis-variables

steps:
- task: Docker@2
  inputs:
    containerRegistry: 'finasis-registry'
    repository: 'finasis'
    command: 'buildAndPush'
    Dockerfile: 'Dockerfile'
    tags: '$(Build.BuildId)'

- task: AzureWebApp@1
  inputs:
    azureSubscription: 'finasis-subscription'
    appType: 'webAppLinux'
    appName: 'finasis'
    runtimeStack: 'PYTHON|3.10'
    startupCommand: 'gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2'
    appSettings: |
      [
        {
          "name": "DJANGO_SETTINGS_MODULE",
          "value": "config.settings.prod",
          "slotSetting": false
        }
      ]
```

## CI/CD Pipeline

### GitHub Actions

`.github/workflows/deploy.yml`:

```yaml
name: Deploy FinAsis

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8 black mypy
          
      - name: Run tests
        run: |
          pytest --cov=apps tests/
          
      - name: Run linting
        run: |
          flake8 .
          black --check .
          mypy .
          
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1
      
      - name: Login to DockerHub
        uses: docker/login-action@v1
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
          
      - name: Build and push
        uses: docker/build-push-action@v2
        with:
          context: .
          push: true
          tags: finasis:latest
          
      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USERNAME }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /var/www/finasis
            git pull
            docker-compose pull
            docker-compose up -d
```

## Monitoring ve Logging

### Prometheus Yapılandırması

`prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'finasis'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
      
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "id": null,
    "title": "FinAsis Monitoring",
    "tags": ["finasis", "django"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "rate(django_http_requests_total[5m])",
            "legendFormat": "{{handler}}"
          }
        ]
      }
    ]
  }
}
```

## Backup ve Recovery

### Veritabanı Yedekleme

```bash
#!/bin/bash
# backup.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/finasis/$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

# PostgreSQL yedekleme
pg_dump -U finasis_user -d finasis_db | gzip > "$BACKUP_DIR/db.sql.gz"

# Medya dosyaları
tar -czf "$BACKUP_DIR/media.tar.gz" /var/www/finasis/media

# Statik dosyalar
tar -czf "$BACKUP_DIR/static.tar.gz" /var/www/finasis/staticfiles

# Yedekleri S3'e yükle
aws s3 sync "$BACKUP_DIR" "s3://finasis-backups/$TIMESTAMP"

# Eski yedekleri temizle
find /backups/finasis -type d -mtime +7 -exec rm -rf {} \;
```

### Kurtarma Prosedürü

```bash
#!/bin/bash
# restore.sh

BACKUP_DIR=$1
if [ -z "$BACKUP_DIR" ]; then
    echo "Yedek dizini belirtilmedi!"
    exit 1
fi

# Veritabanını geri yükle
gunzip -c "$BACKUP_DIR/db.sql.gz" | psql -U finasis_user -d finasis_db

# Medya dosyalarını geri yükle
tar -xzf "$BACKUP_DIR/media.tar.gz" -C /var/www/finasis

# Statik dosyaları geri yükle
tar -xzf "$BACKUP_DIR/static.tar.gz" -C /var/www/finasis

# Servisleri yeniden başlat
systemctl restart finasis
systemctl restart finasis-celery
```

## Performans Optimizasyonu

### PostgreSQL Ayarları

`/etc/postgresql/12/main/postgresql.conf`:

```ini
# Bellek ayarları
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
work_mem = 16MB

# Write-ahead log
wal_buffers = 16MB
checkpoint_completion_target = 0.9
max_wal_size = 2GB
min_wal_size = 1GB

# Performans
random_page_cost = 1.1
effective_io_concurrency = 200
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
```

### Redis Ayarları

`/etc/redis/redis.conf`:

```ini
# Bellek yönetimi
maxmemory 2gb
maxmemory-policy allkeys-lru

# Kalıcılık
save 900 1
save 300 10
save 60 10000

# Performans
tcp-keepalive 300
timeout 0
tcp-backlog 511
```

## SLA ve Uptime

### Uptime Hedefleri
- Yıllık Uptime: %99.95
- Aylık İzin Verilen Kesinti: 21.6 dakika
- Haftalık İzin Verilen Kesinti: 5.04 dakika
- Günlük İzin Verilen Kesinti: 43.2 saniye

### Monitoring Metrikleri
- Response Time: < 200ms
- Error Rate: < 0.1%
- CPU Kullanımı: < 70%
- Bellek Kullanımı: < 80%
- Disk Kullanımı: < 85%

### Alerting Kuralları
```yaml
groups:
- name: finasis
  rules:
  - alert: HighErrorRate
    expr: rate(django_http_requests_total{status=~"5.."}[5m]) / rate(django_http_requests_total[5m]) > 0.01
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Yüksek hata oranı"
      description: "5xx hata oranı %1'in üzerinde"

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(django_http_requests_latency_seconds_bucket[5m])) > 0.5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Yüksek yanıt süresi"
      description: "95. yüzdelik yanıt süresi 500ms'nin üzerinde"
``` 