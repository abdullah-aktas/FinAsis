# 🚀 FinAsis Deployment Rehberi

## 📋 Özet

Bu rehber, FinAsis projesinin Google Cloud Run'a nasıl deploy edileceğini açıklar.

## 🔧 Yapılandırma

### Container Image Yapısı

- **Repository**: `finasis-app`
- **Image Name**: `finasis-api`
- **Service Name**: `finasis-prod` (Cloud Run service name)
- **Region**: `europe-west1`
- **Project ID**: `finasis-478502`

### Doğru Container Image URL

```
europe-west1-docker.pkg.dev/finasis-478502/finasis-app/finasis-api:latest
```

## 🎯 GitHub Actions Workflow'ları

### 1. CI Workflow (`ci.yml`)
- **Amaç**: Lint, test ve güvenlik taraması
- **Deploy Yapmaz**: Sadece kod kalitesi kontrolü
- **Trigger**: Her push ve PR'da çalışır

### 2. Deploy Workflow (`deploy.yml`)
- **Amaç**: Cloud Run'a otomatik deploy
- **Trigger**: 
  - `main` branch'e push (belirli dosya değişikliklerinde)
  - Manuel tetikleme (`workflow_dispatch`)

## 📦 Manuel Deploy (Cloud Run Console)

### Adım 1: Container Image Seçimi

1. Cloud Run Console'a gidin: https://console.cloud.google.com/run
2. `finasis-prod` servisini seçin
3. "Deploy new revision" butonuna tıklayın
4. Container image URL alanında "Select" butonuna tıklayın
5. **Doğru image'ı seçin**:
   - Repository: `europe-west1-docker.pkg.dev/finasis-478502/finasis-app`
   - Image: `finasis-api`
   - Tag: `latest` (veya en son commit hash'i)
6. "Select" butonuna tıklayın

### Adım 2: Deployment Ayarları

- **Container port**: `8080`
- **Memory**: `2 GiB`
- **CPU**: `2`
- **Request timeout**: `300` saniye
- **Concurrency**: `80`

### Adım 3: Deploy

"Deploy" butonuna tıklayın ve deployment'ın tamamlanmasını bekleyin.

## ⚠️ Önemli Notlar

1. **Otomatik Deploy**: Cloud Build trigger'ı varsa, manuel deploy'lar üzerine yazılabilir
2. **Service Name**: Cloud Run service name (`finasis-prod`) ile container image name (`finasis-api`) farklıdır
3. **Image Repository**: Artifact Registry kullanılır, eski GCR değil

## 🔍 Sorun Giderme

### CI Workflow Başarısız Oluyor

- Lint hataları varsa, local'de `ruff check .` çalıştırın
- Tüm hatalar düzeltilmiş olmalı (0 hata)

### Deploy Başarısız Oluyor

- Service name uyumsuzluğu kontrol edin
- Container image URL'ini doğrulayın
- Cloud Build loglarını kontrol edin

## 📝 Değişiklikler

- ✅ CI workflow deploy yapmıyor (sadece test/lint)
- ✅ Deploy workflow service name'i doğru kullanıyor
- ✅ Container image ve service name ayrıldı

