#!/bin/bash
# Migration Kontrol ve Düzeltme Scripti
# Cloud Shell'de çalıştırın

set -euo pipefail

PROJECT_ID="finasis-478502"
SERVICE_NAME="finasis-prod"
REGION="europe-west1"

echo "=========================================="
echo "🔄 Migration Kontrol ve Düzeltme"
echo "=========================================="
echo ""

# 1. Logları kontrol et (alternatif yöntem)
echo "📋 Son Loglar (Migration ile ilgili):"
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
  --limit=50 \
  --project=$PROJECT_ID \
  --format="value(textPayload,jsonPayload.message)" 2>/dev/null | \
  grep -iE "(migration|migrate|billing_module|completed|applying)" | \
  head -20 || echo "   (Migration log bulunamadı)"
echo ""

# 2. Yeni deployment tetikle (migration'lar otomatik çalışacak)
echo "🚀 Yeni Deployment Tetikleniyor..."
echo "   (Migration'lar entrypoint.sh'de otomatik çalışacak)"
echo ""

# GitHub Actions'tan deployment tetiklemek için
echo "💡 GitHub Actions'tan deployment tetiklemek için:"
echo "   1. GitHub repo'ya gidin: https://github.com/abdullah-aktas/FinAsis"
echo "   2. Actions sekmesine gidin"
echo "   3. 'Deploy to Cloud Run' workflow'unu manuel çalıştırın"
echo ""
echo "   VEYA"
echo ""
echo "   Manuel olarak yeni bir commit yapın:"
echo "   git commit --allow-empty -m 'Trigger deployment for migrations'"
echo "   git push origin main"
echo ""

# 3. Mevcut revision'ı kontrol et
echo "📋 Mevcut Revision:"
LATEST_REVISION=$(gcloud run revisions list \
    --service=$SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --limit=1 \
    --format="value(name)" 2>/dev/null || echo "")

if [ -n "$LATEST_REVISION" ]; then
    echo "   ✅ $LATEST_REVISION"
    
    # Revision'ın durumunu kontrol et
    REVISION_READY=$(gcloud run revisions describe $LATEST_REVISION \
        --region=$REGION \
        --project=$PROJECT_ID \
        --format="value(status.conditions[0].status)" 2>/dev/null || echo "")
    echo "   📊 Durum: $REVISION_READY"
else
    echo "   ❌ Revision bulunamadı"
fi
echo ""

# 4. Environment variable kontrolü
echo "🔧 RUN_DB_MIGRATIONS Environment Variable:"
ENV_VARS=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="json" 2>/dev/null | jq -r '.spec.template.spec.containers[0].env[]? | select(.name == "RUN_DB_MIGRATIONS") | .value' || echo "")

if [ -z "$ENV_VARS" ] || [ "$ENV_VARS" = "true" ]; then
    echo "   ✅ RUN_DB_MIGRATIONS=true (default) - Migration'lar çalışacak"
else
    echo "   ⚠️  RUN_DB_MIGRATIONS=$ENV_VARS"
fi
echo ""

# 5. Öneriler
echo "=========================================="
echo "💡 Öneriler:"
echo "=========================================="
echo ""
echo "1. Yeni bir deployment tetikleyin (GitHub Actions)"
echo "2. Deployment sonrası logları kontrol edin:"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=100 --project=$PROJECT_ID --format=\"value(textPayload)\" | grep -iE \"(migration|billing_module)\""
echo ""
echo "3. Ana sayfayı test edin:"
echo "   curl -s https://finasis-prod-s3kju7bqua-ew.a.run.app/ | grep -iE \"(500|error|billing_module)\" || echo \"✅ Ana sayfa çalışıyor!\""
echo ""

