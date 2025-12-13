# Cloud Build ile hızlı deployment scripti (PowerShell)
# Cloud Shell'de çalıştırın veya gcloud CLI ile: powershell -ExecutionPolicy Bypass -File scripts/deploy-cloud-build.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Cloud Build ile deployment başlatılıyor..." -ForegroundColor Cyan

$PROJECT_ID = "finasis-478502"
$REGION = "europe-west1"
$REPOSITORY = "finasis-app"
$SERVICE = "finasis-api"
$CLOUD_RUN_SERVICE = "finasis-prod"
$IMAGE_TAG = "latest"

# Proje dizinine geç
if (Test-Path "~/FinAsis") {
    Set-Location ~/FinAsis
} elseif (Test-Path "D:\FinAsis") {
    Set-Location D:\FinAsis
} else {
    Write-Host "❌ FinAsis dizini bulunamadı!" -ForegroundColor Red
    exit 1
}

# Git durumunu kontrol et
Write-Host "📊 Git durumu kontrol ediliyor..." -ForegroundColor Yellow
git status

# Son değişiklikleri al (opsiyonel)
$pull = Read-Host "Son değişiklikleri pull etmek ister misiniz? (y/N)"
if ($pull -eq "y" -or $pull -eq "Y") {
    git pull origin main
}

# Cloud Build'i tetikle
Write-Host "🔨 Cloud Build başlatılıyor..." -ForegroundColor Yellow
gcloud builds submit `
    --config=deploy/cloud_run/cloudbuild.yaml `
    --substitutions="_IMAGE_TAG=$IMAGE_TAG" `
    --project=$PROJECT_ID `
    --region=$REGION

Write-Host "✅ Deployment tamamlandı!" -ForegroundColor Green

# Servis URL'ini göster
$SERVICE_URL = gcloud run services describe $CLOUD_RUN_SERVICE `
    --region=$REGION `
    --project=$PROJECT_ID `
    --format="value(status.url)"

Write-Host "🌐 Servis URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host "🏥 Health check: $SERVICE_URL/health/" -ForegroundColor Cyan

