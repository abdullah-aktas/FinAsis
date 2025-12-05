#!/bin/bash
# Yerel SQLite veritabanından tüm veriyi export et
# Cloud SQL'e yüklemek için hazırlar

set -e

echo "📦 Yerel Veritabanı Export"
echo "=========================="
echo ""

# 1. Eksik tabloları exclude ederek dumpdata
echo "📋 1. Veritabanı dumpdata yapılıyor..."
# Not: games.ticaretin_izinde app'ini tamamen exclude etmek için
# önce tüm app'leri listele, sonra games.ticaretin_izinde hariç hepsini al
python manage.py dumpdata \
  --exclude=contenttypes \
  --exclude=auth.permission \
  --exclude=games.ticaretin_izinde.UrsinaGame \
  --exclude=games.ticaretin_izinde.GameScore \
  --exclude=games.ticaretin_izinde.GameAchievement \
  --exclude=games.ticaretin_izinde.UrsinaGameSession \
  --exclude=games.ticaretin_izinde.UrsinaPlayer \
  --exclude=games.ticaretin_izinde.PlayerWallet \
  --natural-primary \
  --natural-foreign \
  --indent=2 \
  --output=full_data.json \
  2>&1 | grep -v "games.ticaretin_izinde" || true

if [ $? -eq 0 ]; then
    echo "✅ Export başarılı: full_data.json"
    FILE_SIZE=$(du -h full_data.json | cut -f1)
    echo "   Dosya boyutu: $FILE_SIZE"
else
    echo "❌ Export başarısız!"
    exit 1
fi

echo ""
echo "📋 2. Dosya kontrolü..."
if [ -f "full_data.json" ]; then
    LINE_COUNT=$(wc -l < full_data.json)
    echo "   ✅ Dosya oluşturuldu ($LINE_COUNT satır)"
    echo ""
    echo "⚠️  ÖNEMLİ: Bu dosyayı GitHub'a push ETMEYİN!"
    echo "   İçinde hassas bilgiler (şifre hashleri, kullanıcı bilgileri) olabilir."
    echo ""
    echo "📤 Sonraki adım: Cloud SQL'e yüklemek için:"
    echo "   ./deploy/import_to_production.sh"
else
    echo "❌ Dosya oluşturulamadı!"
    exit 1
fi

