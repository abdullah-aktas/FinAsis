# Kurulum ve Geliştirme Rehberi

Bu dokümantasyon, FinAsis projesinin kurulumu ve geliştirme ortamının hazırlanması için gerekli adımları içerir.

## İçindekiler

1. [Gereksinimler](#gereksinimler)
2. [Geliştirme Ortamı Kurulumu](#geliştirme-ortamı-kurulumu)
3. [Proje Yapısı](#proje-yapısı)
4. [Geliştirme İş Akışı](#geliştirme-iş-akışı)
5. [Test ve Kalite Kontrol](#test-ve-kalite-kontrol)
6. [Dağıtım](#dağıtım)
7. [Sık Karşılaşılan Sorunlar](#sık-karşılaşılan-sorunlar)

## Gereksinimler

### Sistem Gereksinimleri

- Python 3.9 veya üzeri
- pip (Python paket yöneticisi)
- PostgreSQL 13+ (önerilen) veya SQLite
- Node.js 14+ ve npm 6+
- Redis 6+ (görev kuyruğu için)
- Docker & Docker Compose (opsiyonel)
- Git

### IDE ve Araçlar

- Visual Studio Code (önerilen)
- PyCharm Professional/Community
- Git
- Postman veya Insomnia (API testi için)
- pgAdmin veya DBeaver (veritabanı yönetimi için)

## Geliştirme Ortamı Kurulumu

### 1. Projeyi Klonlama

```bash
git clone https://github.com/finasis/finasis.git
cd finasis
```

### 2. Sanal Ortam Oluşturma

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkların Yüklenmesi

```bash
# Python bağımlılıkları
pip install -r requirements.txt

# Node.js bağımlılıkları
npm install
```

### 4. Ortam Değişkenlerinin Ayarlanması

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin ve gerekli değişkenleri ayarlayın:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/finasis
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Veritabanı Kurulumu

```bash
# PostgreSQL veritabanı oluşturma
createdb finasis

# Migrasyonları uygulama
python manage.py migrate

# Örnek verileri yükleme (opsiyonel)
python manage.py loaddata fixtures/initial_data.json
```

### 6. Statik Dosyaların Toplanması

```bash
python manage.py collectstatic
```

### 7. Geliştirme Sunucusunu Başlatma

```bash
# Terminal 1: Django sunucusu
python manage.py runserver

# Terminal 2: Celery worker
celery -A finasis worker -l info

# Terminal 3: Celery beat (zamanlanmış görevler için)
celery -A finasis beat -l info
```

### 8. Docker ile Kurulum (Opsiyonel)

```bash
# Geliştirme ortamı
docker-compose up -d

# Üretim ortamı
docker-compose -f docker-compose.prod.yml up -d
```

## Proje Yapısı

```
finasis/
├── apps/                    # Uygulama modülleri
│   ├── core/               # Çekirdek modül
│   ├── finance/            # Finans modülü
│   ├── accounting/         # Muhasebe modülü
│   ├── pwa/               # Progressive Web App
│   ├── ai_assistant/      # Yapay zeka asistanı
│   ├── analytics/         # Analitik modülü
│   ├── integrations/      # Entegrasyonlar
│   └── api/               # API endpoints
├── docs/                   # Dokümantasyon
├── locale/                # Dil dosyaları
├── static/                # Statik dosyalar
├── templates/             # HTML şablonları
├── tests/                 # Test dosyaları
├── .env.example          # Örnek ortam değişkenleri
├── docker-compose.yml    # Docker yapılandırması
├── Dockerfile            # Docker imaj yapılandırması
├── manage.py             # Django yönetim betiği
└── requirements.txt      # Python bağımlılıkları
```

## Geliştirme İş Akışı

1. Yeni bir branch oluşturun:
```bash
git checkout -b feature/yeni-ozellik
```

2. Değişikliklerinizi yapın ve test edin

3. Değişikliklerinizi commit edin:
```bash
git add .
git commit -m "feat: yeni özellik eklendi"
```

4. Branch'inizi push edin:
```bash
git push origin feature/yeni-ozellik
```

5. Pull Request oluşturun

## Test ve Kalite Kontrol

### Unit Testler

```bash
# Tüm testleri çalıştırma
python manage.py test

# Belirli bir uygulamanın testlerini çalıştırma
python manage.py test apps.core
```

### Kod Kalitesi Kontrolleri

```bash
# Linting
flake8 .

# Format kontrolü
black .

# Import sıralaması
isort .
```

### Güvenlik Taraması

```bash
# Güvenlik açıklarını kontrol etme
safety check

# Bağımlılık taraması
pip-audit
```

## Dağıtım

### Geliştirme Ortamı

```bash
# Docker ile
docker-compose up -d

# Manuel
python manage.py runserver
```

### Üretim Ortamı

```bash
# Docker ile
docker-compose -f docker-compose.prod.yml up -d

# Manuel
python manage.py collectstatic
python manage.py migrate
gunicorn finasis.wsgi:application
```

## Sık Karşılaşılan Sorunlar

### 1. Veritabanı Bağlantı Hatası

**Sorun**: PostgreSQL bağlantı hatası
**Çözüm**: 
- PostgreSQL servisinin çalıştığından emin olun
- Veritabanı kullanıcı adı ve şifresini kontrol edin
- `.env` dosyasındaki `DATABASE_URL` değerini doğrulayın

### 2. Redis Bağlantı Hatası

**Sorun**: Redis bağlantı hatası
**Çözüm**:
- Redis servisinin çalıştığından emin olun
- `.env` dosyasındaki `REDIS_URL` değerini kontrol edin

### 3. Statik Dosya Hatası

**Sorun**: Statik dosyalar yüklenmiyor
**Çözüm**:
```bash
python manage.py collectstatic --noinput
```

### 4. Migrasyon Hatası

**Sorun**: Migrasyon çakışması
**Çözüm**:
```bash
python manage.py makemigrations
python manage.py migrate --fake-initial
```

### 5. Node.js Bağımlılık Hatası

**Sorun**: npm paketleri yüklenemiyor
**Çözüm**:
```bash
rm -rf node_modules
npm cache clean --force
npm install
``` 