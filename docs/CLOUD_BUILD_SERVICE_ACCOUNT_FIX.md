# Cloud Build Service Account Sorunu - Hızlı Çözüm

## Sorun

Cloud Build Permissions sayfasında dropdown'da **doğru service account görünmüyor**:
- ❌ Yanlış: `211704933618-compute@developer.gserviceaccount.com` (dropdown'da görünüyor)
- ✅ Doğru: `211704933618@cloudbuild.gserviceaccount.com` (dropdown'da görünmüyor)

## Çözüm Adımları

### Adım 1: Cloud Build API'sini Tam Olarak Etkinleştirin

Cloud Shell'de:

```bash
PROJECT_ID="finasis-478502"

# Cloud Build API'sini etkinleştir
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID

# Birkaç dakika bekleyin (API'nin tam etkinleşmesi için)
echo "⏳ Cloud Build API'sinin tam etkinleşmesi için 2-3 dakika bekleyin..."
```

### Adım 2: Cloud Build Service Account'unu Kontrol Edin

Cloud Shell'de:

```bash
PROJECT_ID="finasis-478502"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

echo "Cloud Build Service Account: $CB_SA"

# Service account'un var olup olmadığını kontrol et
gcloud iam service-accounts describe $CB_SA --project=$PROJECT_ID
```

**Eğer hata alırsanız** (service account bulunamadı):
- Cloud Build API'si henüz tam olarak etkinleşmemiş olabilir
- 5-10 dakika bekleyin ve tekrar deneyin
- Veya Cloud Build Console'dan manuel olarak bir build başlatmayı deneyin (bu service account'u otomatik oluşturur)

### Adım 3: Service Account'u Manuel Olarak Oluşturun (Gerekirse)

Eğer service account hala yoksa:

```bash
PROJECT_ID="finasis-478502"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Service account'u oluştur
gcloud iam service-accounts create cloudbuild-sa \
  --display-name="Cloud Build Service Account" \
  --project=$PROJECT_ID || echo "Service account zaten mevcut veya otomatik oluşturulacak"
```

**NOT:** Cloud Build service account genellikle Cloud Build API etkinleştirildiğinde otomatik oluşturulur. Manuel oluşturma gerekmez.

### Adım 4: Cloud Build Console'da Service Account'u Seçin

1. [Cloud Build Permissions](https://console.cloud.google.com/cloud-build/permissions?project=finasis-478502) sayfasına gidin
2. **Service account** dropdown'ını açın
3. Eğer `211704933618@cloudbuild.gserviceaccount.com` görünmüyorsa:
   - **"Filter Type to filter"** alanına `@cloudbuild.gserviceaccount.com` yazın
   - Veya dropdown'ı kapatıp tekrar açın (sayfayı yenileyin)
   - Veya service account alanına **manuel olarak** `211704933618@cloudbuild.gserviceaccount.com` yazın
4. **"OK"** butonuna tıklayın
5. **"Save"** butonuna tıklayın

### Adım 5: Alternatif - Service Account'u Manuel Olarak Girin

Eğer dropdown'da doğru service account görünmüyorsa:

1. Service account alanına **doğrudan** şunu yazın:
   ```
   211704933618@cloudbuild.gserviceaccount.com
   ```
2. **"OK"** butonuna tıklayın
3. **"Save"** butonuna tıklayın

### Adım 6: IAM Rollerini Kontrol Edin ve Atayın

Cloud Shell'de:

```bash
PROJECT_ID="finasis-478502"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Gerekli roller
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$CB_SA" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$CB_SA" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$CB_SA" \
  --role="roles/iam.serviceAccountUser"
```

### Adım 7: Test Edin

Cloud Shell'de:

```bash
cd ~/FinAsis
gcloud builds submit --config=deploy/cloud_run/cloudbuild.yaml --project=finasis-478502 --region=europe-west1 .
```

## Hızlı Çözüm Scripti

Tüm adımları otomatik olarak yapan script:

```bash
cd ~/FinAsis
git pull origin main
bash scripts/fix-cloud-build-notfound-comprehensive.sh
```

## Service Account Listede Görünmüyorsa

Eğer Service Accounts sayfasında Cloud Build service account görünmüyorsa:

1. **Cloud Build API'sini Etkinleştirin ve Bekleyin:**
   ```bash
   gcloud services enable cloudbuild.googleapis.com --project=finasis-478502
   # 5-10 dakika bekleyin
   ```

2. **Cloud Build Console'dan Manuel Build Başlatın:**
   - [Cloud Build Dashboard](https://console.cloud.google.com/cloud-build?project=finasis-478502) sayfasına gidin
   - "Create Build" veya "Trigger" butonuna tıklayın
   - Bu işlem Cloud Build service account'unu otomatik oluşturabilir

3. **Service Account Kontrol Scriptini Çalıştırın:**
   ```bash
   cd ~/FinAsis
   git pull origin main
   bash scripts/create-cloud-build-service-account.sh
   ```

4. **Manuel Olarak Yazın (ÖNERİLEN):**
   - Service account dropdown'da görünmese bile, alana manuel olarak yazabilirsiniz
   - Cloud Build Permissions sayfasında service account alanına: `211704933618@cloudbuild.gserviceaccount.com` yazın
   - "OK" ve "Save" butonlarına tıklayın

## Sorun Devam Ederse

2. **Birkaç Dakika Bekleyin:**
   - API'lerin tam etkinleşmesi için 5-10 dakika bekleyin
   - Cloud Shell'i yeniden başlatın

3. **GitHub Actions Kullanın:**
   - Cloud Build'de sorun yaşıyorsanız, GitHub Actions zaten çalışıyor
   - [GitHub Actions](https://github.com/abdullah-aktas/FinAsis/actions) sayfasından manuel olarak tetikleyin

## Önemli Notlar

- **Cloud Build service account** (`@cloudbuild.gserviceaccount.com`) Cloud Build API etkinleştirildiğinde **otomatik oluşturulur**
- Eğer dropdown'da görünmüyorsa, API henüz tam olarak etkinleşmemiş olabilir
- Service account alanına **manuel olarak** yazabilirsiniz (dropdown'dan seçmek zorunda değilsiniz)
- **Compute service account** (`-compute@developer.gserviceaccount.com`) Cloud Build için kullanılmamalıdır

