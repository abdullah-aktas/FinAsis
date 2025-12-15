#!/bin/bash
# Minimal entrypoint - gunicorn'u hemen başlat
set -uo pipefail

# Python'un stdout/stderr buffer'ını kapat
export PYTHONUNBUFFERED=1

# Tüm çıktıları stderr'e yaz (Cloud Run stderr'i loglar)
exec 1>&2

log() {
  echo "$@" >&2
}

log "=========================================="
log "🚀 Starting FinAsis API..."
log "PORT: ${PORT:-8080}"
log "=========================================="

# PORT kontrolü
export PORT=${PORT:-8080}

# Migration'ları background'da başlat (non-blocking)
if [ "${RUN_DB_MIGRATIONS:-true}" = "true" ]; then
  log "🔄 Starting migrations in background..."
  (
    python manage.py migrate --noinput --fake-initial --verbosity 0 2>&1 || true
    log "✅ Migrations completed"
  ) &
fi

# Gunicorn'u hemen başlat (exec ile - process replace)
log "🚀 Starting Gunicorn on port $PORT..."

if [ $# -gt 0 ]; then
  exec "$@"
else
  exec gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -c gunicorn_config.py
fi
