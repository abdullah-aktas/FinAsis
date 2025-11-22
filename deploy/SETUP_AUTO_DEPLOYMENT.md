# Otomatik Deployment Kurulumu

Bu rehber, GitHub'a push yapıldığında otomatik olarak Cloud Run'a deploy eden sistemi kurmanızı sağlar.

## 🎯 Seçenek 1: GitHub Actions (Önerilen)

### Adım 1: Google Cloud Service Account Oluşturun

Cloud Shell'de çalıştırın:

```bash
# Service Account oluştur
gcloud iam service-accounts create github-actions-deploy \
  --display-name="GitHub Actions Deploy" \
  --project=YOUR_PROJECT_ID

# Gerekli roller verin
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Service Account Key oluştur
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### Adım 2: GitHub Secrets Ayarlayın

1. GitHub repository'nize gidin
2. **Settings** > **Secrets and variables** > **Actions** > **New repository secret**

Şu secret'ları ekleyin:

- `GCP_PROJECT_ID`: Google Cloud proje ID'niz (örn: `finasis-478502`)
- `GCP_SA_KEY`: `github-actions-key.json` dosyasının içeriği (tüm JSON'u kopyalayın)

### Adım 3: Workflow Dosyasını Kontrol Edin

`.github/workflows/deploy.yml` dosyası zaten oluşturuldu. İçeriğini kontrol edin ve gerekirse düzenleyin.

### Adım 4: Test Edin

```bash
# Local'de bir değişiklik yapın
echo "# Test" >> README.md
git add README.md
git commit -m "Test: Auto deployment"
git push origin main
```

GitHub Actions sekmesinden deployment'ı izleyebilirsiniz.

## 🎯 Seçenek 2: Cloud Build Trigger

### Adım 1: Cloud Build Trigger Oluşturun

Cloud Shell'de:

```bash
gcloud builds triggers create github \
  --name="finasis-auto-deploy" \
  --repo-name="FinAsis" \
  --repo-owner="abdullah-aktas" \
  --branch-pattern="^main$" \
  --build-config="deploy/cloud_run/cloudbuild.yaml" \
  --region="europe-west1" \
  --substitutions="_SERVICE=finasis-prod"
```

### Adım 2: GitHub Bağlantısını Yapın

1. Google Cloud Console > **Cloud Build** > **Triggers**
2. Oluşturduğunuz trigger'ı seçin
3. **Connect repository** butonuna tıklayın
4. GitHub hesabınızı bağlayın ve repository'yi seçin

### Adım 3: Test Edin

```bash
# Bir değişiklik yapın ve push edin
git commit --allow-empty -m "Test: Cloud Build trigger"
git push origin main
```

Cloud Build Console'dan build'i izleyebilirsiniz.

## 🔄 Her Push'ta Otomatik Deploy

Her iki yöntem de `main` branch'ine push yapıldığında otomatik olarak deploy eder.

### Sadece Belirli Dosyalar Değiştiğinde Deploy

GitHub Actions workflow'u zaten belirli dosya tiplerini kontrol ediyor:
- Python dosyaları (`.py`)
- Template dosyaları (`.html`)
- JavaScript/CSS dosyaları
- Dockerfile ve requirements.txt
- Config ve deploy dosyaları

### Manuel Deploy

Eğer otomatik deploy'u atlamak isterseniz:

**GitHub Actions için:**
- Commit mesajına `[skip ci]` veya `[skip deploy]` ekleyin

**Cloud Build Trigger için:**
- Farklı bir branch'e push edin (örn: `develop`)

## 📊 Deployment Durumunu İzleme

### GitHub Actions

1. GitHub repository > **Actions** sekmesi
2. Son deployment'ı görüntüleyin
3. Logları inceleyin

### Cloud Build

```bash
# Son build'leri listeleyin
gcloud builds list --limit=10

# Belirli bir build'in loglarını görüntüleyin
gcloud builds log BUILD_ID
```

## 🚨 Sorun Giderme

### GitHub Actions Başarısız Olursa

1. **Secrets kontrolü:**
   - `GCP_PROJECT_ID` doğru mu?
   - `GCP_SA_KEY` geçerli bir JSON mu?

2. **Permissions kontrolü:**
   ```bash
   gcloud projects get-iam-policy YOUR_PROJECT_ID \
     --flatten="bindings[].members" \
     --filter="bindings.members:github-actions-deploy@*"
   ```

3. **Logları kontrol edin:**
   - GitHub Actions > Son workflow run > Logs

### Cloud Build Trigger Çalışmıyorsa

1. **Trigger durumunu kontrol edin:**
   ```bash
   gcloud builds triggers list
   ```

2. **Manuel test:**
   ```bash
   gcloud builds triggers run TRIGGER_NAME \
     --branch=main
   ```

## ✅ Kurulum Kontrol Listesi

- [ ] Service Account oluşturuldu
- [ ] Gerekli roller verildi
- [ ] Service Account key oluşturuldu
- [ ] GitHub Secrets ayarlandı
- [ ] Workflow dosyası kontrol edildi
- [ ] Test deployment yapıldı
- [ ] Deployment başarılı oldu

## 🎉 Sonuç

Kurulum tamamlandıktan sonra, `main` branch'ine her push yaptığınızda otomatik olarak:

1. ✅ Kod test edilir (varsa)
2. ✅ Docker image build edilir
3. ✅ Cloud Run'a deploy edilir
4. ✅ Health check yapılır

Artık manuel deployment yapmanıza gerek yok! 🚀

