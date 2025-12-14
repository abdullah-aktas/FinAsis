# syntax=docker/dockerfile:1

FROM python:3.11-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY requirements.txt .
# Wheel oluştururken disk kullanımını minimize et
RUN pip install --upgrade pip setuptools wheel && \
    mkdir -p /tmp/wheel-tmp && \
    TMPDIR=/tmp/wheel-tmp pip wheel --wheel-dir /wheels --no-cache-dir -r requirements.txt && \
    rm -rf /tmp/wheel-tmp && \
    rm -rf /root/.cache/pip && \
    rm -rf /tmp/* /var/tmp/* && \
    apt-get purge -y build-essential gcc g++ && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/apt/archives/*

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PYTHONPATH=/app \
    MPLCONFIGDIR=/tmp/matplotlib-cache
# NOT: PORT environment variable Cloud Run tarafından otomatik set edilir
# CMD'de --bind 0.0.0.0:$PORT ile Cloud Run'ın verdiği PORT'u kullanıyoruz

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
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /var/cache/apt/archives/*

RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt /tmp/requirements.txt
# Paketleri kurarken disk alanını optimize et - pip geçici dosyalarını anında temizle
# TMPDIR'i küçük bir dizine ayarla ve paketleri kur
# Büyük paketleri adım adım kurup her adımda temizlik yap
RUN mkdir -p /tmp/pip-tmp && \
    TMPDIR=/tmp/pip-tmp pip install --no-cache-dir --no-index --find-links /wheels -r /tmp/requirements.txt && \
    rm -rf /wheels && \
    rm -rf /tmp/requirements.txt && \
    rm -rf /tmp/pip-tmp && \
    rm -rf /root/.cache/pip && \
    rm -rf /tmp/* /var/tmp/* && \
    find /usr/local/lib/python3.11/site-packages -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -name "*.pyo" -delete 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -name "*.py[co]" -delete 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -type d -name "test" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    python -c "import compileall; compileall.compile_dir('/usr/local/lib/python3.11/site-packages', quiet=1, workers=0)" 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete 2>/dev/null || true

COPY . .
# Matplotlib cache dizinini oluştur
RUN mkdir -p /tmp/matplotlib-cache && chmod 777 /tmp/matplotlib-cache
# Staticfiles dizinini oluştur
RUN mkdir -p /app/staticfiles
# Tüm /app dizinini app kullanıcısına sahiplik ver (COPY'den sonra)
RUN chown -R app:app /app
# NOT: collectstatic, migrate ve init_trade_sim runtime'da entrypoint.sh içinde çalışacak
# Bu sayede her deployment'ta güncel statikler ve migration'lar garantilenir

COPY deploy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown app:app /entrypoint.sh

USER app
EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
# Production için gunicorn config dosyası kullan (50K users için optimize edilmiş)
# PORT gunicorn_config.py içinde zaten bind ediliyor, bu yüzden --bind kullanmıyoruz
CMD ["gunicorn", "config.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "-c", "gunicorn_config.py"]

