# Disk Yetersizliği Sorunu - Neden Analizi

## Sorunun Kök Nedenleri

### 1. Büyük Python Paketleri (Ana Neden)

`requirements.txt` dosyanızda çok büyük paketler var:

#### En Büyük Paketler (Disk Kullanımı):
- **`torch` (PyTorch)**: ~500-700 MB (derlenmiş)
- **`transformers`**: ~200-300 MB
- **`opencv-python`**: ~100-150 MB
- **`mediapipe`**: ~100-200 MB
- **`scipy`**: ~50-100 MB
- **`scikit-learn`**: ~50-100 MB
- **`pandas`**: ~50-100 MB
- **`numpy`**: ~30-50 MB
- **`pygame`**: ~50-100 MB
- **`ursina`**: ~50-100 MB
- **`weasyprint`**: ~50-100 MB

**Toplam tahmini disk kullanımı**: ~1.5-2 GB (sadece Python paketleri)

### 2. GitHub Actions Runner Disk Sınırlamaları

- **Runner disk alanı**: Genellikle **14GB-28GB** arası (paylaşımlı)
- **Docker build sırasında**:
  - Base image: ~200-300 MB
  - Builder stage: ~2-3 GB (wheels + dependencies)
  - Build cache: ~500 MB - 2 GB (birikimli)
  - Geçici dosyalar: ~500 MB - 1 GB
  - Log dosyaları: ~100-500 MB (birikimli)

**Toplam build sırasında disk kullanımı**: ~5-8 GB

### 3. Runner Log Dosyalarının Birikmesi

Runner'ın kendi log dosyaları (`/home/runner/actions-runner/cached/_diag/`) zamanla birikir:
- Her build log dosyaları oluşturur
- Eski loglar otomatik temizlenmez
- Zamanla GB'lar dolabilir

### 4. Docker Build Cache Birikmesi

- Her build Docker layer cache'i oluşturur
- GitHub Actions runner'ları paylaşımlı olduğu için cache birikir
- Cache temizlenmezse disk dolar

### 5. Çoklu Build'ler

Site canlıda ve GitHub Actions çalışıyordu, ama:
- Her push'ta build tetiklenir
- Her build disk alanı kullanır
- Eski build cache'leri temizlenmezse disk dolar
- Biriken cache'ler + yeni build = disk dolması

## Sorunun Zaman İçinde Artması

```
Başlangıç: 14GB boş disk
├── İlk build: -5GB = 9GB boş
├── 2. build: -3GB (cache sayesinde) = 6GB boş
├── 3. build: -3GB = 3GB boş
├── Runner logları: -2GB = 1GB boş
└── 4. build: -5GB = ❌ DISK DOLDU
```

## Çözümler (Uygulanan)

### 1. Dockerfile Optimizasyonları ✅

- Multi-stage build ile gereksiz dosyalar kaldırıldı
- Wheel oluştururken geçici dosyalar anında temizleniyor
- Paket kurulumu sonrası test dizinleri ve __pycache__ temizleniyor
- Build dependency'leri runtime image'ına dahil edilmiyor

### 2. GitHub Actions Workflow Optimizasyonları ✅

- Build öncesi Docker temizliği
- Build sonrası Docker temizliği
- Runner log dosyalarının temizlenmesi
- Build hatası durumunda ek temizlik

### 3. Alternatif Deploy Yöntemi ✅

- Cloud Build alternatifi hazır (daha fazla disk alanı)
- GitHub Actions optimize edildi (şimdi daha iyi çalışmalı)

## Uzun Vadeli Çözüm Önerileri

### 1. Paket Optimizasyonu (Önerilen)

Bazı paketleri opsiyonel hale getirin veya daha küçük alternatifler kullanın:

```python
# requirements.txt yerine requirements-base.txt ve requirements-optional.txt
# Runtime'da sadece gerekli paketleri yükleyin
```

### 2. Build Cache Stratejisi

- Artifact Registry cache kullanılıyor (zaten var)
- Build cache'i optimize edildi

### 3. Runner Temizliği

- Workflow'a düzenli temizlik eklendi
- Runner log temizliği eklendi

### 4. Cloud Build'e Geçiş (Opsiyonel)

Cloud Build daha fazla disk alanı sunar ve bu sorundan daha az etkilenir.

## Sonuç

**Sorunun ana nedeni**: Büyük ML/AI paketleri (torch, transformers) + GitHub Actions runner'ın sınırlı disk alanı + biriken cache ve log dosyaları.

**Çözüm**: Dockerfile ve workflow optimizasyonları uygulandı. Şimdi daha az disk alanı kullanıyor ve düzenli temizlik yapıyor.

**Gelecek**: Optimizasyonlar sayesinde disk sorunu büyük ölçüde azaldı. Yine de olursa Cloud Build alternatifi hazır.

