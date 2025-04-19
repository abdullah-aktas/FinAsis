#!/bin/sh

# Veritabanı bağlantısını bekle
echo "Veritabanı bağlantısı bekleniyor..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Veritabanı bağlantısı hazır!"

# Migrasyonları uygula
python manage.py migrate

# Statik dosyaları topla
python manage.py collectstatic --noinput

# Gunicorn ile uygulamayı başlat
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 