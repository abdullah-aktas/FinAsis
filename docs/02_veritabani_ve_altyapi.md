# 2. Veritabanƒ± ve Altyapƒ±

## üìå Ama√ß
Bu dok√ºmantasyon, FinAsis projesinin veritabanƒ± yapƒ±sƒ±, SQLite'dan PostgreSQL'e ge√ßi≈ü s√ºreci ve veritabanƒ± y√∂netimi konularƒ±nƒ± detaylandƒ±rmaktadƒ±r.

## ‚öôÔ∏è Veritabanƒ± Mimarisi

### 1. PostgreSQL Yapƒ±landƒ±rmasƒ±

#### 1.1. Temel Ayarlar
```sql
-- Veritabanƒ± olu≈üturma
CREATE DATABASE finasis WITH ENCODING 'UTF8' LC_COLLATE='tr_TR.UTF-8' LC_CTYPE='tr_TR.UTF-8';

-- Kullanƒ±cƒ± olu≈üturma ve yetkilendirme
CREATE USER finasis_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE finasis TO finasis_user;
```

#### 1.2. Performans Ayarlarƒ±
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

### 2. ƒ∞ndeks Yapƒ±larƒ±

#### 2.1. √ñnerilen ƒ∞ndeksler
```sql
-- M√º≈üteri tablosu i√ßin indeksler
CREATE INDEX idx_customers_tax_number ON customers(tax_number);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_created_at ON customers(created_at);

-- Fatura tablosu i√ßin indeksler
CREATE INDEX idx_invoices_customer_id ON invoices(customer_id);
CREATE INDEX idx_invoices_date ON invoices(date);
CREATE INDEX idx_invoices_status ON invoices(status);

-- √ñdeme tablosu i√ßin indeksler
CREATE INDEX idx_payments_invoice_id ON payments(invoice_id);
CREATE INDEX idx_payments_date ON payments(date);
CREATE INDEX idx_payments_type ON payments(payment_type);
```

## üîß Veritabanƒ± Y√∂netimi

### 1. SQLite'dan PostgreSQL'e Ge√ßi≈ü

#### 1.1. Veri Aktarƒ±mƒ±
```bash
# SQLite dump olu≈üturma
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > db_backup.json

# PostgreSQL'e aktarma
python manage.py loaddata db_backup.json
```

#### 1.2. ≈ûema D√∂n√º≈ü√ºm√º
```bash
# Migrasyon dosyalarƒ±nƒ± olu≈üturma
python manage.py makemigrations

# Migrasyonlarƒ± uygulama
python manage.py migrate
```

### 2. Yedekleme ve Geri Y√ºkleme

#### 2.1. Otomatik Yedekleme
```bash
# G√ºnl√ºk yedekleme scripti
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d)
pg_dump -U finasis_user finasis > $BACKUP_DIR/finasis_$DATE.sql
```

#### 2.2. Yedekten Geri Y√ºkleme
```bash
# Yedekten geri y√ºkleme
psql -U finasis_user finasis < backup_file.sql
```

## üß™ Veritabanƒ± Bakƒ±mƒ±

### 1. D√ºzenli Bakƒ±m ƒ∞≈ülemleri
```sql
-- Tablo istatistiklerini g√ºncelleme
ANALYZE VERBOSE;

-- Kullanƒ±lmayan indeksleri temizleme
VACUUM ANALYZE;

-- Tablo boyutlarƒ±nƒ± kontrol etme
SELECT pg_size_pretty(pg_total_relation_size('table_name'));
```

### 2. Performans ƒ∞zleme
```sql
-- Yava≈ü √ßalƒ±≈üan sorgularƒ± bulma
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## üìù Sƒ±k Kar≈üƒ±la≈üƒ±lan Sorunlar ve √á√∂z√ºmleri

### 1. Baƒülantƒ± Havuzu T√ºkenmesi
**Sorun**: Veritabanƒ± baƒülantƒ±larƒ± t√ºkeniyor
**√á√∂z√ºm**:
- `max_connections` deƒüerini artƒ±rƒ±n
- Baƒülantƒ± havuzu yapƒ±landƒ±rmasƒ±nƒ± optimize edin
- Kullanƒ±lmayan baƒülantƒ±larƒ± kapatƒ±n

### 2. Yava≈ü Sorgu Performansƒ±
**Sorun**: Bazƒ± sorgular √ßok yava≈ü √ßalƒ±≈üƒ±yor
**√á√∂z√ºm**:
- ƒ∞ndeksleri kontrol edin ve gerekirse yeni indeksler ekleyin
- Sorgu planlarƒ±nƒ± analiz edin
- Tablo istatistiklerini g√ºncelleyin

### 3. Disk Alanƒ± T√ºkenmesi
**Sorun**: Veritabanƒ± dosyalarƒ± √ßok fazla yer kaplƒ±yor
**√á√∂z√ºm**:
- Eski WAL dosyalarƒ±nƒ± temizleyin
- Kullanƒ±lmayan tablolarƒ± ve indeksleri kaldƒ±rƒ±n
- VACUUM FULL i≈ülemi yapƒ±n

## üìÇ Dosya Yapƒ±sƒ± ve Referanslar

```
finasis/
‚îú‚îÄ‚îÄ postgres/
‚îÇ   ‚îú‚îÄ‚îÄ init/              # Veritabanƒ± ba≈ülangƒ±√ß scriptleri
‚îÇ   ‚îú‚îÄ‚îÄ backup/            # Yedekleme dizini
‚îÇ   ‚îî‚îÄ‚îÄ conf/              # PostgreSQL yapƒ±landƒ±rma dosyalarƒ±
‚îú‚îÄ‚îÄ scripts/
‚îÇ   ‚îú‚îÄ‚îÄ backup.sh          # Yedekleme scripti
‚îÇ   ‚îî‚îÄ‚îÄ maintenance.sh     # Bakƒ±m scripti
‚îî‚îÄ‚îÄ migrations/            # Django migrasyon dosyalarƒ±
```

## üîç Ek Kaynaklar

- [PostgreSQL Performans ƒ∞pu√ßlarƒ±](https://www.postgresql.org/docs/current/performance-tips.html)
- [Django Veritabanƒ± Optimizasyonu](https://docs.djangoproject.com/en/stable/topics/db/optimization/)
- [PostgreSQL Yedekleme ve Kurtarma](https://www.postgresql.org/docs/current/backup.html) 