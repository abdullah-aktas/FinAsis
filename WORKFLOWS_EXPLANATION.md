# 📋 GitHub Actions Workflow'ları Açıklaması

## 🔍 Workflow'lar ve Görevleri

### 1. CI Workflow (`ci.yml`) - ❌ DEPLOY YAPMAZ

**Dosya**: `.github/workflows/ci.yml`

**Amaç**: Kod kalitesi kontrolü
- ✅ Lint kontrolü (Ruff)
- ✅ Format kontrolü (Black)
- ✅ Test çalıştırma (Pytest)
- ✅ Coverage raporlama
- ✅ Güvenlik taraması (Bandit, pip-audit)

**Ne Zaman Çalışır**:
- Her `main` veya `develop` branch'e push
- Her Pull Request'te

**Deploy Yapar mı?**: ❌ **HAYIR** - Sadece test ve kontrol yapar

---

### 2. Deploy Workflow (`deploy.yml`) - ✅ OTOMATIK DEPLOY YAPAR

**Dosya**: `.github/workflows/deploy.yml`

**Amaç**: Cloud Run'a otomatik deployment

**Ne Zaman Çalışır**:
- `main` branch'e push olduğunda (belirli dosya değişikliklerinde):
  - `**.py` dosyaları
  - `**.html`, `**.js`, `**.css` dosyaları
  - `Dockerfile`
  - `requirements.txt`
  - `deploy/**` klasörü
  - `config/**` klasörü
  - `common/**` klasörü
  - `accounts/**` klasörü
- Manuel tetikleme (`workflow_dispatch`)

**Ne Yapar**:
1. Google Cloud'a authenticate olur
2. Cloud Build'e build job'ı submit eder
3. Container image'ı build eder ve Artifact Registry'ye push eder
4. Cloud Run service'ine (`finasis-prod`) deploy eder
5. Health check yapar

**Deploy Yapar mı?**: ✅ **EVET** - Bu workflow otomatik deploy yapar!

---

## 🎯 Özet

| Workflow | Deploy Yapar mı? | Ne Zaman Çalışır |
|----------|------------------|------------------|
| **CI** (`ci.yml`) | ❌ Hayır | Her push/PR |
| **Deploy** (`deploy.yml`) | ✅ **EVET** | `main` branch'e push (belirli dosyalarda) |

## ⚠️ Önemli Notlar

1. **CI başarısız olursa**: Deploy workflow yine de çalışabilir (bağımlılık yok)
2. **Deploy'u durdurmak için**: `deploy.yml` dosyasını geçici olarak devre dışı bırakabilirsiniz
3. **Manuel deploy**: GitHub Actions sayfasından "Deploy to Cloud Run" workflow'unu manuel tetikleyebilirsiniz

