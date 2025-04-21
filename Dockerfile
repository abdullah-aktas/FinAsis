# Python 3.11 imajını kullan
FROM python:3.11-slim

# Standart çıktı ve hata çıktısı arabelleğe alınmasını engeller
ENV PYTHONUNBUFFERED=1 \
    # pip'in önbelleğe alınması engellenir, daha küçük imaj boyutu için
    PIP_NO_CACHE_DIR=1 \
    # pip sürüm kontörllerini geçersiz kılar
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Docker içinde bytecode önbelleklemeyi engeller
    PYTHONDONTWRITEBYTECODE=1 \
    # Önbelleklenmiş .pyc dosyalarının oluşturulmasını engeller
    PYTHONOPTIMIZE=1

# Çalışma dizinini ayarla
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    postgresql-client \
    build-essential \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projeyi kopyala
COPY . .

# Statik dosyaları önceden derler
RUN python manage.py collectstatic --noinput

# Çeviri dosyalarını derle
RUN python manage.py compilemessages

# Gereksiz dosyaları temizle
RUN find . -type d -name __pycache__ -exec rm -rf {} +
RUN rm -rf .git .github tests

# Gerekli klasörleri oluştur ve izinleri düzenle
RUN mkdir -p /app/media /app/staticfiles /var/log/finasis
RUN chmod +x entrypoint.sh

# Non-root kullanıcı oluştur ve izinleri düzenle
RUN addgroup --system app && adduser --system --group app
RUN chown -R app:app /app /var/log/finasis
USER app

# Sağlık kontrolü
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8000/health/ || exit 1

# Entrypoint script'ini çalıştır
ENTRYPOINT ["./entrypoint.sh"]

# Varsayılan komut
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "--timeout", "120"]

# Uygulama portunu aç
EXPOSE 8000 