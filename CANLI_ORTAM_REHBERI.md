# FinAsis Canlı Ortam Kurulum Rehberi

Bu rehber, FinAsis uygulamasının canlı ortamda (production) kurulumu ve çalıştırılması için gerekli adımları içermektedir.

## 1. Sistem Gereksinimleri

- **İşletim Sistemi**: Ubuntu 20.04 LTS veya daha yeni (önerilen)
- **CPU**: En az 4 çekirdek
- **RAM**: En az 8GB (önerilen 16GB+)
- **Disk**: En az 100GB SSD
- **Ağ**: Sabit IP adresi ve domain adı

## 2. Ön Gereksinimler

Aşağıdaki yazılımların sunucunuzda kurulu olması gerekmektedir:

- Docker ve Docker Compose
- Git
- Nginx (Docker dışında, ana host üzerinde)
- Certbot (SSL sertifikaları için)

## 3. Kurulum Adımları

### 3.1 Depoyu Klonlama

```bash
git clone https://github.com/your-username/finasis.git
cd finasis
```

### 3.2 Ortam Değişkenlerini Ayarlama

`.env.example` dosyasını `.env` olarak kopyalayın ve değerleri kendi ortamınıza göre düzenleyin:

```bash
cp .env.example .env
nano .env
```

Aşağıdaki değerleri kendi ortamınıza göre ayarlayın:
- DJANGO_SECRET_KEY
- DJANGO_ALLOWED_HOSTS
- Veritabanı bilgileri
- Email ayarları
- AWS S3 bilgileri (kullanılacaksa)
- OpenAI API Key
- Şirket bilgileri

### 3.3 Docker ile Çalıştırma

Üretim ortamı için docker-compose.prod.yml dosyasını kullanın:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 3.4 Veritabanı Migrasyonlarını Uygulama

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### 3.5 Statik Dosyaları Toplama

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
```

### 3.6 Süper Kullanıcı Oluşturma

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 3.7 Çevirileri Derleme

Django çeviri dosyalarını hazırlamak ve derlemek için scripts/manage_translations.py betiğini kullanabilirsiniz:

```bash
# Çeviri dosyalarını ilk kez hazırlamak için
docker-compose -f docker-compose.prod.yml exec web python scripts/manage_translations.py init

# Mevcut çeviri dosyalarını derlemek için
docker-compose -f docker-compose.prod.yml exec web python scripts/manage_translations.py compile

# Çeviri dosyalarının durumunu görmek için
docker-compose -f docker-compose.prod.yml exec web python scripts/manage_translations.py status
```

### 3.8 Nginx Konfigürasyonu

`/etc/nginx/sites-available/finasis.conf` dosyasını oluşturun:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # SSL yönlendirme
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name your-domain.com www.your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL parametreleri
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384';
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    
    # HSTS (31536000 saniye = 1 yıl)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Diğer güvenlik başlıkları
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    
    # Statik ve medya dosyaları
    location /static/ {
        alias /path/to/finasis/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
    
    location /media/ {
        alias /path/to/finasis/media/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
    
    # API istekleri proxy
    location / {
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
    }
    
    # Sağlık kontrolü endpoint
    location /health/ {
        proxy_pass http://localhost:8000/health/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        access_log off;
        proxy_read_timeout 5s;
        proxy_connect_timeout 5s;
        proxy_send_timeout 5s;
    }
}
```

Nginx konfigürasyonunu etkinleştirin:

```bash
ln -s /etc/nginx/sites-available/finasis.conf /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 3.9 SSL Sertifikası Alınması

Let's Encrypt ile SSL sertifikası oluşturun:

```bash
certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 4. Bakım ve İzleme

### 4.1 Günlük Yedek Alma

Otomatik yedekleme için `backup.sh` betiğini cron ile çalıştırın:

```bash
0 2 * * * /path/to/finasis/backup.sh
```

### 4.2 Log Dosyalarını İzleme

