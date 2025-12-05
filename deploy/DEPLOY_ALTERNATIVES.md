# Cloud Build Sorunu - Alternatif Deploy Yöntemleri

Cloud Build API `NOT_FOUND` hatası alıyorsanız, aşağıdaki alternatif yöntemleri kullanabilirsiniz.

## Yöntem 1: Doğru Cloud Build Config ile Deploy

Root'taki `cloudbuild.yaml` sadece test yapar. Gerçek deploy için:

```bash
cd ~/FinAsis

# Cloud Build API'sini kontrol et
gcloud services list --enabled --filter="name:cloudbuild.googleapis.com"

# Eğer etkin değilse
gcloud services enable cloudbuild.googleapis.com

# Doğru config ile deploy
gcloud builds submit \
  --config=deploy/cloud_run/cloudbuild.yaml \
  --region=europe-west1 \
  --substitutions=_SERVICE=finasis-prod,_REGION=europe-west1,_REPOSITORY=finasis-app,_IMAGE_TAG=latest
```

## Yöntem 2: Deploy Script Kullan

```bash
cd ~/FinAsis

# Deploy script'ini çalıştır
chmod +x deploy_to_cloud_run.sh
./deploy_to_cloud_run.sh
```

## Yöntem 3: Manuel Cloud Run Deploy

Eğer mevcut bir image varsa:

```bash
# Mevcut servisi güncelle (kod değişiklikleri için yeni image gerekir)
gcloud run services update finasis-prod \
  --region=europe-west1 \
  --platform=managed
```

## Yöntem 4: Cloud Build API İzinlerini Kontrol Et

```bash
# Cloud Build servis hesabını kontrol et
PROJECT_NUMBER=$(gcloud projects describe finasis-478502 --format="value(projectNumber)")
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Gerekli rolleri kontrol et
gcloud projects get-iam-policy finasis-478502 \
  --flatten="bindings[].members" \
  --filter="bindings.members:${CLOUD_BUILD_SA}"

# Eğer eksikse, rolleri ekle
gcloud projects add-iam-policy-binding finasis-478502 \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding finasis-478502 \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/artifactregistry.writer"
```

## Yöntem 5: GitHub Actions ile Deploy

Eğer GitHub Actions kuruluysa, otomatik deploy yapılır. Manuel tetiklemek için:

1. GitHub repo'ya git
2. Actions sekmesine git
3. "Deploy to Cloud Run" workflow'unu bul
4. "Run workflow" butonuna tıkla

## Hızlı Çözüm: Sadece Kod Değişiklikleri İçin

Eğer sadece kod değişiklikleri varsa (health check endpoint'leri gibi) ve mevcut image çalışıyorsa, Cloud Run servisini yeniden başlatmak yeterli olabilir:

```bash
# Servisi yeniden başlat (yeni kod için yeni image gerekir)
gcloud run services update finasis-prod \
  --region=europe-west1 \
  --platform=managed \
  --no-traffic
```

**Not:** Kod değişiklikleri için mutlaka yeni image build edilmesi gerekir.

