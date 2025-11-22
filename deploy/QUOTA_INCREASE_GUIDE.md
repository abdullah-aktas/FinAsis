# 📈 Cloud Run Quota Artırım Rehberi

## 🎯 50K Eşzamanlı Kullanıcı İçin Gerekli Quota'lar

### Mevcut Limitler (Varsayılan)
- **Max Instances per Service**: 50
- **CPU per Project per Region**: 200 vCPU
- **Memory per Project per Region**: 400GB

### Gerekli Limitler (50K Users)
- **Max Instances per Service**: 500
- **CPU per Project per Region**: 2000+ vCPU
- **Memory per Project per Region**: 2000GB+ (2TB)

## 📋 Quota Artırım Adımları

### Yöntem 1: Google Cloud Console (Önerilen)

1. **Google Cloud Console'a gidin**
   - https://console.cloud.google.com

2. **IAM & Admin → Quotas'a gidin**
   - Sol menüden "IAM & Admin" → "Quotas"

3. **Filtreleme**
   - **Service**: "Cloud Run API"
   - **Location**: "europe-west1" (veya kullandığınız bölge)
   - **Metric**: 
     - "CPU allocation per project per region"
     - "Memory allocation per project per region"
     - "Max instances per service"

4. **Quota Artırım Talebi**
   - Her quota için "Edit Quotas" butonuna tıklayın
   - Yeni limit değerini girin
   - Gerekçe açıklaması yazın:
     ```
     Production deployment için 50,000 eşzamanlı kullanıcıyı 
     desteklemek amacıyla quota artırımı talep ediyoruz.
     
     Gerekli kapasite:
     - 500 instances × 4 CPU = 2000 vCPU
     - 500 instances × 4GB = 2000GB memory
     - Max instances: 500
     ```
   - "Submit Request" butonuna tıklayın

5. **Onay Bekleme**
   - Quota artırım talepleri genellikle 24-48 saat içinde onaylanır
   - Email ile bilgilendirilirsiniz

### Yöntem 2: gcloud CLI

```bash
# Quota bilgilerini görüntüle
gcloud compute project-info describe \
  --project=$(gcloud config get-value project) \
  --format="table(quotas.metric,quotas.limit,quotas.usage)"

# Quota artırım talebi için support case oluştur
# Not: gcloud CLI ile doğrudan quota artırımı yapılamaz
# Support case oluşturmanız gerekir
```

### Yöntem 3: Support Case

1. **Google Cloud Support'a başvurun**
   - https://cloud.google.com/support
   - "Create Case" → "Quota Increase"

2. **Detaylı bilgi verin**
   - Kullanım amacı
   - Beklenen trafik
   - Mevcut ve istenen limitler
   - İş gereksinimleri

## 🔧 Geçici Çözüm: Mevcut Quota ile Optimizasyon

Quota artırımı onaylanana kadar mevcut limitlerle optimize edebilirsiniz:

### Optimize Edilmiş Yapılandırma

```bash
# Mevcut quota limitleri ile (50 instances max)
gcloud run services update finasis-prod \
    --region=europe-west1 \
    --memory=3Gi \
    --cpu=4 \
    --concurrency=200 \
    --min-instances=10 \
    --max-instances=50 \
    --cpu-boost \
    --project=$(gcloud config get-value project)
```

**Kapasite Hesaplaması:**
- 50 instances × 200 concurrency = **10,000 eşzamanlı request**
- 50 instances × 4 CPU = 200 vCPU (limit)
- 50 instances × 3GB = 150GB memory (limit içinde)

### Daha Fazla Kapasite İçin

1. **Concurrency'yi artırın** (200 → 300-400)
   - Risk: Her instance daha fazla yük alır
   - Test ederek optimize edin

2. **Multi-Region Deployment**
   - Farklı bölgelerde servisler oluşturun
   - Load balancer ile dağıtın
   - Her bölge kendi quota'sını kullanır

3. **Hybrid Approach**
   - Cloud Run + Compute Engine
   - Kritik olmayan işlemleri Compute Engine'e taşıyın

## 📊 Quota Kontrol Komutları

```bash
# Mevcut quota kullanımını kontrol et
gcloud compute project-info describe \
  --project=$(gcloud config get-value project) \
  --format="table(quotas.metric,quotas.limit,quotas.usage)"

# Cloud Run servis limitlerini kontrol et
gcloud run services describe finasis-prod \
    --region=europe-west1 \
    --format="yaml(spec.template.spec)" \
    --project=$(gcloud config get-value project)
```

## ⚠️ Önemli Notlar

1. **Quota Artırım Süresi**
   - Genellikle 24-48 saat
   - Acil durumlarda support'a öncelik talebi yapabilirsiniz

2. **Maliyet**
   - Quota artırımı ücretsizdir
   - Ancak kullandığınız kaynaklar için ücretlendirilirsiniz

3. **Alternatif Bölgeler**
   - Farklı bölgelerde farklı quota limitleri olabilir
   - Multi-region deployment düşünülebilir

4. **Kademeli Artırım**
   - İlk başta düşük limitlerle başlayın
   - Trafiğe göre kademeli artırın

## 🎯 50K Users İçin Önerilen Strateji

### Aşama 1: Mevcut Quota ile Başlangıç
- 50 instances, 200 concurrency
- Kapasite: ~10,000 eşzamanlı
- Test ve optimizasyon

### Aşama 2: Quota Artırımı
- 500 instances, 100 concurrency
- Kapasite: 50,000 eşzamanlı
- Production deployment

### Aşama 3: Optimizasyon
- Monitoring ve analiz
- Gereksiz kaynak kullanımını azaltma
- Cost optimization

## 📞 Destek

Quota artırımı ile ilgili sorularınız için:
- Google Cloud Support: https://cloud.google.com/support
- Quota Documentation: https://cloud.google.com/run/quotas

