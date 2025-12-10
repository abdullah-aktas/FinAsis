#!/bin/bash
# set -e kaldırıldı - hatalar olsa bile gunicorn başlamalı
set -uo pipefail

# PORT kontrolü (Cloud Run otomatik set eder)
if [ -z "${PORT:-}" ]; then
  export PORT=8080
  echo "⚠️  PORT not set, using default: 8080"
else
  echo "✅ PORT is set to: $PORT"
fi

# Collect static files (her zaman çalıştır - eksik statikler olmasın)
echo "📦 Collecting static files..."
if python manage.py collectstatic --noinput 2>&1; then
  echo "✅ collectstatic completed"
else
  echo "⚠️  collectstatic failed, but continuing..."
fi

# Database migrations (idempotent - safe to run multiple times)
if [ "${RUN_DB_MIGRATIONS:-true}" = "true" ]; then
  echo "🔄 Running database migrations..."
  echo "📋 Checking migration status..."
  python manage.py showmigrations --list 2>&1 | head -20 || true
  echo ""
  echo "🔄 Applying migrations..."
  if python manage.py migrate --noinput 2>&1; then
    echo "✅ Migrations completed"
    echo "📋 Final migration status:"
    python manage.py showmigrations --list 2>&1 | grep -E "\[ \]|\[X\]" | head -10 || true
  else
    echo "⚠️  Migration failed, but continuing..."
    echo "📋 Error details:"
    python manage.py migrate --noinput 2>&1 | tail -20 || true
  fi
  
  # Initialize Trade Sim seed data (idempotent - uses get_or_create)
  echo "🎮 Initializing Trade Sim data..."
  if python manage.py init_trade_sim 2>&1; then
    echo "✅ init_trade_sim completed"
  else
    echo "⚠️  init_trade_sim failed, but continuing..."
  fi
fi

# Gunicorn'u başlat (exec ile değiştir - process'i replace et)
echo "🚀 Starting Gunicorn..."
exec "$@"

