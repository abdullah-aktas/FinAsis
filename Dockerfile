# Multi-stage build için temel imaj
FROM python:3.11-slim as base

# Ortak ortam değişkenleri
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=config.settings

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    postgresql-client \
    build-essential \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Python bağımlılıkları için ayrı katman
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodu için ayrı katman
COPY . .

# Statik dosyaları ve çevirileri derle
RUN python manage.py collectstatic --noinput \
    && python manage.py compilemessages

# Gereksiz dosyaları temizle
RUN find . -type d -name __pycache__ -exec rm -rf {} + \
    && rm -rf .git .github tests

# Gerekli klasörleri oluştur
RUN mkdir -p /app/media /app/staticfiles /var/log/finasis \
    && chmod +x entrypoint.sh

# Non-root kullanıcı oluştur
RUN addgroup --system app \
    && adduser --system --group app \
    && chown -R app:app /app /var/log/finasis

# Kullanıcı değiştir
USER app

# Sağlık kontrolü
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8000/health/ || exit 1

# Entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Varsayılan komut
CMD ["gunicorn", "config.wsgi:application", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "3", \
    "--threads", "2", \
    "--timeout", "120", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "--log-level", "info", \
    "--worker-class", "gthread", \
    "--worker-tmp-dir", "/dev/shm"]

# Port aç
EXPOSE 8000

# Development aşaması
FROM base as development
ENV DJANGO_DEBUG=True \
    DJANGO_SECRET_KEY=development-secret-key \
    DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Production aşaması
FROM base as production
ENV DJANGO_DEBUG=False \
    DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY} \
    DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS}

# Frontend build aşaması
FROM node:18-alpine as frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Nginx aşaması
FROM nginx:1.23-alpine as nginx
COPY --from=frontend-builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"] 