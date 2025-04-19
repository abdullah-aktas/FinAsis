# FinAsis Dağıtım Kılavuzu

Bu belge, FinAsis uygulamasını canlı ortama dağıtmak için gerekli adımları açıklar.

## Gereksinimler

- Linux sunucu (Ubuntu 20.04 LTS veya CentOS 8 önerilir)
- Python 3.9+
- PostgreSQL 13+
- Nginx veya Apache
- Redis (önbellek ve kuyruk için)
- SSL sertifikası (Let's Encrypt önerilir)

## 1. Sunucu Hazırlığı

### Sistem Paketlerini Yükleme (Ubuntu 20.04)

```bash
# Sistemi güncelle
sudo apt update
sudo apt upgrade -y

# Gerekli paketleri yükle
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx redis-server supervisor git

# Python geliştirme araçları
sudo apt install -y build-essential libpq-dev python3-dev
```

## 2. PostgreSQL Veritabanı Kurulumu

```bash
# PostgreSQL servisinin çalıştığından emin ol
sudo systemctl status postgresql

# Veritabanı ve kullanıcı oluştur
sudo -u postgres psql -c "CREATE DATABASE finasis;"
sudo -u postgres psql -c "CREATE USER finasisuser WITH PASSWORD 'gucluparola';"
sudo -u postgres psql -c "ALTER ROLE finasisuser SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE finasisuser SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE finasisuser SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE finasis TO finasisuser;"
```

## 3. Uygulama Kurulumu

```bash
# Uygulama için bir dizin oluştur
sudo mkdir -p /var/www/finasis
sudo chown $USER:$USER /var/www/finasis

# Uygulamayı Git repo'sundan çek
cd /var/www/finasis
git clone https://github.com/abdullah-aktas/FinAsis.git .

# Sanal ortam oluştur ve etkinleştir
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Statik dosyaları topla
python manage.py collectstatic --noinput
```

## 4. Ortam Değişkenleri

`.env` dosyası oluşturun:

```bash
cat > .env << EOL
DEBUG=False
SECRET_KEY=random_secure_key_here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=finasis
DB_USER=finasisuser
DB_PASSWORD=gucluparola
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourmailprovider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@yourdomain.com
EMAIL_HOST_PASSWORD=your_email_password

# Redis
REDIS_URL=redis://localhost:6379/0
EOL
```

## 5. Django Uygulamasını Yapılandırma

```bash
# Veritabanı tablolarını oluştur
python manage.py migrate

# Admin kullanıcısı oluştur
python manage.py createsuperuser

# Uygulama ayarlarını kontrol et
python manage.py check --deploy
```

## 6. Gunicorn Yapılandırması

Supervisor konfigürasyon dosyası oluşturun:

```bash
sudo nano /etc/supervisor/conf.d/finasis.conf
```

Aşağıdaki içeriği ekleyin:

```ini
[program:finasis]
directory=/var/www/finasis
command=/var/www/finasis/venv/bin/gunicorn config.wsgi:application --workers 3 --bind 127.0.0.1:8000
autostart=true
autorestart=true
user=www-data
environment=PATH="/var/www/finasis/venv/bin"
stdout_logfile=/var/log/finasis/gunicorn.log
stderr_logfile=/var/log/finasis/gunicorn-error.log
```

Log dizinini oluşturun ve Supervisor'ı yeniden başlatın:

```bash
sudo mkdir -p /var/log/finasis
sudo chown www-data:www-data /var/log/finasis
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status finasis
```

## 7. Nginx Yapılandırması

```bash
sudo nano /etc/nginx/sites-available/finasis
```

Aşağıdaki içeriği ekleyin:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/finasis;
    }

    location /media/ {
        root /var/www/finasis;
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Nginx yapılandırmasını etkinleştirin:

```bash
sudo ln -s /etc/nginx/sites-available/finasis /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 8. SSL Sertifikası (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 9. Firewall Yapılandırması

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable
sudo ufw status
```

## 10. Veritabanı Yedekleme

Günlük yedekleme için cron işi oluşturun:

```bash
sudo crontab -e
```

Aşağıdaki satırı ekleyin:

```
0 2 * * * pg_dump -U finasisuser finasis | gzip > /var/backups/finasis/finasis_$(date +'%Y%m%d').sql.gz
```

## 11. Uygulamayı Güncelleme

Uygulama güncellemeleri için:

```bash
cd /var/www/finasis
source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart finasis
```

## Sorun Giderme

### Gunicorn Çalışmıyor

```bash
sudo tail -f /var/log/finasis/gunicorn-error.log
```

### Nginx Sorunları

```bash
sudo tail -f /var/log/nginx/error.log
```

### Django İzinleri

```bash
sudo chown -R www-data:www-data /var/www/finasis
sudo chmod -R 755 /var/www/finasis
```

## Performans İyileştirmeleri

### Nginx Önbellek Yapılandırması

```nginx
location /static/ {
    root /var/www/finasis;
    expires 30d;
    add_header Cache-Control "public, max-age=2592000";
}
```

### PostgreSQL Performans Ayarları

`/etc/postgresql/13/main/postgresql.conf` dosyasına şu ayarları ekleyin:

```
shared_buffers = 256MB
work_mem = 8MB
maintenance_work_mem = 64MB
effective_cache_size = 1GB
``` 