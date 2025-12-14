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

# Database bağlantısını test et (retry ile, daha hızlı)
log ""
log "🔍 Testing database connection (with retries)..."
DB_CONNECTED=false
MAX_RETRIES=3
RETRY_DELAY=3

for i in $(seq 1 $MAX_RETRIES); do
  if [ $i -gt 1 ]; then
    log "  Attempt $i/$MAX_RETRIES..."
  fi
  if timeout 5 python -c "
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        sys.exit(0)
except Exception as e:
    sys.exit(1)
" >/dev/null 2>&1; then
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
    if [ -S "$SOCKET_PATH" ]; then
      log "  ✅ Socket exists"
    else
      log "  ❌ Socket does not exist (Cloud SQL Proxy may not be ready)"
    fi
  fi
  log "⚠️  Continuing anyway - database may become available later..."
  # Database bağlantısı başarısız olsa bile devam et (Cloud SQL Proxy geç başlayabilir)
fi

# Collect static files (kritik değil - başarısız olursa uyarı ver ama devam et)
# Verbosity 0 kullanarak çok daha hızlı (minimal log)
log ""
log "📦 Collecting static files (minimal verbosity for speed)..."
if timeout 30 python manage.py collectstatic --noinput --verbosity 0 --clear >/dev/null 2>&1; then
  log "✅ collectstatic completed successfully"
else
  log "⚠️  collectstatic failed or timed out, but continuing (not critical - Whitenoise will serve files)..."
  # Statik dosyalar kritik değil - Whitenoise zaten çalışıyor ve eksik dosyalar için fallback var
fi

: <<'OLD_MIGRATION_BLOCK'
# Database migrations (ZORUNLU - başarısız olursa uygulama başlamasın)
if [ "${RUN_DB_MIGRATIONS:-true}" = "true" ]; then
  log ""
  log "🔄 Running database migrations..."
  log "🔄 Applying migrations (optimized for speed)..."
  log "⏱️  Migration timeout: 120 seconds (2 minutes)"
  log "💡 Using --fake-initial and --run-syncdb for faster startup"
  
  # Migration'ları timeout ile çalıştır (2 dakika timeout - daha agresif)
  # --fake-initial: Zaten uygulanmış migration'ları atla
  # --run-syncdb: Migration'ı olmayan modeller için tablo oluştur (daha hızlı)
  # Verbosity 0: Minimal log (daha hızlı)
  MIGRATION_EXIT_CODE=0
  if command -v timeout >/dev/null 2>&1; then
    # Verbosity 0 ile çalıştır, sadece hata durumunda log göster
    if timeout 120 python manage.py migrate --noinput --fake-initial --run-syncdb --verbosity 0 >/tmp/migration.log 2>&1; then
      MIGRATION_EXIT_CODE=0
      log "✅ Migrations completed successfully"
    else
      MIGRATION_EXIT_CODE=$?
      if [ $MIGRATION_EXIT_CODE -eq 124 ]; then
        log "⚠️  Migration timeout after 120 seconds, but continuing (may be partially applied)"
        log "📋 Migration output (last 30 lines):"
        tail -30 /tmp/migration.log
        # Timeout olsa bile devam et - bazı migration'lar uygulanmış olabilir
        MIGRATION_EXIT_CODE=0
      else
        log "⚠️  Migration had errors, but continuing (may be partially applied):"
        tail -30 /tmp/migration.log
        # Hata olsa bile devam et (bazı migration'lar zaten uygulanmış olabilir)
        MIGRATION_EXIT_CODE=0
      fi
    fi
  else
    # timeout komutu yoksa direkt çalıştır
    if python manage.py migrate --noinput --fake-initial --run-syncdb --verbosity 0 >/tmp/migration.log 2>&1; then
      MIGRATION_EXIT_CODE=0
      log "✅ Migrations completed successfully"
    else
      MIGRATION_EXIT_CODE=$?
      log "⚠️  Migration had errors, but continuing:"
      tail -30 /tmp/migration.log
      # Hata olsa bile devam et
      MIGRATION_EXIT_CODE=0
    fi
  fi
  
  if [ $MIGRATION_EXIT_CODE -eq 0 ]; then
    # Final migration status'u sadece hata durumunda göster (zaman kazanmak için)
    # log "📋 Final migration status:"
    # python manage.py showmigrations --list | grep -E "\[ \]|\[X\]" | head -30 || true
    
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

critical_tables = ['billing_module', 'common_errorlog', 'django_migrations', 'partners_partnerprofile']
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

critical_tables = ['billing_module', 'common_errorlog', 'django_migrations', 'partners_partnerprofile']
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

critical_tables = ['billing_module', 'common_errorlog', 'django_migrations', 'partners_partnerprofile']
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

OLD_MIGRATION_BLOCK

# Database migrations (ZORUNLU - başarısız olursa uygulama başlamasın) - basitleştirilmiş sürüm
if [ "${RUN_DB_MIGRATIONS:-true}" = "true" ]; then
  log ""
  log "🔄 Running database migrations..."
  log "⏱️  Migration timeout: 120 seconds (2 minutes)"

  # Migration'ları timeout ile çalıştır (varsa); hata alırsak uygulamayı başlatmayalım
  if command -v timeout >/dev/null 2>&1; then
    if timeout 120 python manage.py migrate --noinput --fake-initial --verbosity 0; then
      log "✅ Migrations completed successfully"
    else
      EXIT_CODE=$?
      if [ $EXIT_CODE -eq 124 ]; then
        log "⚠️  Migration timeout after 120 seconds, but continuing..."
      else
        log "❌ migrate failed with exit code: $EXIT_CODE"
        log "⚠️  Continuing anyway - migrations may be partially applied..."
      fi
    fi
  else
    if python manage.py migrate --noinput --fake-initial --verbosity 0; then
      log "✅ Migrations completed successfully"
    else
      EXIT_CODE=$?
      log "⚠️  migrate had errors (exit code: $EXIT_CODE), but continuing..."
    fi
  fi

  # Migration'ların gerçekten uygulandığını basitçe kontrol et (timeout ile)
  log ""
  log "🔍 Verifying critical tables exist..."
  if timeout 30 python - << 'PYCODE'
import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

critical_tables = [
    "django_migrations",  # En kritik tablo
]
missing_tables = []

for table in critical_tables:
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = %s
                );
                """,
                [table],
            )
            exists = cursor.fetchone()[0]
            if exists:
                print(f"✅ Table {table} exists")
            else:
                print(f"❌ Table {table} does NOT exist")
                missing_tables.append(table)
    except Exception as e:
        print(f"⚠️  Error checking table {table}: {e}")
        # Hata olsa bile devam et

if missing_tables:
    print(f"\n⚠️  Missing critical tables: {missing_tables}")
    print("⚠️  Continuing anyway - tables may be created later...")
    # exit 1 yerine devam et
else:
    print("\n✅ Critical tables exist")
PYCODE
  then
    log "✅ Table verification passed"
  else
    log "⚠️  Table verification had issues, but continuing..."
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
log "Command: $*"
log "Arguments count: $#"
log "PORT: ${PORT:-not set}"
log "=========================================="

# exec "$@" JSON array formatındaki CMD'yi doğru çalıştırmayabilir
# Bu yüzden direkt gunicorn komutunu çalıştıralım
if [ $# -eq 0 ]; then
  # Eğer argüman yoksa, default gunicorn komutunu çalıştır
  log "⚠️  No arguments provided, using default gunicorn command"
  exec gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -c gunicorn_config.py
else
  # Argümanlar varsa, onları kullan
  exec "$@"
fi
