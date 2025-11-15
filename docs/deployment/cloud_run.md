# Google Cloud Run + PostgreSQL Dağıtım Rehberi

Bu rehber FinAsis uygulamasını Google Cloud Run üzerinde çalıştırıp Cloud SQL (PostgreSQL) veritabanına bağlamak için gereken adımları açıklar. Adımların tamamı üretim güvenliği göz önünde bulundurularak hazırlanmıştır.

## 1. Mimari Özet
- **Cloud Run**: Docker imajını barındırır, otomatik ölçeklenir.
- **Cloud SQL for PostgreSQL**: Yönetilen veritabanı (önerilen sürüm 15).
- **Secret Manager**: Hassas ortam değişkenlerini saklar.
- **Artifact Registry**: Docker imajlarının tutulduğu özel kayıt.
- **Cloud Build**: CI/CD ve otomatik dağıtım için isteğe bağlı pipeline.

## 2. Ön Koşullar
1. `gcloud` CLI 470+ ve `beta` bileşenleri.
2. Google Cloud projesi ve faturalandırma aktif.
3. Aşağıdaki API'leri etkinleştirin:
   ```bash
   gcloud services enable run.googleapis.com sqladmin.googleapis.com \
     artifactregistry.googleapis.com secretmanager.googleapis.com
   ```
4. Kullanacağınız hizmet hesabına şu roller verilmeli:
   - `roles/run.admin`
   - `roles/cloudsql.client`
   - `roles/secretmanager.secretAccessor`
   - `roles/artifactregistry.writer`

## 3. Cloud SQL (PostgreSQL) Kurulumu
```bash
gcloud sql instances create finasis-prod-sql \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-7680 \
  --region=europe-west4 \
  --availability-type=regional \
  --storage-type=SSD \
  --storage-size=50 \
  --storage-auto-increase \
  --enable-point-in-time-recovery

gcloud sql databases create finasis \
  --instance=finasis-prod-sql

gcloud sql users create finasis-app \
  --instance=finasis-prod-sql \
  --password "$(openssl rand -base64 24)"
```

> Not: Parolayı Secret Manager'da saklayın ve Cloud Run'a secret referansı olarak geçin.

## 4. Ortam Değişkenleri
Cloud Run servisi için kritik değişkenler:

| Değişken | Açıklama |
| --- | --- |
| `DJANGO_SECRET_KEY` | Rastgele üretin, Secret Manager'dan çekin |
| `DJANGO_ALLOWED_HOSTS` | `app.finasis.com.tr` vb. |
| `DJANGO_DB_ENGINE` | `django.db.backends.postgresql` |
| `DJANGO_DB_NAME` | `finasis` |
| `DJANGO_DB_USER` | `finasis-app` |
| `DJANGO_DB_PASSWORD` | Secret Manager referansı |
| `CLOUD_SQL_CONNECTION_NAME` | `proje:region:finasis-prod-sql` |
| `DJANGO_DB_SSL_REQUIRED` | `True` (Cloud SQL proxy SSL sağlar) |
| `DJANGO_DB_CONN_MAX_AGE` | `300` (5 dk havuz) |
| `DJANGO_SECURE_SSL_REDIRECT` | `True` |
| `FINASIS_MEETING_BASE_URL` | Dış URL |
| `RUN_DB_MIGRATIONS` | `true` (varsayılan) |

Secret Manager'da oluşturma:
```bash
printf "prod-secret-key" | gcloud secrets create finasis-django-secret \
  --data-file=-
```

Cloud Run'da kullanma:
```bash
gcloud beta run services update finasis-api \
  --set-secrets=DJANGO_SECRET_KEY=finasis-django-secret:latest
```

## 5. Docker İmajı Oluşturma
Projede bulunan `Dockerfile` çok-aşamalı build kullanır. Lokal test:
```bash
docker build -t finasis-api:dev .
docker run --rm -p 8080:8080 \
  --env-file=.env.cloudrun \
  finasis-api:dev
```

Artifact Registry'e push:
```bash
gcloud artifacts repositories create finasis-app \
  --repository-format=docker \
  --location=europe-west4

export REGION=europe-west4
export AR_HOST=${REGION}-docker.pkg.dev
export PROJECT_ID=$(gcloud config get-value project)
export IMAGE=${AR_HOST}/${PROJECT_ID}/finasis-app/api

gcloud builds submit --tag ${IMAGE}:$(git rev-parse --short HEAD)
```

## 6. Cloud Run Dağıtımı
```bash
gcloud run deploy finasis-api \
  --image=${IMAGE}:$(git rev-parse --short HEAD) \
  --region=${REGION} \
  --platform=managed \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --execution-environment=gen2 \
  --max-instances=4 \
  --concurrency=40 \
  --timeout=120 \
  --set-env-vars=DJANGO_DB_ENGINE=django.db.backends.postgresql,DJANGO_DB_NAME=finasis,DJANGO_DB_USER=finasis-app,DJANGO_DB_CONN_MAX_AGE=300,FINASIS_MEETING_BASE_URL=https://app.finasis.com.tr \
  --set-secrets=DJANGO_SECRET_KEY=finasis-django-secret:latest,DJANGO_DB_PASSWORD=finasis-db-pass:latest \
  --add-cloudsql-instances=${PROJECT_ID}:${REGION}:finasis-prod-sql
```

## 7. Migrasyon ve Statik Dosyalar
- Container başlangıcında `deploy/entrypoint.sh` otomatik olarak `python manage.py migrate --noinput` çalıştırır. Gerekirse `RUN_DB_MIGRATIONS=false` ile devre dışı bırakabilirsiniz.
- `collectstatic` build aşamasında çalışır; Cloud Run container'ı statik dosyaları Whitenoise ile sunar. CDN isteyen ortamlar için Cloud Storage + CDN senaryosu ayrıca uygulanabilir.

## 8. Sağlık Kontrolleri & İzleme
- Cloud Run Service Settings → Health checks: `GET /metrics/health/` (varsa) veya `/` kullanın.
- `django-prometheus` metrikleri `/_metrics` üzerinden alınabilir; özel yetki katmanı eklemeyi unutmayın.
- Cloud Logging ve Error Reporting otomatik olarak logları toplayacaktır.

## 9. CI/CD (Opsiyonel)
`deploy/cloud_run/cloudbuild.yaml` dosyasını Cloud Build trigger'ına bağlayarak her `main` commit'inde otomatik imaj oluşturup Cloud Run'a deploy edebilirsiniz.

---
Bu adımlar tamamlandığında FinAsis uygulaması ölçeklenebilir, güvenli ve PostgreSQL destekli şekilde Cloud Run üzerinde üretime hazır olur.

