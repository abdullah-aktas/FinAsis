# Health Check Endpoint'lerini Hızlıca Deploy Etme

Health check endpoint'leri production'da görünmüyor. Hızlıca deploy etmek için:

## Cloud Shell'de Adımlar

```bash
cd ~/FinAsis

# 1. Son değişiklikleri al
git pull origin main

# 2. Dosyaların geldiğini kontrol et
ls -la common/views_health.py
ls -la common/urls_health.py

# 3. Cloud Build ile deploy et
gcloud builds submit --config cloudbuild.yaml

# VEYA manuel olarak test et (lokal)
python3 manage.py check
python3 manage.py runserver 0.0.0.0:8080
# Başka bir terminal'de:
curl http://localhost:8080/health/
```

## Hızlı Test (Deploy Öncesi)

```bash
# Cloud Shell'de Django shell ile test
python3 manage.py shell
```

```python
# Django shell'de
from django.urls import reverse
from django.test import Client

client = Client()
response = client.get('/health/')
print(response.status_code)
print(response.content)
```

## Sorun Giderme

Eğer hala 404 alıyorsanız:

1. **URL pattern kontrolü**:
   ```bash
   python3 manage.py show_urls | grep health
   ```

2. **Import hatası kontrolü**:
   ```bash
   python3 manage.py check
   ```

3. **Dosya varlığı kontrolü**:
   ```bash
   ls -la common/views_health.py
   ls -la common/urls_health.py
   cat config/urls.py | grep health
   ```

