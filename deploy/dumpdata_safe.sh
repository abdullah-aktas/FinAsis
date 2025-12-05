#!/bin/bash
# Güvenli dumpdata komutu - eksik tabloları exclude eder

echo "📦 Veritabanı Dumpdata (Güvenli)"
echo "================================"
echo ""

# Eksik tabloları exclude et
python manage.py dumpdata \
  --exclude=contenttypes \
  --exclude=auth.permission \
  --exclude=games.ticaretin_izinde \
  --indent=2 \
  --output=full_data.json

echo ""
echo "✅ Dumpdata tamamlandı: full_data.json"

