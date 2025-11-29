# Cloud Shell Manuel Düzeltme Adımları

Git çakışması olduğunda bu adımları takip edin:

## Adım 1: Git Çakışmasını Çöz

```bash
cd ~/FinAsis

# users_export.json'ı stash et veya sil (gitignore'da olduğu için)
git stash push -m "Stash users_export.json" users_export.json 2>/dev/null || \
git checkout -- users_export.json 2>/dev/null || \
rm -f users_export.json

# Çakışan scriptleri sil (yenilerini çekeceğiz)
rm -f deploy/check_cloud_shell_connection.sh \
      deploy/fix_cloud_build_auth.sh \
      deploy/fix_http_400_error.sh \
      deploy/test_deployment.sh \
      deploy/check_failed_build.sh

# Git pull yap
git pull origin main
```

## Adım 2: HTTP 400 Hatasını Düzelt

```bash
PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"

# Servis URL'sini al
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" 2>/dev/null)

SERVICE_HOST=$(echo "$SERVICE_URL" | sed 's|https\?://||' | sed 's|/.*||')

echo "✅ Servis URL: $SERVICE_URL"
echo "   Host: $SERVICE_HOST"

# Yeni ALLOWED_HOSTS
NEW_ALLOWED_HOSTS="finasis.com.tr,www.finasis.com.tr,$SERVICE_HOST"
echo "📝 Yeni ALLOWED_HOSTS: $NEW_ALLOWED_HOSTS"

# Environment variables'ı güncelle
ENV_VARS_UPDATE="DJANGO_ALLOWED_HOSTS=$NEW_ALLOWED_HOSTS"
ENV_VARS_UPDATE="$ENV_VARS_UPDATE,DJANGO_DEBUG=False"
ENV_VARS_UPDATE="$ENV_VARS_UPDATE,MPLCONFIGDIR=/tmp/matplotlib-cache"
ENV_VARS_UPDATE="$ENV_VARS_UPDATE,PYTHONUNBUFFERED=1"
ENV_VARS_UPDATE="$ENV_VARS_UPDATE,PYTHONDONTWRITEBYTECODE=1"

# Güncelle
gcloud run services update "$SERVICE_NAME" \
    --region="$REGION" \
    --update-env-vars="$ENV_VARS_UPDATE" \
    --quiet

echo "✅ ALLOWED_HOSTS güncellendi!"

# Health check
sleep 5
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Servis çalışıyor! (HTTP $HTTP_CODE)"
else
    echo "⚠️  Servis hala sorunlu (HTTP $HTTP_CODE)"
fi
```

## Adım 3: Cloud Build Authentication

```bash
PROJECT_ID="finasis-478502"

# Cloud Build API'sini etkinleştir
gcloud services enable cloudbuild.googleapis.com --quiet

# Compute ve Cloud Build service account'lara izin ver
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)" 2>/dev/null)
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

for SA in "$COMPUTE_SA" "$CLOUD_BUILD_SA"; do
    for ROLE in "roles/run.admin" "roles/iam.serviceAccountUser"; do
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:$SA" \
            --role="$ROLE" \
            --quiet 2>/dev/null && echo "✅ $ROLE eklendi ($SA)" || echo "ℹ️  $ROLE zaten mevcut ($SA)"
    done
done
```

## Adım 4: Deployment

```bash
gcloud builds submit \
  --config=deploy/cloud_run/cloudbuild.yaml \
  --region=europe-west1 \
  --substitutions=_SERVICE=finasis-prod
```

