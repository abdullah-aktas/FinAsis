#!/bin/bash
# Migration'lar zorunlu - başarısız olursa uygulama başlamasın
set -euo pipefail

# Python'un stdout/stderr buffer'ını kapat (anında log görünsün)
export PYTHONUNBUFFERED=1

# Tüm çıktıları stderr'e yönlendir (Cloud Run stderr'i loglar)
# stdout da stderr'e yönlendirilir
exec 1>&2

echo "=========================================="
echo "🚀 Entrypoint.sh başlatılıyor..."
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=========================================="

# PORT kontrolü (Cloud Run otomatik set eder)
if [ -z "${PORT:-}" ]; then
  export PORT=8080
  echo "⚠️  PORT not set, using default: 8080"
else
  echo "✅ PORT is set to: $PORT"
fi

# Database bağlantısını test et
echo "🔍 Testing database connection..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    print(f'✅ Database connection successful: {result}')
" || {
  echo "❌ Database connection failed!"
  exit 1
}

# Collect static files (her zaman çalıştır - eksik statikler olmasın)
echo ""
echo "📦 Collecting static files..."
if python manage.py collectstatic --noinput --verbosity 2; then
  echo "✅ collectstatic completed successfully"
else
  echo "❌ collectstatic failed!"
  exit 1
fi

# Database migrations (ZORUNLU - başarısız olursa uygulama başlamasın)
if [ "${RUN_DB_MIGRATIONS:-true}" = "true" ]; then
  echo ""
  echo "🔄 Running database migrations..."
  echo "📋 Checking migration status..."
  python manage.py showmigrations --list || true
  echo ""
  echo "🔄 Applying migrations..."
  
  # Migration'ları çalıştır - başarısız olursa exit
  if python manage.py migrate --noinput --verbosity 2; then
    echo "✅ Migrations completed successfully"
    echo ""
    echo "📋 Final migration status:"
    python manage.py showmigrations --list | grep -E "\[ \]|\[X\]" | head -30 || true
    
    # Migration'ların gerçekten uygulandığını kontrol et
    echo ""
    echo "🔍 Verifying critical tables exist..."
    if python -c "
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection

critical_tables = ['billing_module', 'common_errorlog', 'django_migrations']
missing_tables = []

for table in critical_tables:
    with connection.cursor() as cursor:
        cursor.execute(\"\"\"
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        \"\"\", [table])
        exists = cursor.fetchone()[0]
        if exists:
            print(f'✅ Table {table} exists')
        else:
            print(f'❌ Table {table} does NOT exist')
            missing_tables.append(table)

if missing_tables:
    print(f'\\n❌ Missing critical tables: {missing_tables}')
    sys.exit(1)
else:
    print('\\n✅ All critical tables exist')
"; then
      echo "✅ Table verification passed"
    else
      echo "❌ Critical tables are missing! Migration may have failed."
      echo "🔄 Retrying migrations..."
      if python manage.py migrate --noinput --verbosity 2; then
        echo "✅ Migration retry successful"
      else
        echo "❌ Migration retry failed!"
        exit 1
      fi
    fi
  else
    echo "❌ Migration failed!"
    exit 1
  fi
  
  # Initialize Trade Sim seed data (idempotent - uses get_or_create)
  echo ""
  echo "🎮 Initializing Trade Sim data..."
  if python manage.py init_trade_sim; then
    echo "✅ init_trade_sim completed"
  else
    echo "⚠️  init_trade_sim failed, but continuing (not critical)..."
  fi
else
  echo "⏭️  Skipping migrations (RUN_DB_MIGRATIONS=false)"
fi

# Gunicorn'u başlat (exec ile değiştir - process'i replace et)
echo ""
echo "=========================================="
echo "🚀 Starting Gunicorn..."
echo "Command: $@"
echo "=========================================="
exec "$@"

