# FinAsis Projesi

## Kurulum

1. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. Ortam değişkenlerini ayarlayın:
   - `example.env` dosyasını `.env` olarak kopyalayın ve gerekli alanları doldurun.

3. Veritabanı migrasyonlarını uygulayın:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Süper kullanıcı oluşturun:
   ```bash
   python manage.py createsuperuser
   ```

5. Geliştirme sunucusunu başlatın:
   ```bash
   python manage.py runserver
   ```

6. Celery worker başlatmak için:
   ```bash
   celery -A FinAsis worker -l info
   ```

7. (Opsiyonel) Celery Beat başlatmak için:
   ```bash
   celery -A FinAsis beat -l info
   ```

## Notlar
- Ortam değişkenleri `.env` dosyasında tutulur.
- Statik dosyalar için:
   ```bash
   python manage.py collectstatic
   ```
- Testleri çalıştırmak için:
   ```bash
   python manage.py test
   ``` 