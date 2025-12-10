# Deployment Guide

Bu dizin Cloud Run deployment için gerekli dosyaları içerir.

## Önemli Dosyalar

- `entrypoint.sh` - Docker container entrypoint script'i (migration'ları çalıştırır, Gunicorn'u başlatır)
- `cloud_run/cloudbuild.yaml` - Cloud Build configuration (opsiyonel, GitHub Actions kullanılıyor)

## GitHub Actions Deployment

Otomatik deployment `.github/workflows/deploy.yml` dosyası ile yapılır:
- Main branch'e push olduğunda otomatik deploy
- Manuel tetikleme: GitHub Actions → Deploy to Cloud Run → Run workflow

## Environment Variables

Cloud Run'da aşağıdaki environment variables set edilir:
- `DJANGO_SECRET_KEY` - Django secret key (GitHub Secrets'den)
- `DJANGO_DB_PASSWORD` - Database password (GitHub Secrets'den)
- `DJANGO_DB_ENGINE=django.db.backends.postgresql`
- `DJANGO_DB_NAME=finasis`
- `DJANGO_DB_USER=finasis-app`
- `DJANGO_DB_HOST=/cloudsql/finasis-478502:europe-west1:finasis-db`
- `CLOUD_SQL_CONNECTION_NAME=finasis-478502:europe-west1:finasis-db`
- `GOOGLE_CLOUD_PROJECT_NUMBER` - Project number (ALLOWED_HOSTS için)
- `CLOUD_RUN_HOST` - Cloud Run service hostname (ALLOWED_HOSTS için)

## Troubleshooting

### Migration Hataları
- Migration'lar `entrypoint.sh` içinde otomatik çalıştırılır
- Başarısız olursa container başlamaz (set -euo pipefail)
- Loglar Cloud Run console'da görülebilir

### DisallowedHost Hataları
- `ALLOWED_HOSTS` otomatik olarak Cloud Run hostname'lerini içerir
- `GOOGLE_CLOUD_PROJECT_NUMBER` ve `CLOUD_RUN_HOST` environment variables'ı kontrol edin

### Database Connection
- Cloud SQL Proxy otomatik olarak `/cloudsql/` socket üzerinden bağlanır
- `CLOUD_SQL_CONNECTION_NAME` environment variable'ı kontrol edin
