# 🚀 50K Kullanıcı için Hızlı Başlangıç

## ⚡ Tek Komutla Deployment

```bash
# Script'i çalıştırılabilir yapın
chmod +x deploy/deploy_50k_production.sh

# Deployment'ı başlatın
./deploy/deploy_50k_production.sh
```

## 📋 Manuel Adımlar

### 1. Gerekli Servisleri Oluştur

```bash
# Cloud SQL
gcloud sql instances create finasis-prod-db \
  --database-version=POSTGRES_15 \
  --tier=db-highmem-16 \
  --region=europe-west1 \
  --storage-size=500GB

# Redis
gcloud redis instances create finasis-redis \
  --size=4 \
  --region=europe-west1 \
  --redis-version=redis_7_0
```

### 2. Deployment

```bash
# Cloud Build ile deploy
gcloud builds submit \
  --config=deploy/production_50k_users.yaml \
  --project=$(gcloud config get-value project)
```

## 🎯 Önemli Notlar

1. **Maliyet**: ~$4,000-6,000/ay tahmini
2. **Süre**: İlk deployment 30-60 dakika sürebilir
3. **Monitoring**: Cloud Monitoring'de dashboard oluşturun
4. **Load Testing**: K6 ile test edin

## 📚 Detaylı Dokümantasyon

- [Production Deployment Rehberi](PRODUCTION_50K_DEPLOYMENT.md)
- [Load Testing](load_test_k6.js)

