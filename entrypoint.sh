#!/bin/sh
set -e

# Uygulamayı başlatmadan önce sağlık kontrolleri yapılır

# Veritabanı bağlantısını kontrol et
echo "🔍 Veritabanı bağlantısı kontrol ediliyor..."
export PGPASSWORD="${DB_PASSWORD}"
until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}"; do
  echo "⏳ PostgreSQL bağlantısı hazır değil - 2 saniye bekleniyor..."
  sleep 2
done
echo "✅ PostgreSQL bağlantısı hazır!"

# Redis bağlantısını kontrol et
echo "🔍 Redis bağlantısı kontrol ediliyor..."
until nc -z "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}"; do
  echo "⏳ Redis bağlantısı hazır değil - 2 saniye bekleniyor..."
  sleep 2
done
echo "✅ Redis bağlantısı hazır!"

# Log dizinleri oluştur
echo "📁 Log dizinleri kontrol ediliyor..."
mkdir -p /var/log/finasis
mkdir -p /app/logs
chmod -R 755 /var/log/finasis /app/logs
echo "✅ Log dizinleri hazır!"

# Disk alanını kontrol et
echo "🔍 Disk alanı kontrol ediliyor..."
FREE_SPACE=$(df -k /app | tail -1 | awk '{print $4}')
if [ "${FREE_SPACE}" -lt 104857 ]; then  # 100MB'dan az alan varsa
  echo "⚠️ UYARI: Disk alanı kritik seviyede! (Kalan: ${FREE_SPACE}KB)"
fi

# Migrasyonları uygula (--no-input ile onay beklemeden)
echo "🚀 Database migrasyonları uygulanıyor..."
python manage.py migrate --no-input

# Statik dosyaları topla
echo "📦 Statik dosyalar toplanıyor..."
python manage.py collectstatic --no-input

# Çevirileri derle
echo "🌐 Çeviri dosyaları derleniyor..."
python manage.py compilemessages

# Superuser oluşturulması (eğer yoksa)
echo "👤 Admin kullanıcısı kontrol ediliyor..."
python scripts/ensure_superuser.py

# Ortam bilgilerini göster
echo "🌍 Uygulama $(python --version) ile çalışıyor"
echo "⚙️ Django ayarları: ${DJANGO_SETTINGS_MODULE}"
echo "🔒 Debug modu: ${DJANGO_DEBUG}"

# Gunicorn ile uygulamayı başlat
echo "🚀 Uygulama başlatılıyor..."
exec "$@" 