#!/bin/bash
# Cloud Build izinlerini düzeltmek için çalıştırılacak script
# Cloud Shell'de veya gcloud CLI'sı yüklü bir makinede çalıştırın

PROJECT_ID="finasis-478502"
SERVICE_ACCOUNT="github-actions-deploy@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🔧 Cloud Build izinlerini düzeltiyorum..."
echo "📋 Proje: ${PROJECT_ID}"
echo "👤 Service Account: ${SERVICE_ACCOUNT}"

# Cloud Build Editor rolü (build submit ve diğer Cloud Build işlemleri için)
echo "✅ Cloud Build Editor rolü ekleniyor..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/cloudbuild.builds.editor" \
  --condition=None

# Log Writer rolü (logları görmek için)
echo "✅ Logs Writer rolü ekleniyor..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/logging.logWriter" \
  --condition=None

echo ""
echo "✅ Tüm izinler başarıyla eklendi!"
echo "📝 Şimdi GitHub Actions workflow'unu tekrar çalıştırabilirsiniz."

