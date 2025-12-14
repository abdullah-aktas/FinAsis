# Self-Hosted Runner Kurulum Rehberi

## ⚠️ Önemli Not

**Cloud Shell geçici bir ortamdır** ve self-hosted runner için uygun değildir. Self-hosted runner için **kalıcı bir VM** (Google Cloud Compute Engine, AWS EC2, vb.) kullanmalısınız.

## 📋 Adım Adım Kurulum

### 1. VM Oluşturun (Google Cloud Compute Engine)

```bash
# Compute Engine'de VM oluşturun
gcloud compute instances create finasis-runner \
  --zone=europe-west1-b \
  --machine-type=e2-standard-8 \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --project=finasis-478502

# VM'e SSH ile bağlanın
gcloud compute ssh finasis-runner --zone=europe-west1-b --project=finasis-478502
```

### 2. VM'de Runner'ı Kurun

```bash
# VM'de çalıştırın:
cd ~
mkdir actions-runner && cd actions-runner

# En son runner versiyonunu indirin
RUNNER_VERSION="2.311.0"
curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
  -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
```

### 3. GitHub'dan Token Alın

**ÖNEMLİ:** Token'ı doğru şekilde almanız gerekiyor:

1. GitHub repository'nize gidin: `https://github.com/abdullah-aktas/FinAsis`
2. **Settings** → **Actions** → **Runners** (sol menüden)
3. **"New runner"** butonuna tıklayın
4. **"Linux"** seçin
5. Ekranda gösterilen **token'ı kopyalayın** (örnek: `AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)
6. **Token sadece bir kez gösterilir** - kaydedin!

### 4. Runner'ı Yapılandırın

```bash
# VM'de çalıştırın (YOUR_TOKEN yerine gerçek token'ı yazın):
./config.sh \
  --url https://github.com/abdullah-aktas/FinAsis \
  --token YOUR_TOKEN \
  --name finasis-runner-1 \
  --work _work \
  --replace
```

**Örnek token formatı:** `AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` (A ile başlar, 36 karakter)

### 5. Runner'ı Servis Olarak Başlatın

```bash
# Runner'ı systemd servisi olarak kurun
sudo ./svc.sh install

# Runner'ı başlatın
sudo ./svc.sh start

# Runner durumunu kontrol edin
sudo ./svc.sh status
```

### 6. Workflow'u Güncelleyin

`.github/workflows/deploy.yml` dosyasında:

```yaml
jobs:
  deploy:
    name: Build and Deploy to Cloud Run
    runs-on: self-hosted  # ubuntu-latest yerine
    # ... geri kalanı aynı
```

## 🔧 Troubleshooting

### Token Hatası (404 Not Found)

**Sorun:** `Http response code: NotFound from 'POST https://api.github.com/actions/runner-registration'`

**Çözüm:**
1. Token'ın doğru olduğundan emin olun (Settings → Actions → Runners → "New runner" → "Linux")
2. Token'ın süresi dolmuş olabilir - yeni token alın
3. Repository'nin doğru olduğundan emin olun: `abdullah-aktas/FinAsis`

### svc.sh Bulunamıyor

**Sorun:** `sudo: ./svc.sh: command not found`

**Çözüm:**
- `config.sh` başarıyla çalışmamış olabilir
- Önce `config.sh`'ı başarıyla çalıştırın
- `config.sh` başarılı olduktan sonra `svc.sh` dosyası oluşur

### Runner Görünmüyor

1. GitHub → Settings → Actions → Runners sayfasını kontrol edin
2. Runner'ın "Idle" (boşta) durumunda olduğundan emin olun
3. Logları kontrol edin: `sudo journalctl -u actions.runner.* -f`

## 🎯 Alternatif: Cloud Build Kullanın

Self-hosted runner kurmak yerine **Cloud Build** kullanabilirsiniz - daha kolay ve hazır:

```bash
# Cloud Shell'de:
cd ~/FinAsis && git pull origin main
bash scripts/setup-cloud-build.sh
gcloud builds submit --config=deploy/cloud_run/cloudbuild.yaml --project=finasis-478502 --region=europe-west1 .
```

## 📝 Notlar

- Self-hosted runner için **kalıcı bir VM** gereklidir
- Cloud Shell geçici olduğu için uygun değildir
- VM maliyeti: ~$50-100/ay (e2-standard-8, 100GB disk)
- Runner'ı güncellemek için: `./run.sh` ile durdurun, yeni versiyonu indirin, tekrar kurun

