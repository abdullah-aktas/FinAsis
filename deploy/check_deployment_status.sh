#!/bin/bash
# Cloud Run deployment durumunu kontrol et

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"

echo "🔍 Cloud Run Deployment Durumu"
echo "=============================="
echo ""

# 1. Cloud Run servis bilgileri
echo "📋 1. Cloud Run Servis Bilgileri"
echo "--------------------------------"
gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" \
  --format="table(
    metadata.name,
    status.url,
    spec.template.spec.containers[0].image,
    status.latestReadyRevisionName,
    status.latestCreatedRevisionName
  )"

echo ""
echo "📋 2. Son Revision'lar"
echo "--------------------------------"
gcloud run revisions list \
  --service="$SERVICE_NAME" \
  --region="$REGION" \
  --limit=5 \
  --format="table(
    metadata.name,
    status.conditions[0].status,
    metadata.creationTimestamp
  )"

echo ""
echo "📋 3. Son Build'ler (Cloud Build)"
echo "--------------------------------"
gcloud builds list \
  --limit=5 \
  --format="table(
    id,
    status,
    createTime,
    source.repoSource.branchName,
    images[0]
  )"

echo ""
echo "📋 4. GitHub Actions Durumu"
echo "--------------------------------"
echo "GitHub Actions workflow'larını kontrol edin:"
echo "https://github.com/abdullah-aktas/FinAsis/actions"
echo ""

# 5. Health check endpoint testi
echo "📋 5. Health Check Endpoint Testi"
echo "--------------------------------"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "https://finasis.com.tr/health/")
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo "✅ Health check endpoint çalışıyor (HTTP $HEALTH_RESPONSE)"
else
    echo "❌ Health check endpoint çalışmıyor (HTTP $HEALTH_RESPONSE)"
    echo "   Endpoint'ler henüz deploy edilmemiş olabilir."
fi

echo ""
echo "=============================="
echo "✅ Kontrol tamamlandı!"

