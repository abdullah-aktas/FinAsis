# 🚀 Hızlı Deployment Kılavuzu

## ⚡ En Hızlı Yöntem: GitHub Actions (Önerilen) ⭐

**GitHub Actions workflow optimize edildi ve disk temizliği eklendi.** Bu yöntem şimdi daha güvenilir çalışıyor.

### Otomatik Trigger:
- `main` branch'e push yapıldığında otomatik çalışır
- GitHub Actions sayfasından manuel tetiklenebilir

---

## 🔧 Alternatif: Cloud Build (API Etkinleştirme Gerekebilir)

Cloud Build kullanmak isterseniz, önce API'yi etkinleştirin:

### 1. Cloud Build API'yi Etkinleştirin

Cloud Shell'de:

```bash
# Cloud Build API'yi etkinleştir
gcloud services enable cloudbuild.googleapis.com --project=finasis-478502

# Cloud Build servis hesabının yetkilerini kontrol et
gcloud projects get-iam-policy finasis-478502 \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:*@cloudbuild.gserviceaccount.com"
```

### 2. Cloud Build ile Deploy

```bash
cd ~/FinAsis
git pull origin main

gcloud builds submit \
  --config=deploy/cloud_run/cloudbuild.yaml \
  --project=finasis-478502 \
  --region=europe-west1 .
```

**NOT:** Cloud Build config'de secrets kullanımı henüz tam değil. Şimdilik GitHub Actions ile deploy edin.

---

## ⚠️ Disk Alanı Sorunu Çözümü

### GitHub Actions'da disk alanı sorunu varsa:

1. **GitHub Actions workflow optimize edildi** - runner log/cache temizliği eklendi ✅
2. **Cloud Build kullanın** (API etkinleştirme gerekebilir) - daha fazla disk alanı
3. **Build cache'i kullanın** - Artifact Registry cache'i otomatik kullanılır

### GitHub Actions Avantajları:
- ✅ WIF (Workload Identity Federation) ile güvenli authentication
- ✅ Secrets yönetimi hazır
- ✅ Disk temizliği optimize edildi
- ✅ Otomatik trigger

### Cloud Build Avantajları:
- ✅ Daha fazla disk alanı
- ✅ Daha hızlı build (Google Cloud altyapısı)
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

- **GitHub Actions**: Önerilen yöntem (disk temizliği optimize edildi)
- **Cloud Build**: Alternatif yöntem (API etkinleştirme gerekebilir)
- **Build Süresi**: İlk build ~15-20 dakika, sonrakiler cache sayesinde daha hızlı
