#!/bin/bash
# Database Migration Çalıştırma Scripti
# Cloud Shell'de çalıştırın veya Cloud Run container'ında

set -euo pipefail

PROJECT_ID="finasis-478502"
SERVICE_NAME="finasis-prod"
REGION="europe-west1"

echo "=========================================="
echo "🔄 Database Migration Çalıştırma"
echo "=========================================="
echo ""

# Cloud Run container'ında migration çalıştır
echo "🔧 Cloud Run container'ında migration çalıştırılıyor..."
echo ""

# Cloud Run'da migration çalıştırmak için exec kullan
gcloud run jobs create migration-job \
  --image=europe-west1-docker.pkg.dev/$PROJECT_ID/finasis-app/finasis-api:latest \
  --region=$REGION \
  --service-account=github-actions-deploy@$PROJECT_ID.iam.gserviceaccount.com \
  --add-cloudsql-instances=$PROJECT_ID:$REGION:finasis-db \
  --set-env-vars="DJANGO_DB_ENGINE=django.db.backends.postgresql,DJANGO_DB_NAME=finasis,DJANGO_DB_USER=finasis-app,DJANGO_DB_HOST=/cloudsql/$PROJECT_ID:$REGION:finasis-db,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:finasis-db,DJANGO_DEBUG=0,DJANGO_SECRET_KEY=9%d)c&i%r%mc_0p+myppa16@^e3p6sxig5)#&#rar9vy9jhd-3,DJANGO_DB_PASSWORD=FinAsis.4747" \
  --command="python" \
  --args="manage.py,migrate,--noinput" \
  --project=$PROJECT_ID 2>/dev/null || {
    echo "⚠️  Job zaten mevcut, güncelleniyor..."
    gcloud run jobs update migration-job \
      --image=europe-west1-docker.pkg.dev/$PROJECT_ID/finasis-app/finasis-api:latest \
      --region=$REGION \
      --project=$PROJECT_ID
}

echo ""
echo "🚀 Migration job çalıştırılıyor..."
gcloud run jobs execute migration-job \
  --region=$REGION \
  --project=$PROJECT_ID \
  --wait

echo ""
echo "✅ Migration tamamlandı!"
echo ""

