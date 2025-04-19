# Veritabanı Şeması

Bu dokümantasyon, FinAsis projesinin veritabanı yapısını ve ilişkilerini detaylandırmaktadır.

## İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Tablolar](#tablolar)
3. [İlişkiler](#ilişkiler)
4. [İndeksler](#indeksler)
5. [Migrations](#migrations)
6. [Backup ve Restore](#backup-ve-restore)

## Genel Bakış

FinAsis, PostgreSQL veritabanı kullanmaktadır. Veritabanı şeması aşağıdaki ana modülleri içerir:

- Kullanıcı Yönetimi
- Finans Yönetimi
- Muhasebe
- E-Belge
- Raporlama

## Tablolar

### Kullanıcı Yönetimi

#### users

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(30),
    last_name VARCHAR(30),
    is_active BOOLEAN DEFAULT true,
    is_staff BOOLEAN DEFAULT false,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

#### user_profiles

```sql
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    company_name VARCHAR(100),
    tax_number VARCHAR(20),
    tax_office VARCHAR(100),
    address TEXT,
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Finans Yönetimi

#### accounts

```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    currency VARCHAR(3) DEFAULT 'TRY',
    balance DECIMAL(15,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_accounts_account_type ON accounts(account_type);
```

#### transactions

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    transaction_type VARCHAR(50) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'TRY',
    description TEXT,
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_transaction_date ON transactions(transaction_date);
```

### Muhasebe

#### chart_of_accounts

```sql
CREATE TABLE chart_of_accounts (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    parent_id INTEGER REFERENCES chart_of_accounts(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chart_of_accounts_code ON chart_of_accounts(code);
CREATE INDEX idx_chart_of_accounts_parent_id ON chart_of_accounts(parent_id);
```

#### journal_entries

```sql
CREATE TABLE journal_entries (
    id SERIAL PRIMARY KEY,
    entry_date DATE NOT NULL,
    reference_no VARCHAR(50),
    description TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_journal_entries_entry_date ON journal_entries(entry_date);
CREATE INDEX idx_journal_entries_reference_no ON journal_entries(reference_no);
```

#### journal_entry_lines

```sql
CREATE TABLE journal_entry_lines (
    id SERIAL PRIMARY KEY,
    journal_entry_id INTEGER REFERENCES journal_entries(id) ON DELETE CASCADE,
    account_id INTEGER REFERENCES chart_of_accounts(id),
    debit DECIMAL(15,2) DEFAULT 0,
    credit DECIMAL(15,2) DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_journal_entry_lines_journal_entry_id ON journal_entry_lines(journal_entry_id);
CREATE INDEX idx_journal_entry_lines_account_id ON journal_entry_lines(account_id);
```

### E-Belge

#### e_invoices

```sql
CREATE TABLE e_invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_type VARCHAR(20) NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE,
    total_amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'TRY',
    status VARCHAR(20) DEFAULT 'DRAFT',
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_e_invoices_invoice_number ON e_invoices(invoice_number);
CREATE INDEX idx_e_invoices_invoice_date ON e_invoices(invoice_date);
```

#### e_invoice_items

```sql
CREATE TABLE e_invoice_items (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES e_invoices(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    quantity DECIMAL(15,2) NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    vat_rate INTEGER,
    vat_amount DECIMAL(15,2),
    total_amount DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_e_invoice_items_invoice_id ON e_invoice_items(invoice_id);
```

## İlişkiler

### One-to-One İlişkiler

- users <-> user_profiles
- accounts <-> account_settings

### One-to-Many İlişkiler

- users -> accounts
- accounts -> transactions
- users -> journal_entries
- journal_entries -> journal_entry_lines
- chart_of_accounts -> journal_entry_lines
- e_invoices -> e_invoice_items

### Many-to-Many İlişkiler

- users <-> roles (through user_roles)
- permissions <-> roles (through role_permissions)

## İndeksler

### Performans İndeksleri

```sql
-- Sık sorgulanan alanlar için indeksler
CREATE INDEX idx_transactions_date_type ON transactions(transaction_date, transaction_type);
CREATE INDEX idx_journal_entries_date_status ON journal_entries(entry_date, status);
CREATE INDEX idx_e_invoices_date_status ON e_invoices(invoice_date, status);

-- Tam metin araması için indeksler
CREATE INDEX idx_users_full_name ON users USING gin(to_tsvector('turkish', first_name || ' ' || last_name));
CREATE INDEX idx_e_invoices_description ON e_invoices USING gin(to_tsvector('turkish', description));
```

## Migrations

### Migration Komutları

```bash
# Migration oluşturma
python manage.py makemigrations

# Migration uygulama
python manage.py migrate

# Migration durumu
python manage.py showmigrations
```

### Örnek Migration

```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='currency',
            field=models.CharField(default='TRY', max_length=3),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['transaction_date', 'transaction_type'], name='idx_transactions_date_type'),
        ),
    ]
```

## Backup ve Restore

### Backup

```bash
# Tam yedekleme
pg_dump -U postgres -d finasis > backup.sql

# Sıkıştırılmış yedekleme
pg_dump -U postgres -d finasis | gzip > backup.sql.gz
```

### Restore

```bash
# Tam geri yükleme
psql -U postgres -d finasis < backup.sql

# Sıkıştırılmış dosyadan geri yükleme
gunzip -c backup.sql.gz | psql -U postgres -d finasis
```

### Otomatik Yedekleme

```bash
# Günlük yedekleme için cron job
0 0 * * * pg_dump -U postgres -d finasis | gzip > /backup/finasis_$(date +\%Y\%m\%d).sql.gz
``` 