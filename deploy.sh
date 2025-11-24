#!/bin/bash
# FinAsis Canlı Ortam Deploy Script
# Kullanım: ./deploy.sh veya bash deploy.sh

set -e  # Hata durumunda dur

echo "🚀 FinAsis Deploy Başlatılıyor..."

# Proje dizinine geç
cd ~/FinAsis || { echo "❌ FinAsis dizini bulunamadı!"; exit 1; }

# Git durumunu kontrol et
echo "📊 Git durumu kontrol ediliyor..."
git status --short || true

# Son değişiklikleri al
echo "⬇️  Son değişiklikler alınıyor..."
git pull origin main

# Migration kontrolü (opsiyonel - hata verirse devam et)
echo "🗄️  Migration'lar kontrol ediliyor..."
python manage.py migrate --check 2>/dev/null || python manage.py migrate || echo "⚠️  Migration hatası (devam ediliyor...)"

# Static dosyalar (opsiyonel - hata verirse devam et)
echo "📦 Static dosyalar toplanıyor..."
python manage.py collectstatic --noinput 2>/dev/null || echo "⚠️  Static dosyalar toplanamadı (normal olabilir)"

echo ""
echo "✅ Deploy tamamlandı!"
echo "📝 Son commit: $(git log -1 --oneline --no-color)"
echo ""
echo "💡 İpucu: Eğer hata alırsanız, 'python manage.py migrate' veya 'python manage.py collectstatic' komutlarını manuel çalıştırın."

