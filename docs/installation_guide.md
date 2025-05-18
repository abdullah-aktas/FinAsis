# FinAsis Kurulum Kılavuzu

*Son Güncelleme: 22.04.2025*

## 📋 Genel Bakış

Bu kılavuz, FinAsis uygulamasının kurulum sürecini adım adım açıklamaktadır.

## 🔧 Gereksinimler

### Donanım Gereksinimleri
- CPU: 4+ çekirdek
- RAM: 8GB+
- Depolama: 100GB+ SSD
- Ağ: 100Mbps+

### Yazılım Gereksinimleri
- İşletim Sistemi: Ubuntu 20.04 LTS veya CentOS 8
- Docker: 20.10+
- Docker Compose: 2.0+
- Git: 2.30+

## 📥 Kurulum

### 1. Kaynak Kodları İndirme
```bash
git clone https://github.com/finasis/finasis.git
cd finasis
```

### 2. Ortam Değişkenlerini Ayarlama
```bash
cp .env.example .env
nano .env
```

### 3. Docker Konteynerlerini Başlatma
```bash
docker-compose up -d
```

### 4. Veritabanı Migrasyonları
```bash
docker-compose exec web python manage.py migrate
```

### 5. Süper Kullanıcı Oluşturma
```bash
docker-compose exec web python manage.py createsuperuser
```

### 6. Statik Dosyaları Toplama
```bash
docker-compose exec web python manage.py collectstatic
```

## 🛠️ Yapılandırma

### 1. Veritabanı Ayarları
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'finasis',
        'USER': 'finasis',
        'PASSWORD': 'your_password',
        'HOST': 'db',
        'PORT': '5432',
    }
}
```

### 2. E-posta Ayarları
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_password'
```

### 3. Redis Ayarları
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## 🔍 Doğrulama

### 1. Uygulama Durumunu Kontrol Etme
```bash
docker-compose ps
```

### 2. Logları İnceleme
```bash
docker-compose logs -f
```

### 3. Test Çalıştırma
```bash
docker-compose exec web python manage.py test
```

## 🔒 Güvenlik

### 1. SSL Sertifikası Kurulumu
```bash
# Let's Encrypt ile sertifika alma
sudo apt-get install certbot
sudo certbot certonly --standalone -d yourdomain.com
```

### 2. Güvenlik Duvarı Yapılandırması
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Dosya İzinleri
```bash
sudo chown -R www-data:www-data /var/www/finasis
sudo chmod -R 755 /var/www/finasis
```

## 🔄 Güncelleme

### 1. Kaynak Kodları Güncelleme
```bash
git pull origin main
```

### 2. Docker Konteynerlerini Yeniden Başlatma
```bash
docker-compose down
docker-compose pull
docker-compose up -d
```

### 3. Veritabanı Migrasyonlarını Çalıştırma
```bash
docker-compose exec web python manage.py migrate
```

## 📈 Ölçeklendirme

### 1. Yatay Ölçeklendirme
```bash
docker-compose up -d --scale web=3
```

### 2. Dikey Ölçeklendirme
```bash
# docker-compose.yml dosyasında kaynak limitlerini ayarlayın
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## 🔧 Sorun Giderme

### 1. Logları Kontrol Etme
```bash
docker-compose logs web
docker-compose logs db
docker-compose logs redis
```

### 2. Veritabanı Bağlantısını Test Etme
```bash
docker-compose exec db psql -U finasis -d finasis
```

### 3. Redis Bağlantısını Test Etme
```bash
docker-compose exec redis redis-cli ping
```

## 📞 Destek

### İletişim
- E-posta: support@finasis.com
- Telefon: +90 850 123 45 67
- Dokümantasyon: docs.finasis.com

### SLA
- Yanıt süresi: 24 saat
- Çözüm süresi: 72 saat
- Uptime: %99.9 