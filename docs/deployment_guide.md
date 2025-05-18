# FinAsis Deployment Rehberi

## 📋 İçindekiler
1. [Genel Bakış](#genel-bakış)
2. [Sistem Gereksinimleri](#sistem-gereksinimleri)
3. [MVT Yapısı](#mvt-yapısı)
4. [Kurulum](#kurulum)
5. [Veritabanı Ayarları](#veritabanı-ayarları)
6. [Environment Değişkenleri](#environment-değişkenleri)
7. [Statik Dosyalar ve Media](#statik-dosyalar-ve-media)
8. [Dil ve Yerelleştirme](#dil-ve-yerelleştirme)
9. [Güvenlik Ayarları](#güvenlik-ayarları)
10. [CI/CD Pipeline](#cicd-pipeline)
11. [Sunucu Sağlığı İzleme](#sunucu-sağlığı-izleme)
12. [Bakım Modu](#bakım-modu)
13. [Ölçeklendirme](#ölçeklendirme)
14. [Disaster Recovery](#disaster-recovery)
15. [SSL Sertifikaları](#ssl-sertifikaları)

## 📌 Genel Bakış

FinAsis, finansal asistan ve öğretici uygulama olarak geliştirilmiş çok yönlü bir web uygulamasıdır. Bu rehber, FinAsis'in canlı ortama (production environment) nasıl dağıtılacağını detaylı olarak açıklar.

### Desteklediğimiz Ortamlar
- Docker tabanlı deployment
- Kubernetes cluster
- Bare metal server
- VPS (Virtual Private Server)
- Cloud providers (AWS, Azure, GCP)

## 💻 Sistem Gereksinimleri

### Minimum Donanım Gereksinimleri
- CPU: 2 çekirdek
- RAM: 4GB
- Disk: 20GB SSD

### Önerilen Donanım Gereksinimleri
- CPU: 4+ çekirdek
- RAM: 8GB+
- Disk: 50GB+ SSD

### Yazılım Gereksinimleri
- Docker ve Docker Compose
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Nginx 1.23+
- Node.js 16+ (frontend derleme için)

## 🏗️ MVT Yapısı

FinAsis, Django framework'ü temel alır ve MVT (Model-View-Template) mimari desenini kullanır. Bu mimari, kodun düzenlenmesi ve bakımı için belirli bir yapı sağlar:

### 1. Model Katmanı (Veri Yapısı)
**Dizin**: `/apps/*/models.py`

Model katmanı, uygulamanın veri yapısını temsil eden sınıfları içerir. Veri tabanı tablolarını ve aralarındaki ilişkileri tanımlar.

Örnek:
```python
# apps/finance/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class Invoice(models.Model):
    invoice_number = models.CharField(_("Fatura No"), max_length=100)
    amount = models.DecimalField(_("Tutar"), max_digits=15, decimal_places=2)
    issue_date = models.DateField(_("Düzenleme Tarihi"))
    
    class Meta:
        verbose_name = _("Fatura")
        verbose_name_plural = _("Faturalar")
        ordering = ["-issue_date"]
    
    def __str__(self):
        return self.invoice_number
```

### 2. View Katmanı (İş Mantığı)
**Dizin**: `/apps/*/views.py`

View katmanı, HTTP isteklerini alan, işleyen ve yanıt veren fonksiyonlar veya sınıflar içerir. İş mantığını ve veri akışını yönetir.

Örnek:
```python
# apps/finance/views.py
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Invoice

class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "finance/invoice_list.html"
    context_object_name = "invoices"
    paginate_by = 20
    
    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user)
```

### 3. Template Katmanı (Sunum)
**Dizin**: `/templates/*`

Template katmanı, HTML şablonlarını içerir. View tarafından sağlanan verileri görsel olarak sunar.

Örnek:
```html
<!-- templates/finance/invoice_list.html -->
{% extends "base.html" %}
{% load i18n %}

{% block content %}
  <h1>{% trans "Faturalarım" %}</h1>
  <div class="invoice-list">
    {% for invoice in invoices %}
      <div class="card">
        <div class="card-header">{{ invoice.invoice_number }}</div>
        <div class="card-body">
          <p>{% trans "Tutar" %}: {{ invoice.amount }}</p>
          <p>{% trans "Tarih" %}: {{ invoice.issue_date }}</p>
        </div>
      </div>
    {% empty %}
      <div class="alert alert-info">{% trans "Henüz fatura bulunmuyor." %}</div>
    {% endfor %}
  </div>
{% endblock %}
```

### 4. URL Yönlendirme
**Dizin**: `/apps/*/urls.py` ve `/config/urls.py`

URL yönlendirme, HTTP isteklerini ilgili view'lara yönlendirir.

Örnek:
```python
# apps/finance/urls.py
from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("invoices/", views.InvoiceListView.as_view(), name="invoice_list"),
    path("invoices/<int:pk>/", views.InvoiceDetailView.as_view(), name="invoice_detail"),
]
```

### 5. MVT Veri Akışı
1. Kullanıcı bir URL'ye istek gönderir
2. URL yönlendirici isteği ilgili view'e yönlendirir
3. View, model ile etkileşime geçer (veri alışverişi)
4. View, modelden aldığı verileri işler
5. View, işlenmiş verileri template'e gönderir
6. Template, verileri HTML olarak sunar
7. Kullanıcıya yanıt döner

### 6. Proje Organizasyonu
FinAsis projesi, MVT yapısını aşağıdaki organizasyonel yapıyla genişletir:

```
finasis/
├── apps/                 # Modüler uygulamalar
│   ├── core/             # Çekirdek fonksiyonlar
│   ├── users/            # Kullanıcı yönetimi
│   ├── finance/          # Finans modülü
│   ├── accounting/       # Muhasebe modülü
│   └── ...
├── config/               # Proje konfigürasyonu
│   ├── settings/         # Farklı ortamlar için ayarlar
│   ├── urls.py           # Ana URL yapılandırması
│   └── ...
├── templates/            # HTML şablonları
│   ├── base.html         # Ana şablon
│   ├── components/       # Yeniden kullanılabilir bileşenler
│   └── ...
├── static/               # Statik dosyalar (JS, CSS, resimler)
├── media/                # Kullanıcı tarafından yüklenen dosyalar
└── locale/               # Dil çevirileri
```

## 🚀 Kurulum

### 1. Kaynak Kodu Edinme
```bash
git clone https://github.com/finansal-teknolojiler/finasis.git
cd finasis
```

### 2. Docker ile Kurulum (Önerilen)
```bash
# Environment dosyasını oluştur
cp .env.example .env.prod
# Dosyayı düzenle
nano .env.prod

# Production modunda Docker Compose çalıştır
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Migrasyonları Çalıştırma
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### 4. Statik Dosyaları Toplama
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 5. İlk Süper Kullanıcı Oluşturma
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 6. Dil Dosyalarını Derleme
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py compilemessages --locale=tr --locale=en --locale=de --locale=fr --locale=ar --locale=ku
```

## 💾 Veritabanı Ayarları

FinAsis, PostgreSQL veritabanını kullanır. Veritabanı bağlantı ayarları `.env.prod` dosyasında yapılandırılır:

```
DB_NAME=finasis_db
DB_USER=finasis_user
DB_PASSWORD=secure_password_here
DB_HOST=db
DB_PORT=5432
```

### Yedekleme ve Geri Yükleme
```bash
# Veritabanı yedeğini alma
docker-compose -f docker-compose.prod.yml exec db pg_dump -U finasis_user finasis_db > backup_$(date +%Y%m%d).sql

# Veritabanı yedeğini geri yükleme
cat backup_20230101.sql | docker-compose -f docker-compose.prod.yml exec -T db psql -U finasis_user finasis_db
```

## 🔐 Environment Değişkenleri

FinAsis, `.env.prod` dosyasında tanımlanan çeşitli ortam değişkenlerini kullanır:

```
# Django Ayarları
DEBUG=0
SECRET_KEY=your_secure_secret_key_here
DJANGO_SETTINGS_MODULE=config.settings.prod
ALLOWED_HOSTS=finasis.com.tr,www.finasis.com.tr

# Veritabanı
DB_NAME=finasis_db
DB_USER=finasis_user
DB_PASSWORD=secure_password_here
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=1

# AWS S3 (Medya depolama için)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=eu-central-1

# Güvenlik
CSRF_TRUSTED_ORIGINS=https://finasis.com.tr
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
```

## 📂 Statik Dosyalar ve Media

### Statik Dosyaların Yapılandırılması
FinAsis'in statik dosyaları, Docker Compose yapılandırmasında tanımlanan hacimler aracılığıyla Nginx tarafından sunulur:

```yaml
# docker-compose.prod.yml
services:
  web:
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
  
  nginx:
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
```

### Nginx Yapılandırması
```nginx
# nginx/default.conf
server {
    listen 80;
    server_name finasis.com.tr www.finasis.com.tr;
    
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /app/static/;
        expires 30d;
    }
    
    location /media/ {
        alias /app/media/;
        expires 30d;
    }
}
```

## 🌐 Dil ve Yerelleştirme

FinAsis çoklu dil desteği sunar ve aşağıdaki diller için yerelleştirilmiştir:

- Türkçe (tr)
- İngilizce (en)
- Almanca (de)
- Arapça (ar)
- Kürtçe (ku)
- Fransızca (fr)

Dil dosyalarını derlemek için:

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py compilemessages --locale=tr --locale=en --locale=de --locale=fr --locale=ar --locale=ku
```

## 🔒 Güvenlik Ayarları

### SSL Sertifikaları
FinAsis, Let's Encrypt ile otomatik olarak yenilenen SSL sertifikaları kullanır. Traefik reverse proxy, sertifika edinme ve yenileme işlemlerini otomatik olarak yönetir.

### Web Güvenliği Önlemleri
```python
# settings/prod.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 yıl
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### Güvenlik Duvarı ve Ağ Ayarları
```bash
# Güvenlik duvarı kuralları
ufw allow ssh
ufw allow 80
ufw allow 443
ufw enable

# Fail2ban kurulumu
apt-get install fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

## 🔄 CI/CD Pipeline

FinAsis, GitHub Actions kullanarak sürekli entegrasyon ve dağıtım (CI/CD) pipeline'ını otomatize eder.

```yaml
# .github/workflows/django-deploy.yml
name: FinAsis CI/CD

on:
  push:
    branches: [ main, master ]

jobs:
  test:
    # Test adımları...
  
  build-and-push:
    # Docker imajını oluşturma ve push etme adımları...
  
  deploy:
    # Sunucuya dağıtım adımları...
```

### Manuel Deployment
Acil durumlar için manuel dağıtım prosedürü:

```bash
# Sunucuya bağlan
ssh user@your-server

# Proje dizinine git
cd /var/www/finasis

# En son değişiklikleri al
git pull origin master

# Docker imajlarını yeniden oluştur ve başlat
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Migrasyonları çalıştır
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Statik dosyaları topla
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Dil dosyalarını derle
docker-compose -f docker-compose.prod.yml exec web python manage.py compilemessages
```

## 📊 Sunucu Sağlığı İzleme

FinAsis, Prometheus ve Grafana kullanarak sistem sağlığını izler.

### Prometheus ve Grafana
```yaml
# docker-compose.prod.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus_data:/prometheus
  
  grafana:
    image: grafana/grafana
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
```

### Health Check Endpoint
```python
# apps/core/views.py
from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
import redis

def health_check(request):
    status = 200
    data = {
        "database": True,
        "redis": True,
        "celery": True,
    }
    
    # Veritabanı kontrolü
    try:
        connections['default'].cursor()
    except OperationalError:
        data["database"] = False
        status = 500
    
    # Redis kontrolü
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
    except redis.ConnectionError:
        data["redis"] = False
        status = 500
    
    # Celery kontrolü
    # ...
    
    return JsonResponse(data, status=status)
```

## 🛠️ Bakım Modu

Planlı bakım süreçleri için bakım modu:

```python
# apps/core/middleware.py
class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if settings.MAINTENANCE_MODE and not request.path.startswith('/admin'):
            return render(request, 'maintenance.html', status=503)
        return self.get_response(request)
```

Bakım modunu etkinleştirme:

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py shell -c "from django.conf import settings; from django.core.cache import cache; cache.set('maintenance_mode', True, 3600)"
```

## 📈 Ölçeklendirme

### Yatay Ölçeklendirme (Horizontal Scaling)
Docker Swarm veya Kubernetes ile yatay ölçeklendirme yapılabilir:

```bash
# Docker Swarm ile ölçeklendirme
docker service scale finasis_web=3 finasis_celery=2
```

### Dikey Ölçeklendirme (Vertical Scaling)
Sunucu kaynaklarını artırma:

```bash
# Mevcut sunucu özelliklerini görme
free -m
df -h
nproc

# Sunucu kaynaklarını artırma (bulut sağlayıcınıza göre değişir)
# ...
```

## 🔄 Disaster Recovery

### Otomatik Yedekleme
```bash
# Günlük veritabanı yedekleme
0 2 * * * /var/www/finasis/scripts/backup_db.sh

# Haftalık tam yedekleme
0 3 * * 0 /var/www/finasis/scripts/backup_all.sh
```

### Geri Yükleme
```bash
# Veritabanı geri yükleme
/var/www/finasis/scripts/restore_db.sh backup_20230101.sql

# Tam geri yükleme
/var/www/finasis/scripts/restore_all.sh backup_20230101.tar.gz
```

## 🔐 SSL Sertifikaları

FinAsis, Traefik ve Let's Encrypt kullanarak SSL sertifikalarını otomatik olarak yönetir:

```yaml
# docker-compose.prod.yml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "certificatesresolvers.letsencrypt.acme.email=info@finasis.com.tr"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik_data:/etc/traefik
```

Manuel SSL sertifikası yenileme:

```bash
# Certbot ile manuel yenileme
certbot renew
```

## 💡 Sonuç

Bu deployment rehberi, FinAsis uygulamasının MVT mimarisi çerçevesinde canlı ortama dağıtılması için gerekli tüm adımları kapsar. Detaylı bilgi veya yardım için sistem yöneticinizle iletişime geçin.

## 🔍 Ek Kaynaklar
- [Django Dokümantasyonu](https://docs.djangoproject.com/)
- [Docker Dokümantasyonu](https://docs.docker.com/)
- [PostgreSQL Dokümantasyonu](https://www.postgresql.org/docs/)
- [Nginx Dokümantasyonu](https://nginx.org/en/docs/)
- [Let's Encrypt Dokümantasyonu](https://letsencrypt.org/docs/) 