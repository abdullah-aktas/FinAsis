# 🚀 50,000 Eşzamanlı Kullanıcı için Production Deployment Rehberi

Bu rehber, FinAsis uygulamasını 50,000 eşzamanlı kullanıcıyı destekleyecek şekilde production'a almak için gereken tüm adımları içerir.

## 📊 Kapasite Planlaması

### Trafik Tahmini
- **Eşzamanlı Kullanıcı**: 50,000
- **Ortalama Request/User/Dakika**: 2-3
- **Toplam RPS (Requests Per Second)**: ~1,500-2,500
- **Peak RPS**: ~5,000 (trafik patlamalarında)

### Resource Gereksinimleri
- **Cloud Run Instances**: 10-500 (otomatik scaling)
- **Her Instance**: 4 CPU, 4GB RAM
- **Concurrency per Instance**: 100
- **Toplam Kapasite**: 50,000 eşzamanlı request

## 🏗️ Mimari Bileşenler

### 1. Cloud Run (Application Layer)
- **Min Instances**: 10 (cold start önleme)
- **Max Instances**: 500 (peak load için)
- **Memory**: 4GB per instance
- **CPU**: 4 vCPU per instance
- **Concurrency**: 100 requests per instance
- **Timeout**: 300 seconds

### 2. Cloud SQL (PostgreSQL)
- **Instance Type**: db-highmem-16 veya db-standard-32
- **Storage**: 500GB+ SSD
- **Backup**: Otomatik, 7 gün retention
- **High Availability**: Enabled
- **Connection Pooling**: PgBouncer veya Cloud SQL Proxy

### 3. Redis (Cache & Session Store)
- **Instance Type**: Redis 7.x, 4GB+ memory
- **High Availability**: Enabled
- **Persistence**: AOF (Append Only File)
- **Use Cases**: 
  - Session storage
  - Query caching
  - Rate limiting
  - Real-time data

### 4. CDN & Static Files
- **Cloud CDN**: Enabled
- **Static Files**: Cloud Storage + CDN
- **Media Files**: Cloud Storage (regional)

## 📋 Deployment Adımları

### Adım 1: Gerekli Servisleri Etkinleştir

```bash
# Gerekli API'leri etkinleştir
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  compute.googleapis.com \
  storage-component.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com

# Proje ID'yi ayarla
export PROJECT_ID=$(gcloud config get-value project)
export REGION="europe-west1"
```

### Adım 2: Cloud SQL (PostgreSQL) Kurulumu

```bash
# High Availability PostgreSQL instance oluştur
gcloud sql instances create finasis-prod-db \
  --database-version=POSTGRES_15 \
  --tier=db-highmem-16 \
  --region=$REGION \
  --storage-type=SSD \
  --storage-size=500GB \
  --storage-auto-increase \
  --backup-start-time=02:00 \
  --enable-bin-log \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=03 \
  --availability-type=REGIONAL \
  --deletion-protection \
  --project=$PROJECT_ID

# Database oluştur
gcloud sql databases create finasis \
  --instance=finasis-prod-db \
  --project=$PROJECT_ID

# Kullanıcı oluştur
gcloud sql users create finasis-app \
  --instance=finasis-prod-db \
  --password=$(openssl rand -base64 32) \
  --project=$PROJECT_ID

# Connection name'i al
export CLOUD_SQL_CONNECTION=$(gcloud sql instances describe finasis-prod-db \
  --format="value(connectionName)" \
  --project=$PROJECT_ID)

echo "Cloud SQL Connection: $CLOUD_SQL_CONNECTION"
```

### Adım 3: Redis (Memorystore) Kurulumu

```bash
# Redis instance oluştur
gcloud redis instances create finasis-redis \
  --size=4 \
  --region=$REGION \
  --redis-version=redis_7_0 \
  --tier=standard \
  --network=projects/$PROJECT_ID/global/networks/default \
  --connect-mode=PRIVATE_SERVICE_ACCESS \
  --enable-auth \
  --project=$PROJECT_ID

# Redis host ve port bilgilerini al
export REDIS_HOST=$(gcloud redis instances describe finasis-redis \
  --region=$REGION \
  --format="value(host)" \
  --project=$PROJECT_ID)
export REDIS_PORT=$(gcloud redis instances describe finasis-redis \
  --region=$REGION \
  --format="value(port)" \
  --project=$PROJECT_ID)

echo "Redis Host: $REDIS_HOST:$REDIS_PORT"
```

