# FinAsis Deployment Rehberi

Bu rehber, FinAsis uygulamasının Turhost ve Google Cloud gibi platformlarda nasıl çalıştırılacağını açıklamaktadır.

## Gereksinimler

- Python 3.10+
- PostgreSQL 12+
- Redis (önbellek ve kuyruk için)
- Nginx (web sunucusu için)

## Turhost'ta Deployment

### 1. Uygulama Dosyalarını Yükleme

SSH ile sunucuya bağlanın ve uygulamayı yükleyin:

```bash
# SSH ile bağlan
ssh kullanici@sunucu_adresi

# Uygulama dizinine git
cd /var/www/finasis

# Uygulama dosyalarını indirme (git kullanarak)
git clone https://github.com/kullaniciadi/finasis.git .

# veya dosyaları FTP ile yükle
```

### 2. Virtual Environment Oluşturma

```bash
# Virtual environment oluştur
python3 -m venv .venv

# Aktive et
source .venv/bin/activate

# Gereksinimleri yükle
pip install -r requirements.txt
```

### 3. Çevre Değişkenleri

`.env` dosyası oluşturun ve aşağıdaki değişkenleri tanımlayın:

```
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.prod
DJANGO_SECRET_KEY=guclu_bir_secret_key_girin
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=finasis.com.tr,www.finasis.com.tr

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=finasis_db
DB_USER=veritabani_kullanici
DB_PASSWORD=veritabani_sifre
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=user@example.com
EMAIL_HOST_PASSWORD=email_sifre
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=user@example.com

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 4. Veritabanı Hazırlama

```bash
# Migrasyonları oluştur
python manage.py makemigrations

# Migrasyonları uygula
python manage.py migrate

# Statik dosyaları topla
python manage.py collectstatic --noinput

# Admin kullanıcı oluştur
python manage.py createsuperuser
```

### 5. Gunicorn ile Servis Etme

Gunicorn servis dosyası için `/etc/systemd/system/finasis.service` dosyası oluşturun:

```ini
[Unit]
Description=FinAsis Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/finasis
ExecStart=/var/www/finasis/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Servisi etkinleştirin ve başlatın:

```bash
sudo systemctl enable finasis
sudo systemctl start finasis
```

### 6. Nginx Yapılandırması

`/etc/nginx/sites-available/finasis` dosyası oluşturun:

```nginx
server {
    listen 80;
    server_name finasis.com.tr www.finasis.com.tr;
    
    # HTTP'yi HTTPS'ye yönlendir
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name finasis.com.tr www.finasis.com.tr;

    ssl_certificate /etc/letsencrypt/live/finasis.com.tr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/finasis.com.tr/privkey.pem;
    
    # SSL ayarları
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    
    # Güvenlik başlıkları
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:;";
    
    # Gzip sıkıştırma
    gzip on;
    gzip_comp_level 5;
    gzip_min_length 256;
    gzip_proxied any;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Medya ve statik dosyalar
    location /media/ {
        alias /var/www/finasis/media/;
        expires 1M;
        access_log off;
        add_header Cache-Control "public";
    }
    
    location /static/ {
        alias /var/www/finasis/staticfiles/;
        expires 1M;
        access_log off;
        add_header Cache-Control "public";
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
        proxy_redirect off;
    }
}
```

Nginx yapılandırmasını etkinleştirin:

```bash
sudo ln -s /etc/nginx/sites-available/finasis /etc/nginx/sites-enabled/
sudo nginx -t  # Yapılandırmayı test et
sudo systemctl restart nginx
```

## Google Cloud'da Deployment

### 1. App Engine Kullanarak Deployment

Google Cloud App Engine, Django uygulamanızı kolayca çalıştırmanızı sağlar.

#### app.yaml Oluşturma

Proje kök dizininde `app.yaml` dosyası oluşturun:

```yaml
runtime: python310

env_variables:
  DJANGO_SETTINGS_MODULE: "config.settings.prod"
  DJANGO_SECRET_KEY: "guclu_bir_secret_key_girin"
  DJANGO_DEBUG: "False"
  DJANGO_ALLOWED_HOSTS: "finasis.com.tr,www.finasis.com.tr"
  
  # Database Cloud SQL örneği
  DB_ENGINE: "django.db.backends.postgresql"
  DB_NAME: "finasis_db"
  DB_USER: "postgres"
  DB_PASSWORD: "veritabani_sifre"
  DB_HOST: "/cloudsql/your-project-id:region:instance-name"
  DB_PORT: ""
  
  # Redis memorystore
  REDIS_URL: "redis://10.0.0.1:6379/0"
  
  # Diğer ayarlar buraya eklenir

handlers:
- url: /static
  static_dir: staticfiles/
  secure: always

- url: /media
  static_dir: media/
  secure: always

- url: /.*
  script: auto
  secure: always

entrypoint: gunicorn -b :$PORT config.wsgi:application --timeout=120 --workers=2

automatic_scaling:
  min_instances: 1
  max_instances: 5
  min_idle_instances: 1
  max_idle_instances: 1
  min_pending_latency: 30ms
  max_pending_latency: 200ms
  target_cpu_utilization: 0.65
  target_throughput_utilization: 0.6

inbound_services:
- warmup
```

### 2. Google Cloud SQL'i Yapılandırma

1. Google Cloud Console'da bir PostgreSQL örneği oluşturun
2. Veritabanı bağlantı ayarlarını `app.yaml` dosyasında güncelleyin
3. Cloud SQL Proxy kullanarak yerel geliştirme ortamında bağlanın

### 3. Uygulamayı Dağıtma

Google Cloud SDK yüklü olmalıdır:

```bash
# Projeyi seç
gcloud config set project your-project-id

# Uygulamayı dağıt
gcloud app deploy app.yaml
```

### 4. Cloud Storage Entegrasyonu (Statik ve Medya dosyaları için)

Django'da Cloud Storage kullanımı için ayarları güncelleyin:

```python
# prod.py içinde

# Google Cloud Storage için
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'finasis-media'
GS_DEFAULT_ACL = 'publicRead'
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_STATIC_BUCKET_NAME = 'finasis-static'
```

## Önemli Notlar

1. **Güvenlik**:
   - SECRET_KEY güvenli bir şekilde saklanmalıdır
   - DEBUG her zaman False olmalıdır
   - ALLOWED_HOSTS doğru ayarlanmalıdır
   - Tüm yetkili dahiliye sertifikaları kurulmalıdır

2. **Veritabanı**:
   - Düzenli olarak yedeklemeler alınmalıdır
   - PostgreSQL performans ayarları optimize edilmelidir

3. **Redis**:
   - Önbellek ve kuyruk için redis ayarları yapılmalıdır
   - Redis bağlantı havuzu düzgün yapılandırılmalıdır

4. **Ölçeklendirme**:
   - Gunicorn worker sayısı CPU'ya göre ayarlanmalıdır
   - Static dosyalar CDN üzerinden sunulmalıdır

5. **İzleme ve Logging**:
   - Sentry kurulmalıdır
   - Prometheus/Grafana metrikleri yapılandırılmalıdır 