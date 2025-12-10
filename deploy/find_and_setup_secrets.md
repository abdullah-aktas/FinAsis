# 🔐 DJANGO_SECRET_KEY ve DJANGO_DB_PASSWORD Bulma ve Ayarlama Rehberi

## 📍 Bu Değerleri Nerede Bulabilirsiniz?

### 1️⃣ **Local .env Dosyası** (Eğer varsa)
Yerel bilgisayarınızda `.env` dosyası varsa orada olabilir:

```bash
# Windows'ta
type .env | findstr "DJANGO_SECRET_KEY"
type .env | findstr "DJANGO_DB_PASSWORD"

# Linux/Mac'te
grep "DJANGO_SECRET_KEY" .env
grep "DJANGO_DB_PASSWORD" .env
```

### 2️⃣ **Cloud Run Environment Variables** (Mevcut deployment'ta)
Cloud Run'da zaten set edilmiş olabilir:

```bash
# Cloud Shell'de çalıştırın
gcloud run services describe finasis-prod \
  --region=europe-west1 \
  --project=finasis-478502 \
  --format="value(spec.template.spec.containers[0].env)" | grep -E "(DJANGO_SECRET_KEY|DJANGO_DB_PASSWORD)"
```

### 3️⃣ **Cloud SQL Database Password**
PostgreSQL şifresini Cloud SQL'den alabilirsiniz (eğer hatırlamıyorsanız reset edebilirsiniz):

```bash
# Cloud Shell'de
gcloud sql users list --instance=finasis-db --project=finasis-478502
```

## 🆕 Eğer Değerler Yoksa - Yeni Oluşturma

### DJANGO_SECRET_KEY Oluşturma

**Python ile (Önerilen):**
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

**Veya online:**
- https://djecrety.ir/ adresine gidin
- "Generate" butonuna tıklayın
- Oluşturulan key'i kopyalayın

**Veya terminal'de:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### DJANGO_DB_PASSWORD Oluşturma

PostgreSQL için güçlü bir şifre oluşturun:
- En az 16 karakter
- Büyük/küçük harf, sayı ve özel karakter içermeli

**Online password generator:**
- https://www.lastpass.com/features/password-generator
- 20-30 karakter uzunluğunda oluşturun

## 📝 GitHub Secrets'a Ekleme Adımları

### Adım 1: GitHub Repository'ye Gidin
1. https://github.com/abdullah-aktas/FinAsis adresine gidin
2. **Settings** sekmesine tıklayın
3. Sol menüden **Secrets and variables** → **Actions** seçin

### Adım 2: Yeni Secret Ekleme

**DJANGO_SECRET_KEY eklemek için:**
1. **New repository secret** butonuna tıklayın
2. **Name:** `DJANGO_SECRET_KEY` yazın
3. **Secret:** Oluşturduğunuz secret key'i yapıştırın (uzun, rastgele string)
4. **Add secret** butonuna tıklayın

**DJANGO_DB_PASSWORD eklemek için:**
1. Tekrar **New repository secret** butonuna tıklayın
2. **Name:** `DJANGO_DB_PASSWORD` yazın
3. **Secret:** PostgreSQL şifrenizi yapıştırın
4. **Add secret** butonuna tıklayın

## ✅ Kontrol Etme

GitHub Secrets'ı ekledikten sonra, yeni bir deployment yapın. Workflow loglarında şunu görmelisiniz:

```
✅ Secrets are set (length check: SECRET_KEY=XX chars, DB_PASSWORD=XX chars)
```

## 🔄 Eğer Şifreyi Unuttuysanız

### PostgreSQL Şifresini Reset Etme

```bash
# Cloud Shell'de
gcloud sql users set-password finasis-app \
  --instance=finasis-db \
  --password=YENI_SIFRE_BURAYA \
  --project=finasis-478502
```

**ÖNEMLİ:** Şifreyi değiştirdikten sonra:
1. GitHub Secrets'taki `DJANGO_DB_PASSWORD` değerini güncelleyin
2. Yeni deployment yapın

## 🛠️ Hızlı Kontrol Script'i

Cloud Shell'de çalıştırabileceğiniz script:

```bash
# Mevcut Cloud Run environment variables'ı kontrol et
echo "🔍 Cloud Run Environment Variables:"
gcloud run services describe finasis-prod \
  --region=europe-west1 \
  --project=finasis-478502 \
  --format="yaml(spec.template.spec.containers[0].env)" | grep -E "(DJANGO_SECRET_KEY|DJANGO_DB_PASSWORD)" || echo "Bulunamadı"

# Secret Manager'da kontrol et
echo ""
echo "🔍 Secret Manager Secrets:"
gcloud secrets list --project=finasis-478502 --filter="name:DJANGO" || echo "Secret Manager'da bulunamadı"
```

