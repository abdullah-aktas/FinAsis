#!/bin/bash
# Güvenli dumpdata komutu - eksik tabloları exclude eder

echo "📦 Veritabanı Dumpdata (Güvenli)"
echo "================================"
echo ""

# Eksik tabloları exclude et
# Not: games.ticaretin_izinde bir app olduğu için, modelleri tek tek exclude ediyoruz
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
    echo ""
    echo "✅ Dumpdata tamamlandı: full_data.json"
    FILE_SIZE=$(du -h full_data.json 2>/dev/null | cut -f1 || echo "N/A")
    echo "   Dosya boyutu: $FILE_SIZE"
    echo ""
    echo "⚠️  ÖNEMLİ: Bu dosyayı GitHub'a push ETMEYİN!"
    echo "   İçinde hassas bilgiler (şifre hashleri, kullanıcı bilgileri) olabilir."
else
    echo ""
    echo "❌ Dumpdata başarısız!"
    exit 1
fi

