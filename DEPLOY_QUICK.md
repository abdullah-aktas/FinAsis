# 🚀 Hızlı Deployment Kılavuzu

## ⚡ En Hızlı Yöntem: Cloud Build (Önerilen)

GitHub Actions disk alanı sorunu yaşandığında Cloud Build kullanın.

### Cloud Shell'de Tek Komut:

```bash
cd ~/FinAsis && gcloud builds submit --config=deploy/cloud_run/cloudbuild.yaml --project=finasis-478502 --region=europe-west1
```

### Veya Script ile:

```bash
bash scripts/deploy-cloud-build.sh
```

---

## 🔧 Alternatif: GitHub Actions (Optimize Edilmiş)

GitHub Actions workflow'u optimize edildi ve disk temizliği eklendi. Şimdi daha iyi çalışmalı.

### Otomatik Trigger:
- `main` branch'e push yapıldığında otomatik çalışır
- GitHub Actions sayfasından manuel tetiklenebilir

---

## 📋 Adım Adım Cloud Build Deployment

### 1. Cloud Shell'i Açın
- https://shell.cloud.google.com/
- Proje: `finasis-478502`

### 2. Proje Dizinine Geçin
```bash
cd ~/FinAsis
```

### 3. Son Değişiklikleri Alın (Opsiyonel)
```bash
git pull origin main
```

### 4. Cloud Build'i Başlatın
```bash
gcloud builds submit \
  --config=deploy/cloud_run/cloudbuild.yaml \
  --project=finasis-478502 \
  --region=europe-west1
```

### 5. Deployment'ı İzleyin
Build logları terminal'de görünecek. İlerlemeyi takip edebilirsiniz.

---

## ⚠️ Disk Alanı Sorunu Çözümü

### GitHub Actions'da disk alanı sorunu varsa:

1. **Cloud Build kullanın** (en hızlı çözüm) ⬆️
2. **GitHub Actions workflow'u optimize edildi** - disk temizliği eklendi
3. **Build cache'i kullanın** - Artifact Registry cache'i otomatik kullanılır

### Cloud Build Avantajları:
- ✅ Daha fazla disk alanı
- ✅ Daha hızlı build (Google Cloud altyapısı)
- ✅ Daha güvenilir
- ✅ Detaylı loglar

---

## 🔍 Deployment Kontrolü

### Servis Durumunu Kontrol Etme:
```bash
gcloud run services describe finasis-prod \
  --region=europe-west1 \
  --project=finasis-478502
```

### Health Check:
```bash
SERVICE_URL=$(gcloud run services describe finasis-prod \
  --region=europe-west1 \
  --project=finasis-478502 \
  --format="value(status.url)")

curl $SERVICE_URL/health/
```

---

## 📝 Notlar

- **Cloud Build**: Disk alanı sorunu yaşandığında önerilen yöntem
- **GitHub Actions**: Optimize edildi, ama yine de disk sorunu olabilir
- **Build Süresi**: İlk build ~15-20 dakika, sonrakiler cache sayesinde daha hızlı

