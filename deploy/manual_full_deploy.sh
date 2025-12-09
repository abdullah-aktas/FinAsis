#!/bin/bash
# Manuel tam deployment script - Cloud Shell'de çalıştırılır
set -euo pipefail

# Renkli output için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ayarlar
PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
IMAGE_SERVICE="finasis-api"
REPOSITORY="finasis-app"
IMAGE_TAG="latest"
CLOUD_SQL_CONNECTION="finasis-478502:europe-west1:finasis-db"

echo -e "${BLUE}🚀 FinAsis Manuel Tam Deployment${NC}"
echo "=================================="
echo -e "Proje: ${GREEN}$PROJECT_ID${NC}"
echo -e "Bölge: ${GREEN}$REGION${NC}"
echo -e "Servis: ${GREEN}$SERVICE_NAME${NC}"
echo -e "Image: ${GREEN}$IMAGE_SERVICE:$IMAGE_TAG${NC}"
echo ""

# 1. Projeyi ayarla
echo -e "${YELLOW}📋 1. Proje ayarlanıyor...${NC}"
gcloud config set project $PROJECT_ID
echo -e "${GREEN}✅ Proje ayarlandı${NC}"
echo ""

# 1.5. Gerekli API'leri kontrol et ve etkinleştir
echo -e "${YELLOW}🔧 1.5. Gerekli API'ler kontrol ediliyor...${NC}"

# Cloud Build API
if ! gcloud services list --enabled --filter="name:cloudbuild.googleapis.com" --format="value(name)" | grep -q cloudbuild; then
    echo -e "${YELLOW}⚠️  Cloud Build API etkin değil, etkinleştiriliyor...${NC}"
    gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
    echo -e "${BLUE}   API etkinleştiriliyor, 30 saniye bekleniyor...${NC}"
    sleep 30
fi
echo -e "${GREEN}✅ Cloud Build API etkin${NC}"

# Cloud Run API
if ! gcloud services list --enabled --filter="name:run.googleapis.com" --format="value(name)" | grep -q run; then
    echo -e "${YELLOW}⚠️  Cloud Run API etkin değil, etkinleştiriliyor...${NC}"
    gcloud services enable run.googleapis.com --project=$PROJECT_ID
    sleep 10
fi
echo -e "${GREEN}✅ Cloud Run API etkin${NC}"

# Artifact Registry API
if ! gcloud services list --enabled --filter="name:artifactregistry.googleapis.com" --format="value(name)" | grep -q artifactregistry; then
    echo -e "${YELLOW}⚠️  Artifact Registry API etkin değil, etkinleştiriliyor...${NC}"
    gcloud services enable artifactregistry.googleapis.com --project=$PROJECT_ID
    sleep 10
fi
echo -e "${GREEN}✅ Artifact Registry API etkin${NC}"

# Artifact Registry repository kontrolü
if ! gcloud artifacts repositories describe $REPOSITORY \
    --location=$REGION \
    --project=$PROJECT_ID \
    --format="value(name)" >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Artifact Registry repository bulunamadı, oluşturuluyor...${NC}"
    gcloud artifacts repositories create $REPOSITORY \
        --repository-format=docker \
        --location=$REGION \
        --project=$PROJECT_ID \
        --description="FinAsis application Docker images" || {
        echo -e "${RED}❌ Artifact Registry repository oluşturulamadı!${NC}"
        exit 1
    }
    echo -e "${GREEN}✅ Artifact Registry repository oluşturuldu${NC}"
else
    echo -e "${GREEN}✅ Artifact Registry repository mevcut${NC}"
fi
echo ""

# 2. Git pull (son değişiklikleri al)
echo -e "${YELLOW}📥 2. Git pull yapılıyor...${NC}"
cd ~/FinAsis || { echo -e "${RED}❌ FinAsis dizini bulunamadı!${NC}"; exit 1; }

# Yerel değişiklikleri kontrol et ve handle et
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  Yerel değişiklikler bulundu, stash ediliyor...${NC}"
    git stash push -m "Auto-stash before deployment $(date +%Y%m%d_%H%M%S)" || {
        echo -e "${YELLOW}⚠️  Stash başarısız, yerel değişiklikler restore ediliyor...${NC}"
        git restore . || echo -e "${YELLOW}⚠️  Restore başarısız, devam ediliyor...${NC}"
    }
fi

# Git pull yap
git pull origin main || {
    echo -e "${RED}❌ Git pull başarısız!${NC}"
    exit 1
}
echo -e "${GREEN}✅ Git pull tamamlandı${NC}"
echo ""

