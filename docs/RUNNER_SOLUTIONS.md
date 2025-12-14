# GitHub Actions Runner Disk Sorunu - Çözüm Seçenekleri

## 🎯 Sorun

GitHub Actions standart runner'ları **14-28 GB** disk alanına sahip ve büyük Python paketleri (torch, transformers) build sırasında disk alanını tüketiyor.

## ✅ Çözüm Seçenekleri

### 1. Cloud Build Kullanmak (ÖNERİLEN - HAZIR) ⭐

**Avantajlar:**

- ✅ Daha fazla disk alanı (sınırsız değil ama çok daha fazla)
- ✅ Daha hızlı build (Google Cloud altyapısı)
- ✅ Daha güvenilir
- ✅ Setup script'i hazır

**Kullanım:**

```bash
# Cloud Shell'de:
cd ~/FinAsis && git pull origin main
bash scripts/setup-cloud-build.sh
gcloud builds submit --config=deploy/cloud_run/cloudbuild.yaml --project=finasis-478502 --region=europe-west1 .
```

**Durum:** ✅ Hazır ve çalışır durumda

---

### 2. Self-Hosted Runner Kurmak

**Avantajlar:**

- ✅ Tam disk kontrolü (istediğiniz kadar disk alanı)
- ✅ Daha hızlı (kendi sunucunuzda)
- ✅ Ücretsiz (sadece sunucu maliyeti)

**Dezavantajlar:**

- ❌ Kurulum ve bakım gerektirir
- ❌ Sunucu maliyeti
- ❌ Güvenlik yönetimi

**Kurulum Adımları:**

1. **Sunucu hazırlayın** (Google Cloud Compute Engine, AWS EC2, vb.)

   - Minimum: 4 CPU, 8 GB RAM, 50 GB disk
   - Önerilen: 8 CPU, 16 GB RAM, 100 GB disk

2. **Runner'ı kurun:**

```bash
# Sunucuda:
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Token alın: GitHub → Settings → Actions → Runners → "New runner" → "Linux"
./config.sh --url https://github.com/abdullah-aktas/FinAsis --token YOUR_TOKEN

# Runner'ı servis olarak başlatın
sudo ./svc.sh install
sudo ./svc.sh start
```

3. **Workflow'u güncelleyin:**

```yaml
jobs:
  deploy:
    runs-on: self-hosted # GitHub-hosted yerine
```

---

### 3. Daha Büyük GitHub-Hosted Runner'lar (Team/Enterprise Gerektirir)

**Özellikler:**

- 64 çekirdek
- 256 GB RAM
- **2040 GB SSD depolama** ⭐
- Windows, Linux ve Mac

**Gereksinimler:**

- ❌ GitHub Team veya Enterprise planı gerekli
- ❌ Ücretli (aylık maliyet)

**Kullanım:**

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest-4-cores # veya daha büyük
```

**Durum:** Şu anda "Sağlanmamış" - Team/Enterprise planı gerekli

---

### 4. Workflow Optimizasyonları (UYGULANDI) ✅

**Yapılanlar:**

- ✅ İlk adım olarak runner log temizliği
- ✅ Build öncesi Docker temizliği
- ✅ Build sonrası Docker temizliği
- ✅ Runner cache temizliği

**Durum:** ✅ Uygulandı, ama yeterli olmayabilir

---

### 5. Paket Optimizasyonu (UZUN VADELİ)

**Strateji:**

- Büyük paketleri (torch, transformers) opsiyonel hale getirin
- Runtime'da sadece gerekli paketleri yükleyin
- Multi-stage Dockerfile ile gereksiz dosyaları kaldırın

**Örnek:**

```python
# requirements-base.txt (temel paketler)
Django>=5.2,<6.0
# ... diğer temel paketler

# requirements-ai.txt (opsiyonel AI paketleri)
torch>=2.0.0
transformers>=4.40.0
```

---

## 🎯 Önerilen Çözüm Sırası

### Hemen (Şimdi):

1. **Cloud Build kullanın** - Hazır ve çalışır durumda ⭐
2. Workflow optimizasyonları zaten uygulandı

### Kısa Vadede (1-2 hafta):

1. Self-hosted runner kurmayı değerlendirin (sunucu varsa)
2. Paket optimizasyonu yapın (opsiyonel paketleri ayırın)

### Uzun Vadede:

1. GitHub Team/Enterprise planına geçin (büyük runner'lar için)
2. Paket mimarisini optimize edin

---

## 📊 Karşılaştırma

| Çözüm             | Disk Alanı | Kurulum | Maliyet                | Önerilen   |
| ----------------- | ---------- | ------- | ---------------------- | ---------- |
| **Cloud Build**   | Yüksek     | Kolay   | Ücretsiz (kota içinde) | ⭐⭐⭐⭐⭐ |
| **Self-Hosted**   | Sınırsız   | Orta    | Sunucu maliyeti        | ⭐⭐⭐⭐   |
| **Büyük Runner**  | 2040 GB    | Kolay   | Aylık ücret            | ⭐⭐⭐     |
| **Workflow Opt.** | Sınırlı    | Kolay   | Ücretsiz               | ⭐⭐       |

---

## 🚀 Hızlı Başlangıç: Cloud Build

```bash
# Cloud Shell'de:
cd ~/FinAsis && git pull origin main
bash scripts/setup-cloud-build.sh
gcloud builds submit --config=deploy/cloud_run/cloudbuild.yaml --project=finasis-478502 --region=europe-west1 .
```

**Bu çözüm şu anda en pratik ve hazır olanıdır!**
