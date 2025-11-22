# 🚨 Cloud Run Hızlı Düzeltme Kılavuzu

Loglardan görülen sorunlar ve çözümleri:

## 🔴 Tespit Edilen Sorunlar

1. **Memory Limit Aşımı**: 512 MiB limit, 599 MiB kullanılıyor
2. **Matplotlib Cache Hatası**: Permission denied hatası
3. **Container Başlatılamıyor**: STARTUP TCP probe başarısız
4. **500 Hataları**: Servis yanıt veremiyor

## ✅ Hızlı Çözüm

### Yöntem 1: Otomatik Düzeltme Script'i (Önerilen)

Cloud Shell'de çalıştırın:

```bash
# Script'i çalıştırılabilir yapın
chmod +x deploy/fix_cloud_run_issues.sh

# Varsayılan ayarlarla çalıştırın
./deploy/fix_cloud_run_issues.sh
```

Veya özel ayarlarla:

```bash
export SERVICE_NAME="finasis-prod"
export REGION="europe-west1"
export MEMORY="2Gi"
export CPU="2"
export TIMEOUT="300"
export MIN_INSTANCES="1"
export MAX_INSTANCES="10"

./deploy/fix_cloud_run_issues.sh
```

### Yöntem 2: Manuel Komut

```bash
# Proje ID'nizi ayarlayın
export PROJECT_ID="your-project-id"
export SERVICE_NAME="finasis-prod"
export REGION="europe-west1"

# Servisi güncelleyin
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --min-instances=1 \
    --max-instances=10 \
    --set-env-vars="MPLCONFIGDIR=/tmp/matplotlib-cache,PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1" \
    --project=$PROJECT_ID
```

## 📋 Yapılan Değişiklikler

### 1. Memory Limit Artırıldı
- **Önceki**: 512 MiB
- **Yeni**: 2 GiB (2048 MiB)
- **Neden**: Matplotlib ve diğer kütüphaneler daha fazla memory gerektiriyor

### 2. Matplotlib Cache Düzeltildi
- **Environment Variable**: `MPLCONFIGDIR=/tmp/matplotlib-cache`
- **Neden**: `/nonexistent/.config/matplotlib` dizinine yazma izni yok
- **Çözüm**: `/tmp/matplotlib-cache` dizini kullanılıyor (yazılabilir)

### 3. Timeout Artırıldı
- **Önceki**: 120 saniye
- **Yeni**: 300 saniye (5 dakika)
- **Neden**: Container başlatma süresi uzun olabilir

### 4. Min Instances Eklendi
- **Yeni**: 1 minimum instance
- **Neden**: Cold start sorunlarını önlemek için

### 5. Python Ayarları
- `PYTHONUNBUFFERED=1`: Logların anında görünmesi için
- `PYTHONDONTWRITEBYTECODE=1`: .pyc dosyaları oluşturulmaz

## 🔍 Doğrulama

Değişikliklerin uygulandığını kontrol edin:

```bash
# Servis bilgilerini görüntüle
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="yaml" \
    --project=$PROJECT_ID

# Logları kontrol et
./deploy/cloud_shell_prompt.sh tail
```

## 📊 Beklenen Sonuçlar

Düzeltmelerden sonra:

✅ Memory limit aşımı hatası görülmemeli
✅ Matplotlib cache hatası çözülmeli
✅ Container başarıyla başlamalı
✅ 500 hataları azalmalı/ortadan kalkmalı
✅ Servis normal çalışmalı

## 🐛 Sorun Devam Ederse

1. **Logları kontrol edin**:
   ```bash
   ./deploy/cloud_shell_prompt.sh errors
   ```

2. **Servis durumunu kontrol edin**:
   ```bash
   ./deploy/cloud_shell_prompt.sh status
   ```

3. **Metrikleri inceleyin**:
   ```bash
   ./deploy/cloud_shell_prompt.sh metrics
   ```

4. **Yeni bir deployment yapın**:
   ```bash
   # Cloud Build ile yeni image build edin
   gcloud builds submit --config=deploy/cloud_run/cloudbuild.yaml
   ```

## 📝 Notlar

- Değişiklikler birkaç dakika içinde aktif olacaktır
- İlk istekler hala yavaş olabilir (cold start)
- Min instances=1 olduğu için sürekli bir instance çalışacak (maliyet artabilir)
- Gerekirse min instances=0 yapılabilir (cold start riski ile)

## 💰 Maliyet Etkisi

- **Memory**: 512 MiB → 2 GiB (4x artış)
- **Min Instances**: 0 → 1 (sürekli çalışan instance)
- **Tahmini maliyet artışı**: ~$30-50/ay (bölgeye göre değişir)

Maliyeti azaltmak için:
- Min instances=0 yapılabilir (cold start riski ile)
- Memory'yi 1.5 GiB'ye düşürebilirsiniz (test ederek)