### Adım 4: Secrets Yönetimi

```bash
# Django Secret Key
echo -n "$(openssl rand -base64 64)" | \
  gcloud secrets create DJANGO_SECRET_KEY \
  --data-file=- \
  --replication-policy="automatic" \
  --project=$PROJECT_ID

# Database Password
gcloud sql users describe finasis-app \
  --instance=finasis-prod-db \
  --project=$PROJECT_ID | \
  grep password | \
  awk '{print $2}' | \
  gcloud secrets create DJANGO_DB_PASSWORD \
  --data-file=- \
  --replication-policy="automatic" \
  --project=$PROJECT_ID

# Redis Password (eğer auth enabled ise)
echo -n "$(openssl rand -base64 32)" | \
  gcloud secrets create REDIS_PASSWORD \
  --data-file=- \
  --replication-policy="automatic" \
  --project=$PROJECT_ID
```

### Adım 5: Cloud Storage (Static & Media Files)

```bash
# Static files bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-static

# Media files bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-media

# CORS yapılandırması
cat > cors.json << EOF
[
  {
    "origin": ["https://finasis.com.tr", "https://www.finasis.com.tr"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type", "Access-Control-Allow-Origin"],
    "maxAgeSeconds": 3600
  }
]
EOF

gsutil cors set cors.json gs://$PROJECT_ID-static
gsutil cors set cors.json gs://$PROJECT_ID-media
```

### Adım 6: Production Deployment

```bash
# Cloud Build ile deploy
gcloud builds submit \
  --config=deploy/production_50k_users.yaml \
  --substitutions=_CLOUD_SQL_CONNECTION=$CLOUD_SQL_CONNECTION \
  --project=$PROJECT_ID
```

### Adım 7: Environment Variables Ayarlama

```bash
# Servis URL'sini al
SERVICE_URL=$(gcloud run services describe finasis-api \
  --region=$REGION \
  --format="value(status.url)" \
  --project=$PROJECT_ID)

CLOUD_RUN_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')

# Environment variables'ı güncelle
gcloud run services update finasis-api \
  --region=$REGION \
  --update-env-vars="
    DJANGO_ALLOWED_HOSTS=finasis.com.tr,www.finasis.com.tr,$CLOUD_RUN_HOST,
    CLOUD_RUN_HOST=$CLOUD_RUN_HOST,
    REDIS_HOST=$REDIS_HOST,
    REDIS_PORT=$REDIS_PORT,
    DJANGO_DB_CONN_MAX_AGE=600,
    GUNICORN_WORKERS=4,
    GUNICORN_THREADS=8
  " \
  --project=$PROJECT_ID
```

## 🔧 Django Settings Optimizasyonu

### Database Connection Pooling

`config/settings/base.py` dosyasına ekleyin:

```python
# Database Connection Pooling (50K users için)
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 dakika
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'options': '-c statement_timeout=30000',  # 30 saniye query timeout
}

# Connection pool settings
if ENV('DJANGO_DB_ENGINE', '').endswith('postgresql'):
    DATABASES['default']['OPTIONS'].update({
        'MAX_CONNS': 20,  # Her instance için max connection
    })
```

### Redis Cache Configuration

```python
# Redis Cache (50K users için)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{ENV('REDIS_HOST', 'localhost')}:{ENV('REDIS_PORT', '6379')}/1",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'finasis',
        'TIMEOUT': 300,
    }
}

# Session backend
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### Gunicorn Configuration

`gunicorn_config.py` dosyası oluşturun:

```python
# Gunicorn configuration for 50K users
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('GUNICORN_WORKERS', '4'))
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 1000
threads = int(os.environ.get('GUNICORN_THREADS', '8'))
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '120'))
keepalive = int(os.environ.get('GUNICORN_KEEPALIVE', '5'))

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info')

