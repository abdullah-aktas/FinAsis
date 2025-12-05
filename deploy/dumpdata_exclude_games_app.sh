#!/bin/bash
# games.ticaretin_izinde app'ini tamamen exclude eden dumpdata script'i
# App adı exclude edilemediği için, tüm app'leri listele ve games.ticaretin_izinde hariç al

echo "📦 Veritabanı Dumpdata (games.ticaretin_izinde Exclude)"
echo "======================================================"
echo ""

# Tüm app'leri listele (games.ticaretin_izinde hariç)
APPS=$(python manage.py dumpdata --help 2>/dev/null | grep -oP 'apps\.\w+' | sort -u || echo "")

# Manuel olarak tüm app'leri belirt (games.ticaretin_izinde hariç)
DUMP_APPS="accounts accounting advisors ai_assistant audit billing blockchain common core_ui corporate education finance games.game_app games.trade_sim games.finquest integrator_gib integrator_mock kobi_analysis management permissions developer_portal partners security submissions tenancy virtual_company"

echo "📋 Exclude edilen app: games.ticaretin_izinde"
echo "📋 Dahil edilen app'ler: $DUMP_APPS"
echo ""

python manage.py dumpdata \
  $DUMP_APPS \
  --exclude=contenttypes \
  --exclude=auth.permission \
  --natural-primary \
  --natural-foreign \
  --indent=2 \
  --output=full_data.json

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

