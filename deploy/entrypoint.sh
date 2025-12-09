#!/bin/bash
set -euo pipefail

# PORT kontrolü (Cloud Run otomatik set eder)
if [ -z "${PORT:-}" ]; then
  export PORT=8080
  echo "⚠️  PORT not set, using default: 8080"
else
  echo "✅ PORT is set to: $PORT"
fi

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

