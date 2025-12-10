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

# Database bağlantısını test et (retry ile)
log ""
log "🔍 Testing database connection (with retries)..."
DB_CONNECTED=false
MAX_RETRIES=10
RETRY_DELAY=3

for i in $(seq 1 $MAX_RETRIES); do
  log "  Attempt $i/$MAX_RETRIES..."
  if python -c "
import os
import sys
import time
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        print('✅ Database connection successful:', result)
        sys.exit(0)
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
" 2>&1; then
    log "✅ Database connection test passed"
    DB_CONNECTED=true
    break
  else
    if [ $i -lt $MAX_RETRIES ]; then
      log "  ⏳ Waiting ${RETRY_DELAY}s before retry..."
      sleep $RETRY_DELAY
    fi
  fi
done

if [ "$DB_CONNECTED" = "false" ]; then
  log "❌ Database connection failed after $MAX_RETRIES attempts!"
  log "📋 Checking Cloud SQL socket..."
  if [ -n "${CLOUD_SQL_CONNECTION_NAME:-}" ]; then
    SOCKET_PATH="/cloudsql/${CLOUD_SQL_CONNECTION_NAME}"
    log "  Socket path: $SOCKET_PATH"
    if [ -S "$SOCKET_PATH" ]; then
      log "  ✅ Socket exists"
    else
      log "  ❌ Socket does not exist (Cloud SQL Proxy may not be ready)"
    fi
  fi
  exit 1
fi

# Collect static files (kritik değil - başarısız olursa uyarı ver ama devam et)
# Verbosity 1 kullanarak daha hızlı (daha az log)
log ""
log "📦 Collecting static files (verbosity reduced for speed)..."
if python manage.py collectstatic --noinput --verbosity 1 --clear 2>&1 | head -50; then
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
  log "⏱️  Migration timeout: 240 seconds (4 minutes)"
  log "💡 Using --fake-initial for faster startup (skips already applied migrations)"
  
  # Migration'ları timeout ile çalıştır (4 dakika timeout)
  # --fake-initial kullanarak zaten uygulanmış migration'ları atla (daha hızlı)
  # Bazı migration'lar atomic=False olduğu için InFailedSqlTransaction hatası olabilir
  MIGRATION_EXIT_CODE=0
  if command -v timeout >/dev/null 2>&1; then
    MIGRATION_OUTPUT=$(timeout 240 python manage.py migrate --noinput --fake-initial --verbosity 1 2>&1)
    MIGRATION_EXIT_CODE=$?
    if [ $MIGRATION_EXIT_CODE -eq 124 ]; then
      log "❌ Migration timeout after 240 seconds!"
      log "📋 Migration output (last 100 lines):"
      echo "$MIGRATION_OUTPUT" | tail -100
      exit 1
    fi
  else
    # timeout komutu yoksa direkt çalıştır
    MIGRATION_OUTPUT=$(python manage.py migrate --noinput --fake-initial --verbosity 1 2>&1)
    MIGRATION_EXIT_CODE=$?
  fi
  
  if [ $MIGRATION_EXIT_CODE -eq 0 ]; then
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
      log "🔄 Retrying migrations with fake-initial to skip problematic migrations..."
      # Önce fake-initial ile deneyelim (zaten uygulanmış migration'ları atla)
      if python manage.py migrate --noinput --verbosity 2 --fake-initial 2>&1 | tee /tmp/migration_retry.log; then
        log "✅ Migration retry with --fake-initial successful"
      else
        log "⚠️  --fake-initial failed, trying normal migrate..."
        if python manage.py migrate --noinput --verbosity 2 2>&1 | tee /tmp/migration_retry.log; then
        log "✅ Migration retry successful"
        # Tekrar kontrol et
        log "🔄 Verifying tables after retry..."
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
          log "📋 Migration retry log:"
          cat /tmp/migration_retry.log || true
          exit 1
        fi
      else
        log "❌ Migration retry failed!"
        log "📋 Migration retry log:"
        cat /tmp/migration_retry.log || true
        exit 1
      fi
    fi
  else
    log "❌ Migration failed with exit code: $MIGRATION_EXIT_CODE"
    log "📋 Migration output (last 100 lines):"
    echo "$MIGRATION_OUTPUT" | tail -100
    log "🔄 Retrying migrations (with timeout)..."
    if command -v timeout >/dev/null 2>&1; then
      if timeout 180 python manage.py migrate --noinput --verbosity 2 2>&1 | tee /tmp/migration_retry.log; then
        log "✅ Migration retry successful"
        # Tablo kontrolü yap
        log "🔄 Verifying tables after retry..."
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
          log "📋 Migration retry log:"
          cat /tmp/migration_retry.log || true
          exit 1
        fi
      else
        RETRY_EXIT_CODE=$?
        if [ $RETRY_EXIT_CODE -eq 124 ]; then
          log "❌ Migration retry timeout after 180 seconds!"
        else
          log "❌ Migration retry failed with exit code: $RETRY_EXIT_CODE"
        fi
        log "📋 Migration retry log:"
        cat /tmp/migration_retry.log || true
        exit 1
      fi
    else
      # timeout komutu yoksa direkt çalıştır
      if python manage.py migrate --noinput --verbosity 2 2>&1 | tee /tmp/migration_retry.log; then
        log "✅ Migration retry successful"
        # Tablo kontrolü yap
        log "🔄 Verifying tables after retry..."
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
          log "📋 Migration retry log:"
          cat /tmp/migration_retry.log || true
          exit 1
        fi
      else
        log "❌ Migration retry failed!"
        log "📋 Migration retry log:"
        cat /tmp/migration_retry.log || true
        exit 1
      fi
    fi
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
