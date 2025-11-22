# FinAsis Cloud Shell Kullanım Kılavuzu

Google Cloud Shell için hazırlanmış diagnostic ve yönetim script'i.

## 🚀 Hızlı Başlangıç

### 1. Cloud Shell'i Açın
Google Cloud Console'da Cloud Shell ikonuna tıklayın veya [shell.cloud.google.com](https://shell.cloud.google.com) adresine gidin.

### 2. Projeyi Klonlayın
```bash
git clone <repository-url>
cd FinAsis
```

### 3. Script'i Çalıştırılabilir Yapın
```bash
chmod +x deploy/cloud_shell_prompt.sh
```

## 📋 Kullanılabilir Komutlar

### Temel Komutlar

#### Proje ve Servis Durumu
```bash
./deploy/cloud_shell_prompt.sh status
```
- Aktif Google Cloud projesini gösterir
- Cloud Run servis durumunu kontrol eder
- Servis URL'sini ve konfigürasyonunu gösterir

#### Logları Görüntüleme
```bash
# Son 50 satır (varsayılan)
./deploy/cloud_shell_prompt.sh logs

# Son 100 satır
./deploy/cloud_shell_prompt.sh logs 100
```

#### Hata Logları
```bash
./deploy/cloud_shell_prompt.sh errors
```
Sadece ERROR ve CRITICAL seviyesindeki logları gösterir.

#### Canlı Log Takibi
```bash
./deploy/cloud_shell_prompt.sh tail
```
Logları canlı olarak takip eder (tail -f benzeri). Çıkmak için `Ctrl+C`.

### Gelişmiş Komutlar

#### Servis Metrikleri
```bash
./deploy/cloud_shell_prompt.sh metrics
```
- Request sayısı
- Memory kullanımı
- CPU kullanımı
- Response time

#### Environment Variables
```bash
./deploy/cloud_shell_prompt.sh env
```
Cloud Run servisindeki tüm environment variables'ı listeler.

#### Database Kontrolü
```bash
./deploy/cloud_shell_prompt.sh db
```
- Cloud SQL instance'larını listeler
- Cloud Run servisinin database bağlantılarını kontrol eder

#### Deployment Hazırlık
```bash
./deploy/cloud_shell_prompt.sh ready
```
- Python ve Django versiyonlarını kontrol eder
- Django sistem kontrollerini çalıştırır
- Migration durumunu gösterir

#### Tam Diagnostic
```bash
./deploy/cloud_shell_prompt.sh diagnostic
```
Tüm kontrolleri sırayla çalıştırır ve kapsamlı bir rapor oluşturur.

## 🔧 Environment Variables

Script, aşağıdaki environment variables'ı kullanabilir:

```bash
export REGION="europe-west4"           # Cloud Run bölgesi
export SERVICE_NAME="finasis-api"      # Cloud Run servis adı
export REPOSITORY="finasis-app"        # Container registry repository adı
```

Varsayılan değerler script içinde tanımlıdır.

## 📊 Örnek Kullanım Senaryoları

### Senaryo 1: Servis Hata Veriyor
```bash
# 1. Servis durumunu kontrol et
./deploy/cloud_shell_prompt.sh status

# 2. Hata loglarını incele
./deploy/cloud_shell_prompt.sh errors

# 3. Canlı logları takip et
./deploy/cloud_shell_prompt.sh tail
```

### Senaryo 2: Deployment Öncesi Kontrol
```bash
# Tam diagnostic çalıştır
./deploy/cloud_shell_prompt.sh diagnostic

# Environment variables'ı kontrol et
./deploy/cloud_shell_prompt.sh env

# Database bağlantısını kontrol et
./deploy/cloud_shell_prompt.sh db
```

### Senaryo 3: Performans İncelemesi
```bash
# Metrikleri görüntüle
./deploy/cloud_shell_prompt.sh metrics

# Son logları incele
./deploy/cloud_shell_prompt.sh logs 200
```

## 🛠️ Manuel Komutlar

Script kullanmak istemezseniz, aşağıdaki komutları doğrudan kullanabilirsiniz:

### Logları Görüntüleme
```bash
# Son 50 satır
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=finasis-api" \
    --limit=50 \
    --format="table(timestamp,severity,textPayload)" \
    --project=$(gcloud config get-value project)

# Canlı log takibi
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=finasis-api" \
    --format="table(timestamp,severity,textPayload)" \
    --project=$(gcloud config get-value project)
```

### Servis Bilgileri
```bash
# Servis detayları
gcloud run services describe finasis-api \
    --region=europe-west4 \
    --format="yaml"

# Servis URL'si
gcloud run services describe finasis-api \
    --region=europe-west4 \
    --format="value(status.url)"
```

### Environment Variables
```bash
gcloud run services describe finasis-api \
    --region=europe-west4 \
    --format="value(spec.template.spec.containers[0].env)"
```

## 🐛 Sorun Giderme

### Script Çalışmıyor
```bash
# Çalıştırma iznini kontrol et
ls -la deploy/cloud_shell_prompt.sh

# İzin ver
chmod +x deploy/cloud_shell_prompt.sh
```

### Proje Bulunamıyor
```bash
# Aktif projeyi kontrol et
gcloud config get-value project

# Proje ayarla
gcloud config set project YOUR_PROJECT_ID
```

### Servis Bulunamıyor
Script, varsayılan olarak `finasis-api` servis adını arar. Farklı bir isim kullanıyorsanız:

```bash
export SERVICE_NAME="your-service-name"
./deploy/cloud_shell_prompt.sh status
```

## 📝 Notlar

- Script, Google Cloud SDK'nın (`gcloud`) yüklü ve yapılandırılmış olmasını gerektirir
- Cloud Shell'de genellikle `gcloud` zaten yüklü ve yapılandırılmıştır
- Log görüntüleme için Cloud Logging API'nin etkin olması gerekir
- Metrik görüntüleme için Cloud Monitoring API'nin etkin olması gerekir

## 🔗 İlgili Dosyalar

- `deploy/cloud_run/cloudbuild.yaml` - Cloud Build yapılandırması
- `deploy/entrypoint.sh` - Container entrypoint script'i
- `Dockerfile` - Container image tanımı
- `project_readiness_check.py` - Deployment hazırlık kontrol script'i

## 💡 İpuçları

1. **Hızlı Erişim**: Script'i `PATH`'e ekleyerek her yerden çalıştırabilirsiniz:
   ```bash
   export PATH=$PATH:$(pwd)/deploy
   cloud_shell_prompt.sh status
   ```

2. **Alias Oluşturma**: Sık kullanılan komutlar için alias oluşturun:
   ```bash
   alias finasis-logs='./deploy/cloud_shell_prompt.sh logs'
   alias finasis-errors='./deploy/cloud_shell_prompt.sh errors'
   alias finasis-status='./deploy/cloud_shell_prompt.sh status'
   ```

3. **Otomatik Kontrol**: Cron job veya scheduled task ile düzenli diagnostic çalıştırın.

