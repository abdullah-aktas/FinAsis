# FinAsis Kurulum Kılavuzu

Bu belge, FinAsis finansal yönetim sisteminin kurulum adımlarını detaylı olarak açıklamaktadır.

## Sistem Gereksinimleri

- Python 3.8+
- PostgreSQL 13+
- Node.js 14+
- npm 6+
- Redis 6+ (görev kuyruğu için)

## Geliştirme Ortamı Kurulumu

### 1. Projeyi Klonlayın

```bash
git clone https://github.com/your-organization/finasis.git
cd finasis
```

### 2. Python Sanal Ortamı Oluşturun

```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Python Bağımlılıklarını Yükleyin

```bash
pip install -r requirements.txt
```

### 4. Ortam Değişkenlerini Yapılandırın

```bash
cp .env.example .env
```

`.env` dosyasını kendi ortam değişkenlerinizle güncelleyin:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Veritabanı
DATABASE_URL=postgres://username:password@localhost:5432/finasis

# Django Ayarları
LANGUAGE_CODE=tr
TIME_ZONE=Europe/Istanbul

# E-Fatura API
EFATURA_API_URL=https://test-efatura-api.example.com
EFATURA_API_KEY=your-test-key
EFATURA_TEST_MODE=True

# Banka API
BANK_API_URL=https://test-bank-api.example.com
BANK_API_KEY=your-test-key
BANK_API_TEST_MODE=True

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@example.com
```

### 5. Veritabanını Hazırlayın

```bash
# PostgreSQL veritabanı oluşturun
createdb finasis

# Tabloları oluşturun
python manage.py migrate
```

### 6. Frontend Bağımlılıklarını Yükleyin

```bash
npm install
```

### 7. Statik Dosyaları Derleyin

```bash
npm run build
python manage.py collectstatic
```

### 8. Süper Kullanıcı Oluşturun

```bash
python manage.py createsuperuser
```

### 9. Geliştirme Sunucusunu Başlatın

```bash
python manage.py runserver
```

## Docker ile Kurulum

### 1. Docker Compose Dosyasını Hazırlayın

```bash
cp .env.example .env.docker
```

`.env.docker` dosyasını düzenleyin:

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Veritabanı
DATABASE_URL=postgres://postgres:postgres@db:5432/finasis

# Django Ayarları
LANGUAGE_CODE=tr
TIME_ZONE=Europe/Istanbul

# E-Fatura API
EFATURA_API_URL=https://efatura-api.example.com
EFATURA_API_KEY=your-production-key
EFATURA_TEST_MODE=False

# Banka API
BANK_API_URL=https://bank-api.example.com
BANK_API_KEY=your-production-key
BANK_API_TEST_MODE=False

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@example.com
```

### 2. Docker Compose ile Çalıştırın

```bash
docker-compose up -d
```

### 3. Veritabanını Hazırlayın

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 4. Statik Dosyaları Toplayın

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

## Üretim Ortamı Yapılandırması

### 1. Güvenlik Ayarları

Üretim ortamında aşağıdaki güvenlik ayarlarını yapmanız önerilir:

1. `.env` dosyasında `DEBUG=False` olarak ayarlayın
2. `SECRET_KEY` için güçlü bir anahtar oluşturun
3. `ALLOWED_HOSTS` değerine sadece gerçek alan adlarınızı ekleyin
4. HTTPS yapılandırması için Nginx/Apache ters proxy kullanın
5. Güvenlik başlıklarını aktif edin (Nginx veya Django security middleware)

### 2. Nginx Yapılandırması

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # HTTP'yi HTTPS'ye yönlendir
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com www.your-domain.com;
    
    ssl_certificate /path/to/your-domain.crt;
    ssl_certificate_key /path/to/your-domain.key;
    
    # SSL ayarları
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    
    # Güvenlik başlıkları
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    
    # Statik ve medya dosyaları
    location /static/ {
        alias /path/to/finasis/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias /path/to/finasis/media/;
        expires 30d;
    }
    
    # Proxy yapılandırması
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Gunicorn Servis Yapılandırması

`/etc/systemd/system/finasis.service` dosyasını oluşturun:

```ini
[Unit]
Description=FinAsis Gunicorn Daemon
Requires=finasis.socket
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/finasis
ExecStart=/path/to/finasis/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/run/finasis.sock \
    core.wsgi:application