```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### 4.3 Prometheus ve Grafana ile İzleme

Prometheus ve Grafana kurulumları docker-compose.prod.yml içinde tanımlanmıştır. Grafana arayüzüne erişmek için:

```
http://your-domain.com:3000
```

Varsayılan kullanıcı adı ve şifre: admin/admin

### 4.4 Güvenlik Güncellemeleri

Düzenli olarak güvenlik güncellemelerini yapın:

```bash
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
docker-compose -f docker-compose.prod.yml exec web python scripts/manage_translations.py compile
```

## 5. MVT (Model-View-Template) Yapısı Rehberi

Django MVT yapısına göre FinAsis projesi aşağıdaki şekilde düzenlenmiştir:

### 5.1 Models (Modeller)

Her uygulama kendi `models.py` dosyasında veritabanı modellerini tanımlar:

- `apps/accounts/models.py`: Kullanıcı ve hesap modelleri
- `apps/finance/models.py`: Finans ile ilgili modeller
- `apps/accounting/models.py`: Muhasebe ile ilgili modeller

### 5.2 Views (Görünümler)

Görünümler, MVT yapısına uygun olarak her uygulamanın kendi `views` dizini içinde organize edilmiştir:

- `apps/{app_name}/views/__init__.py`: Ana görünüm dosyası, diğer modüllerden görünümleri içe aktarır
- `apps/{app_name}/views/module.py`: Her modül belirli bir işlevselliğe odaklanır

Örneğin, Finance uygulaması için görünümler:
- `apps/finance/views/banking.py`: Banka işlemleri ile ilgili görünümler 
- `apps/finance/views/einvoice.py`: E-fatura işlemleri ile ilgili görünümler

### 5.3 Templates (Şablonlar)

Şablonlar iki düzeyde organize edilmiştir:

1. **Merkezi Şablonlar**: Tüm uygulama genelinde kullanılan şablonlar `templates/` klasöründe toplanmıştır:
   - `templates/base.html`: Ana şablon
   - `templates/includes/`: Yeniden kullanılabilir şablon parçaları

2. **Uygulama Özel Şablonlar**: Her uygulama kendi şablonlarını kendi dizininde tutar:
   - `apps/{app_name}/templates/{app_name}/`: Uygulama özel şablonlar

### 5.4 URLs (URL Yapılandırması)

URL yapısı da benzer şekilde organize edilmiştir:

- `config/urls.py`: Ana URL yapılandırması
- `apps/{app_name}/urls.py`: Her uygulama kendi URL'lerini tanımlar

### 5.5 MVT İş Akışı

Tipik bir MVT iş akışı şu şekildedir:

1. Kullanıcı bir URL'ye istek gönderir.
2. `urls.py` içindeki URL deseni eşleşen bir görünüme yönlendirilir.
3. Görünüm (`views/`) gerekli modelleri (`models.py`) çağırır ve verileri işler.
4. Görünüm, işlenmiş verileri bir şablona (`templates/`) aktarır.
5. Şablon verileri HTML olarak render eder ve kullanıcıya geri döndürür.

## 6. Çoklu Dil Desteği

FinAsis, aşağıdaki dillerde tam destek sunar:

- Türkçe (tr)
- İngilizce (en)
- Arapça (ar)
- Kürtçe (ku)
- Almanca (de)

### 6.1 Dil Dosyaları

Çeviri dosyaları `locale/{lang}/LC_MESSAGES/django.po` konumunda bulunur. Çeviri dosyalarını yönetmek için `scripts/manage_translations.py` betiği kullanılır.

### 6.2 Dil Seçimi

Kullanıcılar arayüzde dil seçimi yapabilirler. Dil tercihi tarayıcı çerezlerinde saklanır ve 
kullanıcı oturumu boyunca korunur.

### 6.3 URL'lerde Dil Öneki

URL'lerde dil öneki (ör. `/tr/finance/`, `/en/finance/`) kullanılmaktadır. Bu, her sayfanın her dilde kendi benzersiz URL'sine sahip olmasını sağlar.

### 6.4 Çeviri İş Akışı

Yeni çeviriler eklemek için iş akışı:

1. Kaynak kodda çevrilebilir metinler `_(...)` veya `gettext_lazy(...)` ile işaretlenir.
2. `python scripts/manage_translations.py make` komutu ile çeviri dosyaları güncellenir.
3. Çevirmenler her dil için `locale/{lang}/LC_MESSAGES/django.po` dosyalarını düzenler.
4. `python scripts/manage_translations.py compile` komutu ile çeviriler derlenir.

## 7. Canlı Ortam En İyi Uygulamaları

### 7.1 Güvenlik En İyi Uygulamaları

- SECRET_KEY'i güvenli ve karmaşık yapın, ortam değişkenlerinde saklayın
- DEBUG modunu canlı ortamda kapatın
- ALLOWED_HOSTS'u sınırlandırın
- Tüm güvenlik başlıklarını etkinleştirin
- Güçlü şifre politikaları uygulayın
- Rate limiting kullanın
- Düzenli güvenlik denetimleri yapın

### 7.2 Performans Optimizasyonu

- Redis önbelleğini etkinleştirin
- CDN kullanarak statik dosyaları dağıtın
- PostgreSQL optimizasyonlarını uygulayın
- Veritabanı indekslerini doğru kullanın
- ORM sorgularını optimize edin
- Celery ile arka plan görevlerini yönetin

### 7.3 Ölçeklenebilirlik

- Docker Swarm veya Kubernetes ile yatay ölçeklendirme
- Veritabanı replikasyonu
- Yük dengeleyici kullanın

## 8. Sorun Giderme

### 8.1 Yaygın Hatalar ve Çözümleri

1. **500 Internal Server Error**
   - Django loglarını kontrol edin: `docker-compose logs -f web`
   - DEBUG=True yaparak geliştirme modunda detaylı hata gösterimini etkinleştirin (yalnızca geçici olarak)

2. **Veritabanı Bağlantı Hataları**
   - Veritabanı erişim bilgilerini kontrol edin
   - PostgreSQL servisinin çalıştığından emin olun
   - PostgreSQL loglarını kontrol edin: `docker-compose logs -f db`

3. **Statik Dosya Sorunları**
   - `collectstatic` komutunu çalıştırın
   - Nginx yapılandırmasını kontrol edin
   - Dosya izinlerini kontrol edin

4. **E-Belge Sorunları**
   - API anahtarlarını ve URL'leri kontrol edin
   - SOAP isteklerini doğrulayın
   - Test modunda bir belge gönderin

5. **Sağlık Kontrolü Hataları**
   - `/health/` endpoint'ine giderek detaylı hata raporunu görüntüleyin
   - Redis, PostgreSQL ve diğer servislerin çalıştığından emin olun

## 9. Sağlık Kontrolü ve İzleme

FinAsis, sistem durumunu sürekli izlemek için bir sağlık kontrolü sistemi içerir:

### 9.1 Sağlık Kontrolü Endpoint

`/health/` endpoint'i (verbose=true parametresi ile) şu bileşenlerin durumunu kontrol eder:
- Veritabanı bağlantısı
- Redis bağlantısı
- Önbellek sistemi
- Statik dosyalar
- Media dosyaları
- Sistem kaynakları (CPU, RAM, Disk)

### 9.2 Prometheus Metrikler

`/metrics/` endpoint'i (yetkilendirme gerektirir) Prometheus için metrikler sunar:
- HTTP istek sayısı ve yanıt süreleri
- Veritabanı sorgu sayısı ve süreleri
- Cache hit/miss oranları
- Sistem kaynakları kullanımı

### 9.3 Grafana Gösterge Panelleri

Grafana, Prometheus verilerini görselleştirmek için hazır gösterge panelleri sunar:
- Sistem Genel Bakış
- Uygulama Performansı
- Veritabanı Performansı
- Kullanıcı Etkinliği

## 10. Destek ve İletişim

Herhangi bir sorunla karşılaşırsanız, aşağıdaki kanallardan destek alabilirsiniz:

- **Email**: support@finasis.com.tr
- **Telefon**: +90 212 123 4567
- **Destek Portalı**: https://destek.finasis.com.tr

---

Bu rehber, FinAsis uygulamasının başarılı bir şekilde canlıya alınması için temel bilgileri içermektedir. Daha detaylı bilgi için teknik dokümantasyona bakabilirsiniz: `docs/` klasörü 