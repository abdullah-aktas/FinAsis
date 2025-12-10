# Cloud SQL (PostgreSQL) Bağlantı Rehberi

Bu rehber, Cloud Run servisinin Cloud SQL PostgreSQL veritabanına bağlanması için gereken tüm adımları içerir.

## 📋 Mevcut Durum Kontrolü

### 1. Cloud SQL Instance Kontrolü

```bash
# Cloud Shell'de çalıştırın
gcloud sql instances list --project=finasis-478502
```

**Beklenen çıktı:**
```
NAME: finasis-db
DATABASE_VERSION: POSTGRES_17
LOCATION: europe-west1-b
STATUS: RUNNABLE
```

### 2. Database ve User Kontrolü

```bash
# Database'leri listele
gcloud sql databases list --instance=finasis-db --project=finasis-478502

# User'ları listele
gcloud sql users list --instance=finasis-db --project=finasis-478502
```

**Beklenen:**
- Database: `finasis` ✅
- User: `finasis-app` ✅

---

## 🔧 Eğer Database/User Yoksa

### Database Oluşturma

```bash
gcloud sql databases create finasis \
  --instance=finasis-db \
  --project=finasis-478502
```

### User Oluşturma

```bash
# Güçlü bir şifre oluştur
DB_PASSWORD=$(openssl rand -base64 32)
echo "Generated password: $DB_PASSWORD"

# User oluştur
gcloud sql users create finasis-app \
  --instance=finasis-db \
  --password="$DB_PASSWORD" \
  --project=finasis-478502

# ⚠️ ÖNEMLİ: Bu şifreyi GitHub Secrets'e ekleyin!
echo "Add this to GitHub Secrets → DJANGO_DB_PASSWORD: $DB_PASSWORD"
```

---

## 🔐 Service Account İzinleri

Cloud Run servisinin Cloud SQL'e bağlanabilmesi için service account'a izin verin:

```bash
PROJECT_ID="finasis-478502"
SERVICE_ACCOUNT="github-actions-deploy@finasis-478502.iam.gserviceaccount.com"
INSTANCE_NAME="finasis-db"
REGION="europe-west1"

# Cloud SQL Client rolü ver
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/cloudsql.client" \
  --project=$PROJECT_ID

# Cloud Run servisine Cloud SQL instance'ı ekle
gcloud run services update finasis-prod \
  --add-cloudsql-instances=$PROJECT_ID:$REGION:$INSTANCE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID
```

---

## ✅ Environment Variables Kontrolü

Cloud Run servisinde şu environment variables olmalı:

```bash
# Mevcut environment variables'ı kontrol et
gcloud run services describe finasis-prod \
  --region=europe-west1 \
  --project=finasis-478502 \
  --format="value(spec.template.spec.containers[0].env)" | grep -E "(DJANGO_DB|CLOUD_SQL)"
```

**Beklenen değerler:**
- `DJANGO_DB_ENGINE=django.db.backends.postgresql`
- `DJANGO_DB_NAME=finasis`
- `DJANGO_DB_USER=finasis-app`
- `DJANGO_DB_HOST=/cloudsql/finasis-478502:europe-west1:finasis-db`
- `CLOUD_SQL_CONNECTION_NAME=finasis-478502:europe-west1:finasis-db`
- `DJANGO_DB_PASSWORD=***` (GitHub Secrets'ten geliyor)

---

## 🧪 Bağlantı Testi

### 1. Cloud Run Loglarından Test

```bash
# Son logları kontrol et
gcloud run services logs read finasis-prod \
  --region=europe-west1 \
  --project=finasis-478502 \
  --limit=50 | grep -E "(database|postgresql|connection|OperationalError)"
```

**Başarılı bağlantı belirtileri:**
- ✅ "Database health check: ok"
- ✅ "Migration completed"
- ❌ "OperationalError" yok
- ❌ "connection refused" yok

### 2. Health Endpoint'ten Test

```bash
curl https://finasis-prod-s3kju7bqua-ew.a.run.app/health/
```

**Beklenen JSON:**
```json
{
  "status": "healthy",
  "checks": {
    "database": {
      "status": "ok",
      "response_time_ms": 5
    }
  }
}
```

### 3. Cloud SQL Proxy ile Yerel Test (Opsiyonel)

```bash
# Cloud SQL Proxy'yi indir ve çalıştır
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy

# Proxy'yi başlat (ayrı terminal)
./cloud_sql_proxy -instances=finasis-478502:europe-west1:finasis-db=tcp:5432

# Başka bir terminal'de test et
psql -h 127.0.0.1 -U finasis-app -d finasis
```

---

## 🚨 Yaygın Sorunlar ve Çözümleri

### Sorun 1: "connection refused" veya "connection timeout"

**Çözüm:**
```bash
# Service account'a Cloud SQL Client rolü verildiğinden emin ol
gcloud projects get-iam-policy finasis-478502 \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:github-actions-deploy@finasis-478502.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
```

### Sorun 2: "password authentication failed"

**Çözüm:**
```bash
# User şifresini sıfırla
gcloud sql users set-password finasis-app \
  --instance=finasis-db \
  --password="YENI_SIFRE" \
  --project=finasis-478502

# GitHub Secrets'i güncelle: DJANGO_DB_PASSWORD
```

### Sorun 3: "database does not exist"

**Çözüm:**
```bash
# Database'i oluştur
gcloud sql databases create finasis \
  --instance=finasis-db \
  --project=finasis-478502
```

### Sorun 4: "permission denied" (Cloud SQL bağlantısı)

**Çözüm:**
```bash
# Service account'a Cloud SQL Client rolü ver
gcloud projects add-iam-policy-binding finasis-478502 \
  --member="serviceAccount:github-actions-deploy@finasis-478502.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

---

## 📝 Hızlı Kontrol Scripti

Tüm bağlantı ayarlarını tek seferde kontrol edin:

```bash
#!/bin/bash
PROJECT_ID="finasis-478502"
INSTANCE_NAME="finasis-db"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
SERVICE_ACCOUNT="github-actions-deploy@finasis-478502.iam.gserviceaccount.com"

echo "🔍 Cloud SQL Instance Kontrolü..."
gcloud sql instances describe $INSTANCE_NAME --project=$PROJECT_ID --format="value(state)"

echo ""
echo "🔍 Database Kontrolü..."
gcloud sql databases list --instance=$INSTANCE_NAME --project=$PROJECT_ID | grep finasis

echo ""
echo "🔍 User Kontrolü..."
gcloud sql users list --instance=$INSTANCE_NAME --project=$PROJECT_ID | grep finasis-app

echo ""
echo "🔍 Service Account İzinleri..."
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT" \
  --format="table(bindings.role)" | grep cloudsql

echo ""
echo "🔍 Cloud Run Environment Variables..."
gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(spec.template.spec.containers[0].env)" | grep -E "(DJANGO_DB|CLOUD_SQL)"

echo ""
echo "🔍 Cloud SQL Instance Bağlantısı..."
gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(spec.template.spec.containers[0].cloudSqlInstances)"
```

---

## 🎯 Sonraki Adımlar

1. ✅ Database ve user oluşturuldu mu?
2. ✅ Service account'a `roles/cloudsql.client` rolü verildi mi?
3. ✅ Cloud Run servisine Cloud SQL instance eklendi mi?
4. ✅ Environment variables doğru set edildi mi?
5. ✅ GitHub Secrets'te `DJANGO_DB_PASSWORD` var mı?
6. ✅ Health endpoint database bağlantısını doğruluyor mu?

Tüm adımlar tamamlandıktan sonra deployment'ı tekrar çalıştırın!

