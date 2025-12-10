#!/bin/bash
# Son logları al - gcloud crash sorununu çözer
# Cloud Shell'de çalıştırın: bash deploy/get_recent_logs.sh

PROJECT_ID="finasis-478502"
SERVICE_NAME="finasis-prod"
REGION="europe-west1"

echo "📋 Son loglar (JSON formatından parse ediliyor):"
echo "================================================"
echo ""

# JSON formatında al ve parse et
gcloud run services logs read $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --limit=100 \
  --format=json 2>/dev/null | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
for entry in data[:50]:
    payload = entry.get('textPayload', '') or entry.get('jsonPayload', {}).get('message', '')
    severity = entry.get('severity', 'DEFAULT')
    timestamp = entry.get('timestamp', '')
    if any(keyword in payload for keyword in ['SIGTERM', 'ERROR', 'Exception', 'Traceback', 'Starting Gunicorn', 'FinAsis API server', 'SECRET_KEY', 'PORT is set', 'Container called exit', 'Worker', 'Shutting down']):
        print(f\"{timestamp} [{severity}] {payload[:200]}\")
" 2>/dev/null || \
  echo "⚠️  JSON parse edilemedi, alternatif yöntem deneniyor..."

echo ""
echo "================================================"
echo "💡 Tüm logları görmek için Cloud Console'u kullanın:"
echo "   https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/logs?project=$PROJECT_ID"

