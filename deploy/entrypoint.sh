#!/bin/bash
# set -e kaldırıldı - hatalar olsa bile gunicorn başlamalı
set -uo pipefail

# Tüm çıktıları stderr'e yönlendir (Cloud Run stderr'i loglar)
exec 1>&2

echo "==========================================" >&2
echo "🚀 Entrypoint.sh başlatılıyor..." >&2
echo "==========================================" >&2

# PORT kontrolü (Cloud Run otomatik set eder)
if [ -z "${PORT:-}" ]; then
  export PORT=8080
  echo "⚠️  PORT not set, using default: 8080" >&2
else
  echo "✅ PORT is set to: $PORT" >&2
fi

# Collect static files (her zaman çalıştır - eksik statikler olmasın)
echo "📦 Collecting static files..." >&2
if python manage.py collectstatic --noinput >&2; then
  echo "✅ collectstatic completed" >&2
else
  echo "⚠️  collectstatic failed, but continuing..." >&2
fi

# Database migrations (idempotent - safe to run multiple times)
if [ "${RUN_DB_MIGRATIONS:-true}" = "true" ]; then
  echo "🔄 Running database migrations..." >&2
  echo "📋 Checking migration status..." >&2
  python manage.py showmigrations --list >&2 || true
  echo "" >&2
  echo "🔄 Applying migrations..." >&2
  MIGRATE_OUTPUT=$(python manage.py migrate --noinput 2>&1)
  MIGRATE_EXIT=$?
  echo "$MIGRATE_OUTPUT" >&2
  if [ $MIGRATE_EXIT -eq 0 ]; then
    echo "✅ Migrations completed successfully" >&2
    echo "📋 Final migration status:" >&2
    python manage.py showmigrations --list 2>&1 | grep -E "\[ \]|\[X\]" | head -20 >&2 || true
  else
    echo "❌ Migration failed with exit code: $MIGRATE_EXIT" >&2
    echo "⚠️  Continuing anyway, but application may not work correctly..." >&2
  fi
  
  # Initialize Trade Sim seed data (idempotent - uses get_or_create)
  echo "🎮 Initializing Trade Sim data..." >&2
  if python manage.py init_trade_sim >&2; then
    echo "✅ init_trade_sim completed" >&2
  else
    echo "⚠️  init_trade_sim failed, but continuing..." >&2
  fi
else
  echo "⏭️  Skipping migrations (RUN_DB_MIGRATIONS=false)" >&2
fi

# Gunicorn'u başlat (exec ile değiştir - process'i replace et)
echo "🚀 Starting Gunicorn..." >&2
echo "==========================================" >&2
exec "$@"