Environment="PATH=/path/to/finasis/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=core.settings"
EnvironmentFile=/path/to/finasis/.env.prod

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/finasis.socket` dosyasını oluşturun:

```ini
[Unit]
Description=FinAsis Gunicorn Socket

[Socket]
ListenStream=/run/finasis.sock
SocketUser=www-data
SocketGroup=www-data
SocketMode=0660

[Install]
WantedBy=sockets.target
```

Servisi etkinleştirin ve başlatın:

```bash
sudo systemctl enable finasis.socket
sudo systemctl start finasis.socket
sudo systemctl enable finasis.service
sudo systemctl start finasis.service
```

## Yedekleme Stratejisi

### Veritabanı Yedekleme Betiği

Otomatik veritabanı yedeklemesi için `/path/to/finasis/scripts/backup.sh` betiği oluşturun:

```bash
#!/bin/bash

# Yapılandırma
BACKUP_DIR="/path/to/backups"
DB_NAME="finasis"
DB_USER="postgres"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/$DB_NAME-$DATE.sql"

# Yedekleme klasörünü oluştur
mkdir -p $BACKUP_DIR

# Veritabanını yedekle
pg_dump -U $DB_USER $DB_NAME > $BACKUP_FILE

# Sıkıştır
gzip $BACKUP_FILE

# 30 günden eski yedeklemeleri temizle
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +30 -delete

# Uzak sunucuya kopyala (opsiyonel)
# rsync -avz $BACKUP_DIR/* user@remote-server:/path/to/backup/
```

Cron görevi ekleyin:

```bash
# Her gece 02:00'de yedekleme yap
0 2 * * * /path/to/finasis/scripts/backup.sh >> /var/log/finasis-backup.log 2>&1
```

## Sorun Giderme

### Yaygın Hatalar ve Çözümleri

1. **Veritabanı Bağlantı Hatası**
   ```
   django.db.utils.OperationalError: could not connect to server: Connection refused
   ```
   
   Çözüm:
   - PostgreSQL servisinin çalıştığını kontrol edin: `sudo systemctl status postgresql`
   - Veritabanı kullanıcı adı ve şifresinin doğru olduğunu kontrol edin
   - Veritabanının oluşturulduğunu kontrol edin: `sudo -u postgres psql -c "\l"`

2. **Statik Dosyalar Yüklenmiyor**
   
   Çözüm:
   - `python manage.py collectstatic --noinput` komutunu çalıştırın
   - Nginx yapılandırmasındaki statik dosya yolunu kontrol edin
   - `STATIC_ROOT` ve `STATIC_URL` ayarlarını kontrol edin

3. **Migrate Hataları**
   
   Çözüm:
   - Sıfırdan başlayın: `python manage.py migrate --fake-initial`
   - Sorunlu uygulamayı belirleyin ve o uygulamanın migrate işlemini atlayın

4. **Performans Sorunları**
   
   Çözüm:
   - Gunicorn worker sayısını artırın (CPU çekirdek sayısı * 2 + 1)
   - Django debug toolbar ile yavaş sorguları analiz edin
   - PostgreSQL performans ayarlarını iyileştirin

### Kayıt Dosyaları (Logs)

Sorun giderme için aşağıdaki log dosyalarını kontrol edin:

- Django log: `/path/to/finasis/logs/django.log`
- Nginx erişim log: `/var/log/nginx/access.log`
- Nginx hata log: `/var/log/nginx/error.log`
- Gunicorn log: `/var/log/finasis/gunicorn.log`

## Güncellemeler ve Bakım

### Sistem Güncelleme Prosedürü

1. Yedekleme yapın
   ```bash
   /path/to/finasis/scripts/backup.sh
   ```

2. Kodu güncelleyin
   ```bash
   cd /path/to/finasis
   git pull origin main
   ```

3. Sanal ortamı etkinleştirin
   ```bash
   source venv/bin/activate
   ```

4. Bağımlılıkları güncelleyin
   ```bash
   pip install -r requirements.txt
   ```

5. Veritabanını migrate edin
   ```bash
   python manage.py migrate
   ```

6. Statik dosyaları derleyin
   ```bash
   npm run build
   python manage.py collectstatic --noinput
   ```

7. Servisleri yeniden başlatın
   ```bash
   sudo systemctl restart finasis.service
   ``` 