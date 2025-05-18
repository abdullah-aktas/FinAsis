#!/bin/bash

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

# Uygulamayı başlat
python manage.py runserver 0.0.0.0:8000 