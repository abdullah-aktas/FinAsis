# Python 3.11 slim imajını kullan
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Sistem bağımlılıklarını yükle
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential libpq-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını yükle
COPY requirements.txt .
RUN pip install --upgrade pip \
  && pip install -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Statik dosyaları topla
RUN mkdir -p /app/staticfiles /app/media
RUN python manage.py collectstatic --noinput

# Uygulama kullanıcısı oluştur ve yetkileri ayarla
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Gerekli portları aç
EXPOSE 8000

# Gunicorn ile uygulamayı başlat
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"] 