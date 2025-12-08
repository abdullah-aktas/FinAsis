#!/bin/bash
# Cloud Run deployment durumunu kontrol et

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"

echo "🔍 Cloud Run Servis Durumu"
echo "=========================="
echo ""

# Servis bilgilerini al
gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="yaml(status,spec.template.spec.containers[0].image,status.latestReadyRevisionName,status.url)"

echo ""
echo "📊 Son revision'ları listele:"
gcloud run revisions list \
  --service=$SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --limit=5 \
  --format="table(metadata.name,status.conditions[0].status,metadata.creationTimestamp)"

echo ""
echo "🌐 Servis URL:"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(status.url)")

echo "   $SERVICE_URL"

echo ""
echo "✅ Deployment kontrolü tamamlandı!"

