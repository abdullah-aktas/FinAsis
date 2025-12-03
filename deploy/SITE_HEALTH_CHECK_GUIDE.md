# finasis.com.tr Site Health Check Rehberi

Bu rehber, finasis.com.tr sitesinin sağlık durumunu kontrol etmek için oluşturulmuş monitoring sistemini açıklar.

## 🎯 Oluşturulan Yapı

### 1. Health Check Endpoint'leri

Sitede 3 farklı health check endpoint'i mevcut:

#### Basit Health Check
```
GET https://finasis.com.tr/health/
```
- **Amaç**: Hızlı durum kontrolü (Cloud Run health check için)
- **Yanıt**: Database ve cache durumu
- **Kimlik Doğrulama**: Gerektirmez (public)

#### Detaylı Health Check
```
GET https://finasis.com.tr/health/detailed/
```
- **Amaç**: Kapsamlı sistem durumu
- **Yanıt**: Database, cache, aktif kullanıcılar, son hatalar
- **Kimlik Doğrulama**: Gerektirmez (public)

#### Site Status
```
GET https://finasis.com.tr/health/status/
```
- **Amaç**: Modül durumları ve genel site durumu
- **Yanıt**: Tüm modüllerin durumu
- **Kimlik Doğrulama**: Gerektirmez (public)

## 🚀 Kullanım

### Cloud Shell'de Kontrol

```bash
cd ~/FinAsis
git pull origin main

# Tek seferlik kontrol
chmod +x deploy/check_site_health.sh
./deploy/check_site_health.sh
```

### Sürekli Monitoring

```bash
# Her 60 saniyede bir kontrol et (sınırsız)
chmod +x deploy/monitor_site.sh
./deploy/monitor_site.sh

# Her 30 saniyede bir, 10 kez kontrol et
CHECK_INTERVAL=30 MAX_CHECKS=10 ./deploy/monitor_site.sh
```

### Lokal Ortamda Kontrol

```bash
# PowerShell'de
cd D:\FinAsis
bash deploy/check_site_health.sh

# Veya direkt curl ile
curl https://finasis.com.tr/health/
curl https://finasis.com.tr/health/detailed/ | python -m json.tool
```

## 📊 Health Check Response Örnekleri

### Basit Health Check Response

```json
{
  "status": "healthy",
  "timestamp": "2025-12-03T07:00:00Z",
  "checks": {
    "database": {
      "status": "ok",
      "response_time_ms": 15
    },
    "cache": {
      "status": "ok"
    }
  },
  "version": "unknown"
}
```

### Detaylı Health Check Response

```json
{
  "status": "healthy",
  "timestamp": "2025-12-03T07:00:00Z",
  "checks": {
    "database": {
      "status": "ok",
      "response_time_ms": 15,
      "version": "PostgreSQL 15.0",
      "active_connections": 5,
      "vendor": "postgresql"
    },
    "cache": {
      "status": "ok",
      "response_time_ms": 2
    },
    "static_files": {
      "status": "ok"
    }
  },
  "system_info": {
    "settings": {
      "debug": false,
      "allowed_hosts": ["finasis.com.tr", "www.finasis.com.tr"],
      "database_engine": "django.db.backends.postgresql"
    },
    "recent_errors_5min": 0,
    "active_sessions": 42,
    "version": "unknown"
  }
}
```

## 🔧 Cloud Run Health Check Yapılandırması

Cloud Run'da health check endpoint'ini kullanmak için:

```bash
gcloud run services update finasis-prod \
  --region=europe-west1 \
  --health-check-path=/health/ \
  --health-check-interval=30 \
  --health-check-timeout=10 \
  --health-check-threshold=3
```

## 📈 Monitoring Araçları ile Entegrasyon

### Uptime Robot

1. Uptime Robot'a giriş yapın
2. "Add New Monitor" seçin
3. Monitor Type: HTTP(s)
4. URL: `https://finasis.com.tr/health/`
5. Interval: 5 dakika
6. Alert Contacts: E-posta ekleyin

### Google Cloud Monitoring

```bash
# Cloud Monitoring'de alert policy oluştur
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="FinAsis Health Check" \
  --condition-display-name="Health Check Failed" \
  --condition-threshold-value=1 \
  --condition-threshold-duration=300s
```

## 🆘 Sorun Giderme

### Health Check Başarısız Olursa

1. **Database Sorunu**:
   ```bash
   # Cloud SQL bağlantısını kontrol et
   gcloud sql instances describe INSTANCE_NAME
   ```

2. **Cache Sorunu**:
   ```bash
   # Redis bağlantısını kontrol et (eğer kullanıyorsanız)
   ```

3. **Logları Kontrol Et**:
   ```bash
   gcloud run services logs read finasis-prod \
     --region=europe-west1 \
     --limit=50
   ```

### Site Yanıt Vermiyorsa

1. Cloud Run servis durumunu kontrol et:
   ```bash
   gcloud run services describe finasis-prod --region=europe-west1
   ```

2. Revision durumunu kontrol et:
   ```bash
   gcloud run revisions list --service=finasis-prod --region=europe-west1
   ```

3. Son deployment'ı kontrol et:
   ```bash
   gcloud run services describe finasis-prod \
     --region=europe-west1 \
     --format="value(status.latestReadyRevisionName)"
   ```

## 📝 Hızlı Referans

```bash
# Tek seferlik kontrol
curl https://finasis.com.tr/health/

# Detaylı kontrol
curl https://finasis.com.tr/health/detailed/ | jq

# Site status
curl https://finasis.com.tr/health/status/ | jq

# Script ile kontrol
./deploy/check_site_health.sh

# Sürekli monitoring
./deploy/monitor_site.sh
```

## 🔐 Güvenlik Notları

- Health check endpoint'leri public erişilebilir (authentication gerektirmez)
- Hassas bilgiler (şifreler, API key'ler) döndürülmez
- Sadece sistem durumu bilgileri paylaşılır
- Production'da DEBUG=False olduğundan emin olun

