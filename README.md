# FinAsis - Finansal Yönetim ve Eğitim Platformu

FinAsis, finansal yönetim ve eğitim platformudur. Kullanıcılara finansal verilerini analiz etme, yapay zeka destekli öneriler alma ve finansal eğitim alma imkanı sunar.

## Özellikler

- 📊 Finansal veri analizi ve raporlama
- 🤖 Yapay zeka destekli finansal öneriler
- 📚 İnteraktif finansal eğitim içerikleri
- 💼 Sanal şirket simülasyonları
- 🔗 Blockchain entegrasyonu
- 📱 Responsive tasarım

## Teknolojiler

- Python 3.11
- Django 5.0
- PostgreSQL
- Redis
- Docker
- Nginx
- React Native (Mobil uygulama)

## Kurulum

### Gereksinimler

- Python 3.11+
- PostgreSQL
- Redis
- Docker ve Docker Compose (opsiyonel)

### Yerel Geliştirme Ortamı

1. Repoyu klonlayın:
```bash
git clone https://github.com/yourusername/finasis.git
cd finasis
```

2. Sanal ortam oluşturun ve aktifleştirin:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. .env dosyasını oluşturun:
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

5. Veritabanını oluşturun:
```bash
python manage.py migrate
```

6. Geliştirme sunucusunu başlatın:
```bash
python manage.py runserver
```

### Docker ile Kurulum

1. Docker imajını oluşturun ve konteynerleri başlatın:
```bash
docker-compose up --build
```

2. Veritabanı migrasyonlarını çalıştırın:
```bash
docker-compose exec web python manage.py migrate
```

## Test

Testleri çalıştırmak için:
```bash
pytest
```

Test coverage raporu için:
```bash
pytest --cov=. --cov-report=html
```

## API Dokümantasyonu

API dokümantasyonuna erişmek için:
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje BSD lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## İletişim

- Website: https://www.finasis.com
- Email: contact@finasis.com
- Twitter: [@finasis](https://twitter.com/finasis)
- LinkedIn: [FinAsis](https://linkedin.com/company/finasis) 