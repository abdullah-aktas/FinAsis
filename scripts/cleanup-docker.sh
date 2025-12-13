#!/bin/bash
# Docker disk temizliği scripti
# Bu script Docker build öncesi disk alanını temizlemek için kullanılır

set -e

echo "🧹 Docker disk temizliği başlatılıyor..."

# Kullanılmayan container'ları temizle
echo "📦 Kullanılmayan container'lar temizleniyor..."
docker container prune -f 2>/dev/null || echo "⚠️  Container temizliği atlandı"

# Kullanılmayan image'ları temizle
echo "🖼️  Kullanılmayan image'lar temizleniyor..."
docker image prune -a -f 2>/dev/null || echo "⚠️  Image temizliği atlandı"

# Kullanılmayan volume'leri temizle
echo "💾 Kullanılmayan volume'ler temizleniyor..."
docker volume prune -f 2>/dev/null || echo "⚠️  Volume temizliği atlandı"

# Kullanılmayan network'leri temizle
echo "🌐 Kullanılmayan network'ler temizleniyor..."
docker network prune -f 2>/dev/null || echo "⚠️  Network temizliği atlandı"

# Build cache'i temizle (dikkatli kullanın - build süresini artırabilir)
if [ "${CLEAN_BUILD_CACHE:-0}" = "1" ]; then
    echo "🗑️  Build cache temizleniyor..."
    docker builder prune -a -f 2>/dev/null || echo "⚠️  Build cache temizliği atlandı"
else
    echo "ℹ️  Build cache korunuyor (CLEAN_BUILD_CACHE=1 ile temizlenebilir)"
fi

# Disk kullanımını göster
echo ""
echo "📊 Docker disk kullanımı:"
docker system df 2>/dev/null || echo "⚠️  Disk kullanımı bilgisi alınamadı"

echo ""
echo "✅ Temizlik tamamlandı!"

