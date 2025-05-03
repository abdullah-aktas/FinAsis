# Python 3.11 temel imajını kullan
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    gnupg \
    apt-transport-https \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Non-root kullanıcı oluştur
RUN useradd -m -u 1000 finasis

# Çalışma dizinini ayarla ve izinleri düzenle
RUN chown -R finasis:finasis /app

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY --chown=finasis:finasis . .

# Geliştirme bağımlılıklarını yükle (isteğe bağlı)
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Statik dosyaları topla
RUN python manage.py collectstatic --noinput

# Güvenlik ayarları
RUN chmod -R 755 /app && \
    find /app -type f -exec chmod 644 {} \; && \
    chmod 755 /app/manage.py

# Kullanıcıyı değiştir
USER finasis

# Sağlık kontrolü
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Gunicorn yapılandırması
ENV GUNICORN_CMD_ARGS="--workers=4 --threads=2 --timeout=60 --access-logfile=- --error-logfile=- --log-level=info --capture-output --enable-stdio-inheritance"

# Uygulama portu
EXPOSE 8000

# Uygulamayı başlat
CMD ["gunicorn", "finasis.wsgi:application", "--bind", "0.0.0.0:8000"] 