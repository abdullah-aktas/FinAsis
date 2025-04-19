# 2. Veritabanı ve Altyapı

## 📌 Amaç
Bu dokümantasyon, FinAsis projesinin veritabanı yapısı, SQLite'dan PostgreSQL'e geçiş süreci ve veritabanı yönetimi konularını detaylandırmaktadır.

## ⚙️ Veritabanı Mimarisi

### 1. PostgreSQL Yapılandırması

#### 1.1. Temel Ayarlar
```sql
-- Veritabanı oluşturma
CREATE DATABASE finasis WITH ENCODING 'UTF8' LC_COLLATE='tr_TR.UTF-8' LC_CTYPE='tr_TR.UTF-8';

-- Kullanıcı oluşturma ve yetkilendirme
CREATE USER finasis_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE finasis TO finasis_user;
```

#### 1.2. Performans Ayarları
```ini
# postgresql.conf
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 768MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 13107kB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
max_parallel_maintenance_workers = 2
```

### 2. İndeks Yapıları

#### 2.1. Önerilen İndeksler
```sql
-- Müşteri tablosu için indeksler
CREATE INDEX idx_customers_tax_number ON customers(tax_number);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_created_at ON customers(created_at);

-- Fatura tablosu için indeksler
CREATE INDEX idx_invoices_customer_id ON invoices(customer_id);
CREATE INDEX idx_invoices_date ON invoices(date);
CREATE INDEX idx_invoices_status ON invoices(status);

-- Ödeme tablosu için indeksler
CREATE INDEX idx_payments_invoice_id ON payments(invoice_id);
CREATE INDEX idx_payments_date ON payments(date);
CREATE INDEX idx_payments_type ON payments(payment_type);
```

## 🔧 Veritabanı Yönetimi

### 1. SQLite'dan PostgreSQL'e Geçiş

#### 1.1. Veri Aktarımı
```bash
# SQLite dump oluşturma
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > db_backup.json

# PostgreSQL'e aktarma
python manage.py loaddata db_backup.json
```

#### 1.2. Şema Dönüşümü
```bash
# Migrasyon dosyalarını oluşturma
python manage.py makemigrations

# Migrasyonları uygulama
python manage.py migrate
```

### 2. Yedekleme ve Geri Yükleme

#### 2.1. Otomatik Yedekleme
```bash
# Günlük yedekleme scripti
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d)
pg_dump -U finasis_user finasis > $BACKUP_DIR/finasis_$DATE.sql
```

#### 2.2. Yedekten Geri Yükleme
```bash
# Yedekten geri yükleme
psql -U finasis_user finasis < backup_file.sql
```

## 🧪 Veritabanı Bakımı

### 1. Düzenli Bakım İşlemleri
```sql
-- Tablo istatistiklerini güncelleme
ANALYZE VERBOSE;

-- Kullanılmayan indeksleri temizleme
VACUUM ANALYZE;

-- Tablo boyutlarını kontrol etme
SELECT pg_size_pretty(pg_total_relation_size('table_name'));
```

### 2. Performans İzleme
```sql
-- Yavaş çalışan sorguları bulma
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## 📝 Sık Karşılaşılan Sorunlar ve Çözümleri

### 1. Bağlantı Havuzu Tükenmesi
**Sorun**: Veritabanı bağlantıları tükeniyor
**Çözüm**:
- `max_connections` değerini artırın
- Bağlantı havuzu yapılandırmasını optimize edin
- Kullanılmayan bağlantıları kapatın

### 2. Yavaş Sorgu Performansı
**Sorun**: Bazı sorgular çok yavaş çalışıyor
**Çözüm**:
- İndeksleri kontrol edin ve gerekirse yeni indeksler ekleyin
- Sorgu planlarını analiz edin
- Tablo istatistiklerini güncelleyin

### 3. Disk Alanı Tükenmesi
**Sorun**: Veritabanı dosyaları çok fazla yer kaplıyor
**Çözüm**:
- Eski WAL dosyalarını temizleyin
- Kullanılmayan tabloları ve indeksleri kaldırın
- VACUUM FULL işlemi yapın

## 📂 Dosya Yapısı ve Referanslar

```
finasis/
├── postgres/
│   ├── init/              # Veritabanı başlangıç scriptleri
│   ├── backup/            # Yedekleme dizini
│   └── conf/              # PostgreSQL yapılandırma dosyaları
├── scripts/
│   ├── backup.sh          # Yedekleme scripti
│   └── maintenance.sh     # Bakım scripti
└── migrations/            # Django migrasyon dosyaları
```

## 🔍 Ek Kaynaklar

- [PostgreSQL Performans İpuçları](https://www.postgresql.org/docs/current/performance-tips.html)
- [Django Veritabanı Optimizasyonu](https://docs.djangoproject.com/en/stable/topics/db/optimization/)
- [PostgreSQL Yedekleme ve Kurtarma](https://www.postgresql.org/docs/current/backup.html) 