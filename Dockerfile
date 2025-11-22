# syntax=docker/dockerfile:1

FROM python:3.11-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir /wheels --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PORT=8080 \
    PYTHONPATH=/app \
    MPLCONFIGDIR=/tmp/matplotlib-cache

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgomp1 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY . .
# Matplotlib cache dizinini oluştur
RUN mkdir -p /tmp/matplotlib-cache && chmod 777 /tmp/matplotlib-cache
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate
RUN python manage.py init_trade_sim

COPY deploy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER app
EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
# Production için gunicorn config dosyası kullan (50K users için optimize edilmiş)
CMD ["gunicorn", "config.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "-c", "gunicorn_config.py"]

