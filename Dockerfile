# Python 3.11 imajını kullan
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Entrypoint script'ini çalıştırılabilir yap
RUN chmod +x entrypoint.sh

# Entrypoint script'ini çalıştır
ENTRYPOINT ["./entrypoint.sh"]

# Varsayılan komut
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"] 