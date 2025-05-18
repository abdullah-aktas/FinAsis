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

## Demo

Canlı demo ortamı için: [https://demo.finasis.com](https://demo.finasis.com) *(Demo ortamı kurulduğunda bu linki güncelleyiniz)*

## Ekran Görüntüleri

Ana modüllerin ve dashboard'un ekran görüntülerini aşağıda bulabilirsiniz:

- ![Dashboard](docs/screenshots/dashboard.png)
- ![CRM Modülü](docs/screenshots/crm.png)
- ![Muhasebe Modülü](docs/screenshots/accounting.png)

Daha fazla ekran görüntüsü için [docs/screenshots/](docs/screenshots/) klasörüne bakınız.

## Tanıtım Videosu

Kısa tanıtım videosu için: [YouTube - FinAsis Tanıtım](https://youtu.be/finasis-demo) *(Video hazırlandığında bu linki güncelleyiniz)*

## Referanslar & Kullanıcı Hikayeleri

> "FinAsis sayesinde finansal süreçlerimizi %40 daha hızlı yönetiyoruz!"  
> <small>- Örnek Müşteri, ABC Şirketi</small>

Daha fazla başarı hikayesi ve referans için [docs/referanslar.md](docs/referanslar.md) dosyasını inceleyin. 