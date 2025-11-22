#!/bin/bash
# =============================================================================
# Quota Uyumlu 50K Users Deployment - Cloud Shell Versiyonu
# Mevcut quota limitleri ile optimize edilmiş deployment
# =============================================================================

SERVICE_NAME="${SERVICE_NAME:-finasis-prod}"
REGION="${REGION:-europe-west1}"
PROJECT_ID=$(gcloud config get-value project)

echo "🚀 Quota Uyumlu Deployment (50K Users için optimize)"
echo "Proje: $PROJECT_ID"
echo "Servis: $SERVICE_NAME"
echo ""

echo "📊 Mevcut Quota Limitleri:"
echo "  • Max Instances: 50"
echo "  • Max CPU: 200 vCPU"
echo "  • Max Memory: 400GB"
echo ""

echo "🎯 Optimize Edilmiş Yapılandırma:"
echo "  • Instances: 10-50"
echo "  • Memory: 3GB per instance"
echo "  • CPU: 4 per instance"
echo "  • Concurrency: 200 per instance"
echo "  • Toplam Kapasite: 10,000 eşzamanlı request"
echo ""

read -p "Devam etmek istiyor musunuz? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "İptal edildi"
    exit 0
fi

# Servisi güncelle
echo "🚀 Servis güncelleniyor..."
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --memory=3Gi \
    --cpu=4 \
    --timeout=300 \
    --concurrency=200 \
    --min-instances=10 \
    --max-instances=50 \
    --cpu-boost \
    --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Servis başarıyla güncellendi!"
    echo ""
    echo "📊 Güncellenmiş Bilgiler:"
    gcloud run services describe "$SERVICE_NAME" \
        --region="$REGION" \
        --format="table(
            metadata.name,
            status.url,
            spec.template.spec.containers[0].resources.limits.memory,
            spec.template.spec.containers[0].resources.limits.cpu,
            spec.template.spec.containerConcurrency
        )" \
        --project="$PROJECT_ID"
    
    echo ""
    echo "⚠️  Not: 50K eşzamanlı kullanıcı için quota artırımı gerekli"
    echo "📈 Quota artırımı için: deploy/QUOTA_INCREASE_GUIDE.md dosyasına bakın"
else
    echo ""
    echo "❌ Deployment başarısız oldu"
    echo "📈 Quota artırımı gerekebilir: deploy/QUOTA_INCREASE_GUIDE.md"
    exit 1
fi

