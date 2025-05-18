# FinAsis Kurulum ve Dağıtım Kılavuzu

Bu belge, FinAsis uygulamasının kurulum, yapılandırma ve dağıtım adımlarını içerir.

## İçindekiler

1. [Gereksinimler](#gereksinimler)
2. [Geliştirme Ortamı Kurulumu](#geliştirme-ortamı-kurulumu)
3. [Üretim Ortamı Kurulumu](#üretim-ortamı-kurulumu)
4. [Veritabanı Kurulumu](#veritabanı-kurulumu)
5. [Ortam Değişkenleri](#ortam-değişkenleri)
6. [Komutlar ve İşlemler](#komutlar-ve-işlemler)
7. [Sorun Giderme](#sorun-giderme)

## Gereksinimler

### Yazılım Gereksinimleri

- Python 3.10 veya üstü
- PostgreSQL 14 veya üstü
- Node.js 18 veya üstü
- Redis 6 veya üstü
- Nginx (üretim ortamında)
- Git

### Donanım Gereksinimleri

- **Geliştirme Ortamı**: En az 4GB RAM, 2 çekirdekli işlemci, 10GB disk alanı
- **Üretim Ortamı**: En az 8GB RAM, 4 çekirdekli işlemci, 50GB disk alanı

## Geliştirme Ortamı Kurulumu

1. Depoyu klonlayın:

```bash
git clone https://github.com/finasis/finasis.git
cd finasis
```

2. Sanal ortam oluşturun ve bağımlılıkları yükleyin:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

3. Ortam değişkenlerini ayarlayın:

```bash
cp .env.example .env
# .env dosyasını düzenleyin ve gerekli değişkenleri ayarlayın
```

4. Veritabanını oluşturun:

```bash
python manage.py migrate
```

5. Test verileri yükleyin (isteğe bağlı):

```bash
python manage.py loaddata fixtures/initial_data.json
```

6. Statik dosyaları toplayın:

```bash
python manage.py collectstatic
```

7. Geliştirme sunucusunu başlatın:

```bash
python manage.py runserver
```

## Üretim Ortamı Kurulumu

### Docker İle Kurulum

1. Docker ve Docker Compose'u yükleyin:

```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
```

2. Docker Compose dosyasını çalıştırın:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Manuel Kurulum

1. Bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

2. Ortam değişkenlerini ayarlayın:

```bash
cp .env.example .env.prod
# .env.prod dosyasını düzenleyin ve değişkenleri ayarlayın
```

3. Gunicorn için servis dosyası oluşturun:

```bash
# /etc/systemd/system/finasis.service
[Unit]
Description=FinAsis Gunicorn Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/finasis
ExecStart=/path/to/finasis/venv/bin/gunicorn config.wsgi:application --workers 4 --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```

4. Nginx yapılandırması:

```nginx
# /etc/nginx/sites-available/finasis
server {
    listen 80;
    server_name finasis.com www.finasis.com;

    location /static/ {
        alias /path/to/finasis/staticfiles/;
    }

    location /media/ {
        alias /path/to/finasis/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

5. Servisleri başlatın:

```bash
sudo systemctl start finasis
sudo systemctl enable finasis
sudo ln -s /etc/nginx/sites-available/finasis /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

## Veritabanı Kurulumu

1. PostgreSQL kurulumu:

```bash
sudo apt-get install postgresql postgresql-contrib
```

2. Veritabanı ve kullanıcı oluşturma:

```bash
sudo -u postgres psql
postgres=# CREATE DATABASE finasis;
postgres=# CREATE USER finasisuser WITH PASSWORD 'password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE finasis TO finasisuser;
postgres=# \q
```

## Ortam Değişkenleri

FinAsis uygulaması için aşağıdaki ortam değişkenlerini ayarlamanız gerekir:

| Değişken | Açıklama | Örnek Değer |
|----------|----------|-------------|
| DJANGO_SECRET_KEY | Django güvenlik anahtarı | somerandomstring |
| DJANGO_DEBUG | Debug modu | True/False |
| DJANGO_ALLOWED_HOSTS | İzin verilen host adresleri | localhost,finasis.com |
| DB_NAME | Veritabanı adı | finasis |
| DB_USER | Veritabanı kullanıcısı | finasisuser |
| DB_PASSWORD | Veritabanı şifresi | password |
| DB_HOST | Veritabanı sunucusu | localhost |
| DB_PORT | Veritabanı portu | 5432 |
| EMAIL_HOST | SMTP sunucusu | smtp.gmail.com |
| EMAIL_PORT | SMTP portu | 587 |
| EMAIL_HOST_USER | SMTP kullanıcısı | email@example.com |
| EMAIL_HOST_PASSWORD | SMTP şifresi | password |
| REDIS_URL | Redis bağlantı URL'si | redis://localhost:6379/0 |

## Komutlar ve İşlemler

### Veritabanı İşlemleri

```bash
# Migrasyon oluşturma
python manage.py makemigrations

# Migrasyon uygulama
python manage.py migrate

# Veritabanı yedekleme
python manage.py dumpdata > backup.json

# Veritabanı geri yükleme
python manage.py loaddata backup.json
```

### Admin Kullanıcısı Oluşturma

```bash
python manage.py createsuperuser
```

### Çeviri Dosyaları

```bash
# Çeviri dosyalarını güncelleme
python manage.py makemessages -l tr

# Çeviri dosyalarını derleme
python manage.py compilemessages
```

### Statik Dosyalar

```bash
# Statik dosyaları toplama
python manage.py collectstatic
```

### Test Çalıştırma

```bash
# Tüm testleri çalıştırma
python manage.py test

# Belirli bir uygulamanın testlerini çalıştırma
python manage.py test apps.users
```

## Sorun Giderme

### Sık Karşılaşılan Hatalar

1. **Veritabanı Bağlantı Hatası**
   - PostgreSQL servisinin çalıştığından emin olun
   - Veritabanı kimlik bilgilerini kontrol edin
   - PostgreSQL loglarını kontrol edin

2. **Statik Dosya Yükleme Sorunu**
   - `collectstatic` komutunu çalıştırdığınızdan emin olun
   - Nginx yapılandırmasını kontrol edin
   - Dosya izinlerini kontrol edin

3. **500 Sunucu Hatası**
   - Django log dosyalarını kontrol edin
   - DEBUG modunu geçici olarak etkinleştirin
   - Nginx error loglarını kontrol edin

### Logları Kontrol Etme

```bash
# Django logları
tail -f logs/django.log

# Nginx error logları
sudo tail -f /var/log/nginx/error.log

# PostgreSQL logları
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

## Güvenlik Notları

- Üretim ortamında `DEBUG = False` olarak ayarlanmalıdır
- Hassas bilgiler için ortam değişkenleri kullanın, kod içinde saklamayın
- PostgreSQL yapılandırmasında güvenlik önlemlerini alın
- Düzenli olarak güvenlik güncellemelerini yapın
- HTTPS kullanımını zorunlu kılın
- Güçlü parolalar kullanın ve düzenli olarak değiştirin

---

© 2023 FinAsis Yazılım A.Ş. Tüm hakları saklıdır. 