# 3. Mevcut environment variables'ı al
echo -e "${YELLOW}🔍 3. Mevcut environment variables kontrol ediliyor...${NC}"
EXISTING_ENV_JSON=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="json" 2>/dev/null || echo "{}")

EXISTING_ENV_VARS=$(echo "$EXISTING_ENV_JSON" | jq -r '.spec.template.spec.containers[0].env[]? | "\(.name)=\(.value)"' 2>/dev/null | tr '\n' ',' | sed 's/,$//' || echo "")

if [ -n "$EXISTING_ENV_VARS" ]; then
  echo -e "${GREEN}✅ Mevcut environment variables bulundu:${NC}"
  echo "$EXISTING_ENV_VARS" | tr ',' '\n' | sed 's/^/   /'
else
  echo -e "${YELLOW}⚠️  Mevcut environment variables bulunamadı (yeni servis olabilir)${NC}"
fi
echo ""

# 4. Cloud Build Submit
echo -e "${YELLOW}🔨 4. Cloud Build başlatılıyor...${NC}"
echo -e "${BLUE}   Bu işlem 5-10 dakika sürebilir...${NC}"

# Substitutions hazırla
SUBSTITUTIONS="_PYTHON_VERSION=3.11,_REGION=$REGION,_SERVICE=$IMAGE_SERVICE,_CLOUD_RUN_SERVICE=$SERVICE_NAME,_REPOSITORY=$REPOSITORY,_IMAGE_TAG=$IMAGE_TAG,_CLOUD_SQL_CONNECTION=$CLOUD_SQL_CONNECTION,_CLOUD_RUN_ENV_VARS=,_CLOUD_RUN_SECRETS="

gcloud builds submit \
  --config=deploy/cloud_run/cloudbuild.yaml \
  --region=$REGION \
  --substitutions="$SUBSTITUTIONS" \
  --project=$PROJECT_ID

BUILD_EXIT_CODE=$?

if [ $BUILD_EXIT_CODE -eq 0 ]; then
  echo -e "${GREEN}✅ Cloud Build başarıyla tamamlandı!${NC}"
else
  echo -e "${RED}❌ Cloud Build başarısız oldu!${NC}"
  exit 1
fi
echo ""

# 5. Deployment kontrolü
echo -e "${YELLOW}🔍 5. Deployment kontrol ediliyor...${NC}"
sleep 5

# Servis URL'ini al
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
  echo -e "${GREEN}✅ Servis URL: $SERVICE_URL${NC}"
else
  echo -e "${RED}❌ Servis URL alınamadı!${NC}"
fi

# Environment variables'ı kontrol et
echo ""
echo -e "${YELLOW}📊 Environment Variables Kontrolü:${NC}"
gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="json" | jq -r '.spec.template.spec.containers[0].env[]? | "\(.name)=\(.value)"' | grep -E "(DEBUG|DB_|DJANGO_)" | sed 's/^/   /' || echo "   (Bulunamadı)"

echo ""

# 6. Health check
echo -e "${YELLOW}🏥 6. Health check yapılıyor...${NC}"
if [ -n "$SERVICE_URL" ]; then
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$SERVICE_URL" || echo "000")
  if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "${GREEN}✅ Health check başarılı (HTTP $HTTP_CODE)${NC}"
  else
    echo -e "${YELLOW}⚠️  Health check: HTTP $HTTP_CODE (Beklenen: 200/301/302)${NC}"
    echo -e "${BLUE}   Servis başlatılıyor olabilir, birkaç dakika bekleyin...${NC}"
  fi
else
  echo -e "${YELLOW}⚠️  Servis URL bulunamadı, health check atlandı${NC}"
fi
echo ""

# 7. Son logları göster
echo -e "${YELLOW}📋 7. Son loglar (ilk 20 satır):${NC}"
gcloud run services logs read $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --limit=20 \
  --format="table(timestamp,severity,textPayload)" 2>/dev/null | head -25 || echo "   Loglar alınamadı"

echo ""
echo -e "${GREEN}🎉 Deployment tamamlandı!${NC}"
echo ""
echo -e "${BLUE}📊 İzleme:${NC}"
echo "   Cloud Run: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME?project=$PROJECT_ID"
echo "   Cloud Build: https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
if [ -n "$SERVICE_URL" ]; then
  echo "   Servis URL: $SERVICE_URL"
fi
echo ""

