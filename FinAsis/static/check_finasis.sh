#!/bin/bash

echo "=== FinAsis Pre-Deployment Sağlık Kontrolü Başlatılıyor ==="

# Adım 1: Django ayar dosyası kontrolü
echo "➤ Django yapı kontrolü (python manage.py check)..."
python manage.py check || exit 1

# Adım 2: Yapılmamış migration var mı?
echo "➤ Migration kontrolü (makemigrations --check)..."
python manage.py makemigrations --check || exit 1

# Adım 3: Migration planı
echo "➤ Migration planı görüntüleniyor..."
python manage.py migrate --plan || exit 1

# Adım 4: Veritabanı bağlantı kontrolü
echo "➤ Veritabanı bağlantısı kontrol ediliyor (dbshell)..."
echo "\\q" | python manage.py dbshell > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Veritabanına bağlanılamadı. Lütfen ayarları kontrol edin."
    exit 1
else
    echo "✅ Veritabanına bağlantı başarılı."
fi

# Adım 5: Statik dosya testi
echo "➤ Statik dosya testi (collectstatic)..."
python manage.py collectstatic --dry-run --noinput || exit 1

# Adım 6: Otomatik testler
echo "➤ Unit testler çalıştırılıyor..."
python manage.py test || exit 1

echo "🎉 TÜM KONTROLLER BAŞARIYLA TAMAMLANDI. Canlıya geçmeye hazırsınız."
