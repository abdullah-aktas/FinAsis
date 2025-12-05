#!/bin/bash
# Yerel SQLite veritabanından tüm veriyi export et
# Cloud SQL'e yüklemek için hazırlar

set -e

echo "📦 Yerel Veritabanı Export"
echo "=========================="
echo ""

# 1. Eksik tabloları exclude ederek dumpdata
echo "📋 1. Veritabanı dumpdata yapılıyor..."
python manage.py dumpdata \
  --exclude=contenttypes \
  --exclude=auth.permission \
  --exclude=games.ticaretin_izinde \
  --natural-primary \
  --natural-foreign \
  --indent=2 \
  --output=full_data.json

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

