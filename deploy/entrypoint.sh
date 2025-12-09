#!/bin/bash
set -euo pipefail

# Collect static files (her zaman çalıştır - eksik statikler olmasın)
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput || {
  echo "⚠️  collectstatic failed, but continuing..."
}

# Database migrations (idempotent - safe to run multiple times)
if [ "${RUN_DB_MIGRATIONS:-true}" = "true" ]; then
  echo "🔄 Running database migrations..."
  python manage.py migrate --noinput || {
    echo "⚠️  Migration failed, but continuing..."
  }
  
  # Initialize Trade Sim seed data (idempotent - uses get_or_create)
  echo "🎮 Initializing Trade Sim data..."
  python manage.py init_trade_sim || {
    echo "⚠️  init_trade_sim failed, but continuing..."
  }
fi

# Gunicorn'u başlat
exec "$@"

