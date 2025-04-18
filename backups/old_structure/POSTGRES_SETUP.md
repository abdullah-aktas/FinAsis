# PostgreSQL'e Geçiş Kılavuzu

Bu kılavuz, FinAsis projesinin SQLite'dan PostgreSQL'e geçiş sürecini adım adım açıklar.

## Neden PostgreSQL?

PostgreSQL, SQLite'a göre aşağıdaki avantajları sunar:

- **Eşzamanlı çoklu bağlantı desteği**: Birden fazla kullanıcı/işlem aynı anda veritabanına yazabilir
- **Daha iyi ölçeklenebilirlik**: Büyük veri kümeleri için optimize edilmiştir
- **Gelişmiş veri tipleri**: JSON, Dizi, XML, vb. özel veri tipleri
- **Tam-metin arama**: Gelişmiş metin arama özellikleri
- **Güçlü yetkilendirme sistemi**: Daha detaylı erişim kontrolü
- **Daha iyi veri bütünlüğü garantileri**: Daha sağlam ACID desteği

## Gereksinimler

- PostgreSQL 15+
- Python 3.8+
- psycopg2-binary paketi

## Kurulum Adımları

### 1. PostgreSQL Kurulumu

#### Windows

1. [PostgreSQL indirme sayfasından](https://www.postgresql.org/download/windows/) en son sürümü indirin ve kurun
2. Kurulum sırasında:
   - PostgreSQL şifresini unutmayın (varsayılan kullanıcı: postgres)
   - Port numarasını not edin (varsayılan: 5432)
   - Tüm bileşenleri seçin

#### macOS

```bash
brew install postgresql
brew services start postgresql
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### 2. Proje Yapılandırması

1. `.env` dosyanızı düzenleyin:

```
DB_NAME=finasis
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
```

2. psycopg2 paketini yükleyin:

```bash
pip install psycopg2-binary
```

### 3. Otomatik Kurulum Scriptini Çalıştırma

#### Windows

PowerShell'de:

```powershell
.\setup_postgres.ps1
```

#### Linux/macOS

```bash
chmod +x setup_postgres.sh
./setup_postgres.sh
```

### 4. Veritabanını Manuel Olarak Oluşturma

PostgreSQL'i kendiniz yapılandırmak istiyorsanız:

1. PostgreSQL komut satırına giriş:

```bash
# Linux
sudo -u postgres psql

# macOS
psql postgres

# Windows
psql -U postgres
```

2. Veritabanı ve kullanıcı oluşturma:

```sql
CREATE USER finasis WITH PASSWORD 'your_password';
CREATE DATABASE finasis OWNER finasis;
GRANT ALL PRIVILEGES ON DATABASE finasis TO finasis;
```

3. Django migrasyonlarını çalıştırma:

```bash
python manage.py migrate
```

## Docker Kullanımı

Docker Compose ile tüm sistemi (PostgreSQL dahil) başlatmak için:

```bash
docker-compose up -d
```

## Sorun Giderme

### Bağlantı Hataları

- **psycopg2 hatası**: `pip install psycopg2-binary` komutunu çalıştırın
- **"password authentication failed"**: `.env` dosyasındaki şifreyi kontrol edin
- **"could not connect to server"**: PostgreSQL servisinin çalıştığından emin olun

### Migrasyon Sorunları

Migrasyon hatalarında:

```bash
python manage.py migrate --plan  # Çalıştırılacak migrasyonları göster
python manage.py showmigrations  # Mevcut tüm migrasyonları ve durumlarını göster
```

### Veri Aktarımı

SQLite'dan PostgreSQL'e veri aktarmak için:

```bash
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data.json
python manage.py loaddata data.json
```

## Yardımcı Komutlar

- PostgreSQL durumunu kontrol etme:
  ```bash
  # Linux
  sudo systemctl status postgresql
  
  # macOS
  brew services list
  
  # Windows
  # Servisler panelinden kontrol edin
  ```

- Veritabanı boyutunu kontrol etme:
  ```sql
  SELECT pg_size_pretty(pg_database_size('finasis'));
  ``` 