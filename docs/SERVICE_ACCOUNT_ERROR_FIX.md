# Service Account Hata Düzeltme Rehberi

## Sorun

GCP log'larında şu hata tekrarlanıyor:
```
ERROR: The default service account (211704933618-compute@developer.gserviceaccount.com) has already been created.
```

Bu hata, Cloud Build veya deployment script'lerinin default compute service account'u tekrar oluşturmaya çalışmasından kaynaklanıyor.

## Çözüm

### 1. Idempotent Service Account Kontrolü

Tüm deployment script'lerinde service account oluşturma işlemlerinden önce kontrol eklenmiştir:

```bash
# Service account'un var olup olmadığını kontrol et
if gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project=$PROJECT_ID &>/dev/null; then
  echo "✅ Service account zaten mevcut"
else
  # Service account oluştur veya API'yi etkinleştir
  gcloud services enable compute.googleapis.com --project=$PROJECT_ID
fi
```

### 2. Helper Script Kullanımı

`scripts/ensure-service-account.sh` helper script'i oluşturulmuştur:

```bash
# Kullanım
bash scripts/ensure-service-account.sh \
  "211704933618-compute@developer.gserviceaccount.com" \
  "Default compute service account"
```

Bu script:
- Service account'un var olup olmadığını kontrol eder
- Yoksa otomatik oluşturur (Compute Engine API etkinleştirerek)
- "Already exists" hatalarını ignore eder

### 3. Güncellenmiş Script'ler

Aşağıdaki script'ler güncellenmiştir:

- `scripts/deploy-production-cloud-shell.sh`
- `scripts/build-and-deploy-cloud-shell.sh`
- `scripts/setup-and-deploy.sh`
- `scripts/deploy-cloud-run-manual.sh`
- `scripts/create-runner-vm.sh`
- `deploy/cloud_run/cloudbuild.yaml`

### 4. Cloud Build YAML Güncellemesi

`deploy/cloud_run/cloudbuild.yaml` dosyasında service account kontrolü eklendi:

```yaml
# Service account'u kontrol et ve ayarla (idempotent)
EXISTING_SA=$(gcloud run services describe ${_CLOUD_RUN_SERVICE} \
  --region=${_REGION} \
  --project=$PROJECT_ID \
  --format="value(spec.template.spec.serviceAccountName)" 2>/dev/null || echo "")

if [ -n "$${EXISTING_SA}" ]; then
  DEPLOY_ARGS+=("--service-account=$${EXISTING_SA}")
else
  # Default compute service account'u kontrol et
  # ...
fi
```

## Kullanım

### Otomatik Düzeltme Script'i

```bash
bash scripts/fix-service-account-errors.sh
```

Bu script:
1. Default compute service account'u kontrol eder
2. Cloud Build service account'u kontrol eder
3. Helper script'i oluşturur
4. Öneriler sunar

### Manuel Kontrol

```bash
PROJECT_ID="finasis-478502"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Service account var mı?
gcloud iam service-accounts describe "$COMPUTE_SA" --project=$PROJECT_ID
```

## Sonuç

Bu güncellemelerle:
- ✅ Service account oluşturma hataları önlenir
- ✅ "Already exists" hataları ignore edilir
- ✅ Deployment script'leri idempotent hale gelir
- ✅ Log'larda ERROR sayısı azalır

## Notlar

- Default compute service account, Compute Engine API etkinleştirildiğinde otomatik oluşturulur
- Cloud Build service account, Cloud Build API etkinleştirildiğinde otomatik oluşturulur
- Bu service account'ları manuel oluşturmaya gerek yoktur
- Script'ler artık bu service account'ların varlığını kontrol eder ve yoksa API'yi etkinleştirir

