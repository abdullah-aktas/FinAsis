# Docker disk temizliği scripti (PowerShell)
# Bu script Docker build öncesi disk alanını temizlemek için kullanılır

Write-Host "🧹 Docker disk temizliği başlatılıyor..." -ForegroundColor Cyan

# Kullanılmayan container'ları temizle
Write-Host "📦 Kullanılmayan container'lar temizleniyor..." -ForegroundColor Yellow
try {
    docker container prune -f 2>$null
} catch {
    Write-Host "⚠️  Container temizliği atlandı" -ForegroundColor Yellow
}

# Kullanılmayan image'ları temizle
Write-Host "🖼️  Kullanılmayan image'lar temizleniyor..." -ForegroundColor Yellow
try {
    docker image prune -a -f 2>$null
} catch {
    Write-Host "⚠️  Image temizliği atlandı" -ForegroundColor Yellow
}

# Kullanılmayan volume'leri temizle
Write-Host "💾 Kullanılmayan volume'ler temizleniyor..." -ForegroundColor Yellow
try {
    docker volume prune -f 2>$null
} catch {
    Write-Host "⚠️  Volume temizliği atlandı" -ForegroundColor Yellow
}

# Kullanılmayan network'leri temizle
Write-Host "🌐 Kullanılmayan network'ler temizleniyor..." -ForegroundColor Yellow
try {
    docker network prune -f 2>$null
} catch {
    Write-Host "⚠️  Network temizliği atlandı" -ForegroundColor Yellow
}

# Build cache'i temizle (isteğe bağlı)
if ($env:CLEAN_BUILD_CACHE -eq "1") {
    Write-Host "🗑️  Build cache temizleniyor..." -ForegroundColor Yellow
    try {
        docker builder prune -a -f 2>$null
    } catch {
        Write-Host "⚠️  Build cache temizliği atlandı" -ForegroundColor Yellow
    }
} else {
    Write-Host "ℹ️  Build cache korunuyor (CLEAN_BUILD_CACHE=1 ile temizlenebilir)" -ForegroundColor Gray
}

# Disk kullanımını göster
Write-Host ""
Write-Host "📊 Docker disk kullanımı:" -ForegroundColor Cyan
try {
    docker system df
} catch {
    Write-Host "⚠️  Disk kullanımı bilgisi alınamadı" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Temizlik tamamlandı!" -ForegroundColor Green