# Process naming
proc_name = 'finasis-api'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Performance
preload_app = True
max_requests = 1000
max_requests_jitter = 50
```

## 📊 Monitoring & Alerting

### Cloud Monitoring Dashboards

```bash
# Monitoring dashboard oluştur
cat > monitoring_dashboard.json << EOF
{
  "displayName": "FinAsis 50K Users Dashboard",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Request Rate",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=cloud_run_revision",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_RATE"
                  }
                }
              }
            }]
          }
        }
      }
    ]
  }
}
EOF

gcloud monitoring dashboards create --config-from-file=monitoring_dashboard.json
```

### Alert Policies

```bash
# High error rate alert
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s \
  --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count"'
```

## 💰 Maliyet Tahmini

### Aylık Tahmini Maliyet (50K Users)

- **Cloud Run**: ~$2,000-3,000/ay
  - 10-500 instances, 4GB RAM, 4 CPU
  - Ortalama 50-100 instance çalışır
  
- **Cloud SQL**: ~$1,500-2,000/ay
  - db-highmem-16, 500GB storage
  
- **Redis**: ~$300-500/ay
  - 4GB standard tier
  
- **Cloud Storage**: ~$50-100/ay
  - Static + media files
  
- **Network Egress**: ~$200-500/ay
  - CDN + data transfer
  
- **Monitoring & Logging**: ~$100-200/ay

**Toplam**: ~$4,150-6,300/ay

## 🧪 Load Testing

### K6 Load Test Script

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '5m', target: 1000 },   // Ramp up to 1000 users
    { duration: '10m', target: 5000 },   // Ramp up to 5000 users
    { duration: '10m', target: 10000 },  // Ramp up to 10000 users
    { duration: '10m', target: 25000 },  // Ramp up to 25000 users
    { duration: '10m', target: 50000 },  // Peak: 50000 users
    { duration: '10m', target: 50000 },  // Sustain peak
    { duration: '10m', target: 0 },      // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],    // 95% of requests < 500ms
    http_req_failed: ['rate<0.01'],      // Error rate < 1%
  },
};

export default function () {
  const BASE_URL = 'https://finasis.com.tr';
  
  // Homepage
  let res = http.get(BASE_URL);
  check(res, { 'status was 200': (r) => r.status == 200 });
  sleep(1);
  
  // API endpoint
  res = http.get(`${BASE_URL}/api/dashboard/`);
  check(res, { 'status was 200': (r) => r.status == 200 });
  sleep(2);
}
```

## ✅ Deployment Checklist

- [ ] Cloud SQL instance oluşturuldu ve yapılandırıldı
- [ ] Redis instance oluşturuldu ve yapılandırıldı
- [ ] Secrets oluşturuldu ve yapılandırıldı
- [ ] Cloud Storage buckets oluşturuldu
- [ ] Cloud Run servisi deploy edildi
- [ ] Environment variables ayarlandı
- [ ] Database migrations çalıştırıldı
- [ ] Static files collect edildi
- [ ] CDN yapılandırıldı
- [ ] Monitoring dashboards oluşturuldu
- [ ] Alert policies ayarlandı
- [ ] Load testing yapıldı
- [ ] DNS yapılandırması tamamlandı
- [ ] SSL sertifikaları yapılandırıldı
- [ ] Backup stratejisi ayarlandı
- [ ] Disaster recovery planı hazırlandı

## 🚨 Troubleshooting

### Yüksek Latency
- Database connection pool'u kontrol et
- Redis cache hit rate'ini kontrol et
- CDN cache hit rate'ini kontrol et
- Database query'leri optimize et

### Yüksek Error Rate
- Logları kontrol et
- Database connection limit'ini kontrol et
- Memory kullanımını kontrol et
- Instance sayısını artır

### Scaling Issues
- Min instances'i artır
- Concurrency değerini ayarla
- CPU ve memory limit'lerini kontrol et

## 📚 İlgili Dokümantasyon

- [Cloud Run Scaling](https://cloud.google.com/run/docs/configuring/scaling)
- [Cloud SQL Best Practices](https://cloud.google.com/sql/docs/postgres/best-practices)
- [Redis Memorystore](https://cloud.google.com/memorystore/docs/redis)
- [Django Production Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

