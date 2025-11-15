#!/bin/bash
set -euo pipefail

if [ "${RUN_DB_MIGRATIONS:-true}" = "true" ]; then
  python manage.py migrate --noinput
fi

exec "$@"

