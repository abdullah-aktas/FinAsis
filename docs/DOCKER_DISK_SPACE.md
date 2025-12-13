# Docker Disk Alanı Sorunları ve Çözümleri

Bu dokümantasyon, Docker build sırasında karşılaşılan "No space left on device" hatalarının çözümlerini içerir.

## Sorun

Büyük Python paketleri (torch, transformers, mediapipe vb.) Docker build sırasında çok fazla disk alanı kullanabilir ve disk alanı tükenebilir.

## Çözümler

### 1. Docker Disk Temizliği

Build öncesi Docker disk temizliği yapın:

**Linux/Mac:**
```bash
bash scripts/cleanup-docker.sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File scripts/cleanup-docker.ps1
```

**Build cache'i de temizlemek için:**
```bash
CLEAN_BUILD_CACHE=1 bash scripts/cleanup-docker.sh
```

### 2. Manuel Docker Temizliği

Aşağıdaki komutları kullanarak manuel olarak temizlik yapabilirsiniz:

```bash
# Tüm kullanılmayan kaynakları temizle
docker system prune -a --volumes

# Sadece build cache'i temizle
docker builder prune -a -f

# Disk kullanımını kontrol et
docker system df
```

### 3. Dockerfile Optimizasyonları

Dockerfile'da şu optimizasyonlar yapıldı:

- **Builder stage**: Wheel oluştururken geçici dosyalar anında temizleniyor
- **Runtime stage**: Paket kurulumu sonrası gereksiz dosyalar (tests, __pycache__ vb.) temizleniyor
- **Multi-stage build**: Builder stage'deki build araçları runtime image'ında yok

### 4. Disk Alanı Kontrolü

Build öncesi disk alanını kontrol edin:

**Linux/Mac:**
```bash
df -h
```

**Windows:**
```powershell
Get-PSDrive C | Select-Object Used,Free
```

### 5. Build Sırasında Disk İzleme

Build sırasında disk kullanımını izlemek için ayrı bir terminal'de:

**Linux:**
```bash
watch -n 1 'df -h /var/lib/docker'
```

**Mac:**
```bash
watch -n 1 'df -h ~/Library/Containers/com.docker.docker'
```

## Öneriler

1. **Düzenli temizlik**: Her build öncesi temizlik scriptini çalıştırın
2. **Disk izleme**: Build sırasında disk kullanımını izleyin
3. **Gereksiz paketleri kaldırın**: requirements.txt'den kullanılmayan paketleri kaldırın
4. **Alternatif paketler**: Daha küçük alternatif paketler kullanmayı değerlendirin

## Troubleshooting

### "No space left on device" hatası devam ediyor

1. Disk temizliği scriptini çalıştırın
2. Build cache'i temizleyin: `docker builder prune -a -f`
3. Eski image'ları temizleyin: `docker image prune -a -f`
4. Docker Desktop ayarlarından disk alanı limitini artırın

### Build çok yavaş

Build cache temizleme build süresini artırabilir. Gerekirse cache'i koruyun:
```bash
bash scripts/cleanup-docker.sh  # CLEAN_BUILD_CACHE=1 kullanmayın
```

## İlgili Dosyalar

- `Dockerfile` - Optimize edilmiş multi-stage build
- `scripts/cleanup-docker.sh` - Linux/Mac temizlik scripti
- `scripts/cleanup-docker.ps1` - Windows PowerShell temizlik scripti

