# Veritabanı Şifre Doğrulama Hatası - Çözüm Rehberi

## Sorun

Loglarda şu hata görülüyor:
```
password authentication failed for user "finasis-app"
```

Bu hata, Cloud Run servisinin Cloud SQL veritabanına bağlanamadığı anlamına gelir.

## Neden Olur?

1. **GitHub Secret'taki şifre yanlış**: `DJANGO_DB_PASSWORD` secret'ı güncel değil
2. **Cloud SQL'deki şifre değiştirilmiş**: Veritabanı şifresi güncellenmiş ama GitHub Secret güncellenmemiş
3. **Kullanıcı mevcut değil**: `finasis-app` kullanıcısı Cloud SQL'de oluşturulmamış

## Çözüm Adımları

### 1. Cloud SQL Kullanıcısını Kontrol Et

Cloud Shell'de veya gcloud CLI ile:

```bash
gcloud sql users list \
  --instance=finasis-db \
  --project=finasis-478502
```

### 2. Şifreyi Sıfırla veya Kullanıcı Oluştur

#### Kullanıcı Yoksa - Yeni Kullanıcı Oluştur:

```bash
gcloud sql users create finasis-app \
  --instance=finasis-db \
  --password="GÜVENLİ_ŞİFRE_BURAYA" \
  --project=finasis-478502
```

#### Kullanıcı Varsa - Şifreyi Sıfırla:

```bash
gcloud sql users set-password finasis-app \
  --instance=finasis-db \
  --password="YENİ_GÜVENLİ_ŞİFRE_BURAYA" \
  --project=finasis-478502
```

**Önemli**: Güvenli bir şifre kullanın (en az 16 karakter, büyük/küçük harf, rakam, özel karakter)

### 3. GitHub Secret'ı Güncelle

1. GitHub repository'nize gidin: https://github.com/abdullah-aktas/FinAsis
2. **Settings** → **Secrets and variables** → **Actions** bölümüne gidin
3. `DJANGO_DB_PASSWORD` secret'ını bulun (yoksa **New repository secret** ile oluşturun)
4. Yeni şifreyi girin ve **Update secret** butonuna tıklayın

### 4. Deployment'ı Yeniden Yap

GitHub Actions ile otomatik deployment:

1. GitHub Actions sayfasına gidin: https://github.com/abdullah-aktas/FinAsis/actions
2. **Deploy to Cloud Run** workflow'unu bulun
3. **Run workflow** butonuna tıklayın
4. Deployment'ın tamamlanmasını bekleyin

Veya Cloud Shell'de manuel deployment:

```bash
cd ~/FinAsis
bash scripts/deploy-production-cloud-shell.sh
```

### 5. Logları Kontrol Et

Deployment sonrası logları kontrol edin:

```bash
gcloud logging read \
  "resource.type=cloud_run_revision AND \
   resource.labels.service_name=finasis-prod AND \
   textPayload=~'password authentication'" \
  --project=finasis-478502 \
  --limit=10
```

Eğer hata devam ediyorsa, tüm hataları görmek için:

```bash
gcloud logging read \
  "resource.type=cloud_run_revision AND \
   resource.labels.service_name=finasis-prod AND \
   severity>=ERROR" \
  --project=finasis-478502 \
  --limit=50
```

## Otomatik Teşhis Scripti

Cloud Shell'de çalıştırabileceğiniz bir teşhis scripti:

```bash
cd ~/FinAsis
bash scripts/fix-database-password.sh
```

Bu script:
- Cloud SQL instance'ı kontrol eder
- Kullanıcının varlığını kontrol eder
- Şifre sıfırlama seçenekleri sunar
- GitHub Secret güncelleme talimatları verir

## Doğrulama

Deployment sonrası, uygulamanın çalıştığını kontrol edin:

```bash
# Service URL'ini al
SERVICE_URL=$(gcloud run services describe finasis-prod \
  --region=europe-west1 \
  --project=finasis-478502 \
  --format="value(status.url)")

# Health check yap
curl "$SERVICE_URL/health/"
```

Başarılı bir yanıt alırsanız, veritabanı bağlantısı çalışıyor demektir.

## Önleme

Gelecekte bu sorunu önlemek için:

1. **Secret Manager Kullanın**: Environment variable yerine Secret Manager kullanın (daha güvenli)
2. **Şifre Değişikliklerini Dokümante Edin**: Şifre değiştiğinde GitHub Secret'ı da güncelleyin
3. **Düzenli Kontrol**: Aylık olarak veritabanı bağlantılarını test edin

## İlgili Dosyalar

- `.github/workflows/deploy.yml` - GitHub Actions deployment workflow
- `scripts/deploy-production-cloud-shell.sh` - Manuel deployment script
- `scripts/fix-database-password.sh` - Otomatik teşhis ve düzeltme scripti
- `config/settings/base.py` - Database configuration

## Destek

Sorun devam ederse:
1. Cloud SQL instance'ın çalıştığından emin olun
2. Cloud Run servisinin Cloud SQL'e erişim izni olduğunu kontrol edin
3. Service account'un `roles/cloudsql.client` rolüne sahip olduğunu doğrulayın

