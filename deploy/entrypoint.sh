#!/bin/bash
# Migration'lar zorunlu - başarısız olursa uygulama başlamasın
set -euo pipefail

# Python'un stdout/stderr buffer'ını kapat (anında log görünsün)
export PYTHONUNBUFFERED=1

# Tüm çıktıları stderr'e yaz (Cloud Run stderr'i loglar)
# stdout'u da stderr'e yönlendir
exec 1>&2

# Log fonksiyonu - her mesajı hem stdout hem stderr'e yazar
log() {
  echo "$@" >&2
}

log "=========================================="
log "🚀 Entrypoint.sh başlatılıyor..."
log "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
log "Working directory: $(pwd)"
log "User: $(whoami)"
log "Python: $(which python)"
log "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-not set}"
log "=========================================="

# PORT kontrolü (Cloud Run otomatik set eder)
if [ -z "${PORT:-}" ]; then
  export PORT=8080
  log "⚠️  PORT not set, using default: 8080"
else
  log "✅ PORT is set to: $PORT"
fi

# Database bağlantısını test et
log ""
log "🔍 Testing database connection..."
if python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    print('✅ Database connection successful:', result)
"; then
  log "✅ Database connection test passed"
else
  log "❌ Database connection failed!"
  exit 1
fi

# Collect static files (kritik değil - başarısız olursa uyarı ver ama devam et)
log ""
log "📦 Collecting static files..."
if python manage.py collectstatic --noinput --verbosity 2; then
  log "✅ collectstatic completed successfully"
else
  log "⚠️  collectstatic failed, but continuing (not critical - Whitenoise will serve files)..."
  # Statik dosyalar kritik değil - Whitenoise zaten çalışıyor ve eksik dosyalar için fallback var
fi

# Database migrations (ZORUNLU - başarısız olursa uygulama başlamasın)
if [ "${RUN_DB_MIGRATIONS:-true}" = "true" ]; then
  log ""
  log "🔄 Running database migrations..."
  log "📋 Checking migration status..."
  python manage.py showmigrations --list || true
  log ""
  log "🔄 Applying migrations..."
  
  # Migration'ları çalıştır - başarısız olursa exit
  if python manage.py migrate --noinput --verbosity 2; then
    log "✅ Migrations completed successfully"
    log ""
    log "📋 Final migration status:"
    python manage.py showmigrations --list | grep -E "\[ \]|\[X\]" | head -30 || true
    
    # Migration'ların gerçekten uygulandığını kontrol et
    log ""
    log "🔍 Verifying critical tables exist..."
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
      log "✅ Table verification passed"
    else
      log "❌ Critical tables are missing! Migration may have failed."
      log "🔄 Retrying migrations..."
      if python manage.py migrate --noinput --verbosity 2; then
        log "✅ Migration retry successful"
        # Tekrar kontrol et
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
        if not exists:
            missing_tables.append(table)

if missing_tables:
    print(f'❌ Still missing tables: {missing_tables}')
    sys.exit(1)
else:
    print('✅ All critical tables now exist')
"; then
          log "✅ Table verification passed after retry"
        else
          log "❌ Tables still missing after retry!"
          exit 1
        fi
      else
        log "❌ Migration retry failed!"
        exit 1
      fi
    fi
  else
    log "❌ Migration failed!"
    exit 1
  fi
  
  # Initialize Trade Sim seed data (idempotent - uses get_or_create)
  log ""
  log "🎮 Initializing Trade Sim data..."
  if python manage.py init_trade_sim; then
    log "✅ init_trade_sim completed"
  else
    log "⚠️  init_trade_sim failed, but continuing (not critical)..."
  fi
else
  log "⏭️  Skipping migrations (RUN_DB_MIGRATIONS=false)"
fi

# Gunicorn'u başlat (exec ile değiştir - process'i replace et)
log ""
log "=========================================="
log "🚀 Starting Gunicorn..."
log "Command: $@"
log "=========================================="
exec "$@"
