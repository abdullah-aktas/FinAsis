# Fixture Dosyasını Canlıya Aktarma Rehberi

Bu rehber, `fixtures/users_all.json` dosyasını GitHub'a gönderme, Cloud Shell'e aktarma ve canlı ortama yansıtma adımlarını açıklar.

## 📤 1. GitHub'a Gönderme (Lokal)

### Adım 1: Değişiklikleri Commit Edin

```bash
git commit -m "feat: Add user fixture data and update cloudbuild.yaml

- Add fixtures/users_all.json with customuser, groups, and permissions
- Update cloudbuild.yaml to skip migrations in build (migrations run in Cloud Run)
- Fix dumpdata command to use accounts.customuser instead of auth.user"
```

### Adım 2: GitHub'a Push Edin

```bash
git push origin main
```

## 📥 2. Cloud Shell'e Aktarma

### Seçenek A: Git Pull (Önerilen)

Cloud Shell'de proje zaten klonlanmışsa:

```bash
cd ~/FinAsis
git pull origin main
```

### Seçenek B: Manuel Yükleme

Eğer proje klonlanmamışsa:

```bash
# 1. Projeyi klonlayın
git clone https://github.com/abdullah-aktas/FinAsis.git
cd FinAsis

# 2. Veya mevcut projeyi güncelleyin
cd ~/FinAsis
git pull origin main
```

## 🚀 3. Canlıya Yansıtma

### Yöntem 1: Cloud Run Exec ile (Önerilen)

Cloud Run container'ında direkt komut çalıştırma:

```bash
# Cloud Shell'de çalıştırın
PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"

# Cloud Run servisine bağlanın ve loaddata çalıştırın
gcloud run services execute $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --command="python" \
  --args="manage.py,loaddata,fixtures/users_all.json" \
  --args="--noinput"
```

### Yöntem 2: Cloud SQL Proxy ile (Alternatif)

Eğer Cloud Run Exec çalışmazsa, Cloud SQL Proxy kullanarak:

```bash
# Cloud Shell'de
PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"

# Cloud SQL instance adını bulun
gcloud sql instances list

# Cloud SQL Proxy'yi başlatın (arka planda)
CLOUD_SQL_INSTANCE="finasis-478502:europe-west1:YOUR_INSTANCE_NAME"
cloud_sql_proxy -instances=$CLOUD_SQL_INSTANCE=tcp:5432 &

# Environment variables'ı ayarlayın
export DJANGO_SETTINGS_MODULE=config.settings
export DJANGO_DB_ENGINE=django.db.backends.postgresql
export DJANGO_DB_NAME=finasis
export DJANGO_DB_USER=finasis-app
export DJANGO_DB_HOST=127.0.0.1
export DJANGO_DB_PORT=5432

# Secret Manager'dan şifreyi alın
export DJANGO_DB_PASSWORD=$(gcloud secrets versions access latest --secret="finasis-db-pass")
export DJANGO_SECRET_KEY=$(gcloud secrets versions access latest --secret="finasis-django-secret")

# Loaddata çalıştırın
cd ~/FinAsis
python manage.py loaddata fixtures/users_all.json
```

### Yöntem 3: Management Command ile (En Güvenli)

Özel bir management command oluşturup Cloud Run'da çalıştırma:

```bash
# Cloud Shell'de
cd ~/FinAsis

# Management command oluşturun (opsiyonel, zaten varsa atlayın)
# python manage.py load_fixture fixtures/users_all.json

# Veya direkt loaddata
python manage.py loaddata fixtures/users_all.json --verbosity=2
```

## ⚠️ Önemli Notlar

### 1. Mevcut Verileri Yedekleyin

Loaddata çalıştırmadan önce mevcut verileri yedekleyin:

```bash
# Cloud Shell'de
cd ~/FinAsis

# Mevcut kullanıcıları yedekleyin
python manage.py dumpdata accounts.customuser auth.group auth.permission \
  --indent 2 --output fixtures/users_backup_$(date +%Y%m%d_%H%M%S).json
```

### 2. Conflict Kontrolü

Fixture dosyasındaki kullanıcılar zaten varsa:

```bash
# Dry-run yapın (sadece kontrol, değişiklik yapmaz)
python manage.py loaddata fixtures/users_all.json --verbosity=2 --dry-run
```

### 3. Sadece Eksik Verileri Yükleyin

Eğer sadece yeni kullanıcıları eklemek istiyorsanız:

```bash
# Mevcut kullanıcıları atla, sadece yeni olanları ekle
python manage.py loaddata fixtures/users_all.json --verbosity=2
```

Django otomatik olarak mevcut kayıtları atlar (primary key conflict).

## 🔍 Kontrol Komutları

### Fixture Dosyasını Kontrol Edin

```bash
# JSON syntax kontrolü
python -m json.tool fixtures/users_all.json > /dev/null && echo "✅ JSON geçerli" || echo "❌ JSON geçersiz"

# Kaç kullanıcı var?
python -c "import json; data=json.load(open('fixtures/users_all.json')); print(f'Toplam kayıt: {len(data)}')"
```

### Yükleme Sonrası Kontrol

```bash
# Kullanıcı sayısını kontrol edin
python manage.py shell -c "from accounts.models import CustomUser; print(f'Toplam kullanıcı: {CustomUser.objects.count()}')"

# Grup sayısını kontrol edin
python manage.py shell -c "from django.contrib.auth.models import Group; print(f'Toplam grup: {Group.objects.count()}')"
```

## 🆘 Sorun Giderme

### Hata: "No such table: accounts_customuser"

Migration'ların uygulandığından emin olun:

```bash
python manage.py migrate
```

### Hata: "IntegrityError: duplicate key value"

Mevcut kayıtlar var. Sadece yeni kayıtları eklemek için:

```bash
# Mevcut kullanıcıları fixture'tan çıkarın veya
# --update-existing kullanın (eğer management command varsa)
```

### Hata: "Permission denied"

Cloud Run service account'una gerekli izinleri verin:

```bash
gcloud projects add-iam-policy-binding finasis-478502 \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

## 📝 Hızlı Referans

```bash
# 1. GitHub'a gönder
git add fixtures/users_all.json cloudbuild.yaml
git commit -m "feat: Add user fixture data"
git push origin main

# 2. Cloud Shell'de al
cd ~/FinAsis && git pull origin main

# 3. Yedek al
python manage.py dumpdata accounts.customuser auth.group auth.permission \
  --indent 2 --output fixtures/backup_$(date +%Y%m%d).json

# 4. Yükle
python manage.py loaddata fixtures/users_all.json --verbosity=2

# 5. Kontrol et
python manage.py shell -c "from accounts.models import CustomUser; print(CustomUser.objects.count())"
```

