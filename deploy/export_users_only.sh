#!/bin/bash
# Sadece kullanıcıları export et

echo "👥 Kullanıcı Export"
echo "==================="
echo ""

python manage.py dumpdata \
  accounts.customuser \
  --natural-primary \
  --indent=2 \
  --output=users.json

if [ $? -eq 0 ]; then
    echo "✅ Kullanıcılar export edildi: users.json"
    echo ""
    echo "⚠️  ÖNEMLİ: Bu dosyayı GitHub'a push ETMEYİN!"
    echo "   İçinde şifre hashleri ve kullanıcı bilgileri var."
else
    echo "❌ Export başarısız!"
    exit 1
fi

