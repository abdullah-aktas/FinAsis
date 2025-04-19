from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # İndeksler
            sql="""
            -- Fatura indeksleri
            CREATE INDEX IF NOT EXISTS idx_invoice_number ON accounting_invoice(invoice_number);
            CREATE INDEX IF NOT EXISTS idx_invoice_date ON accounting_invoice(invoice_date);
            CREATE INDEX IF NOT EXISTS idx_invoice_status ON accounting_invoice(status);
            CREATE INDEX IF NOT EXISTS idx_invoice_customer ON accounting_invoice(customer_id);
            CREATE INDEX IF NOT EXISTS idx_invoice_created_at ON accounting_invoice(created_at);
            
            -- Müşteri indeksleri
            CREATE INDEX IF NOT EXISTS idx_customer_name ON crm_customer(name);
            CREATE INDEX IF NOT EXISTS idx_customer_email ON crm_customer(email);
            CREATE INDEX IF NOT EXISTS idx_customer_tax_number ON crm_customer(tax_number);
            
            -- Kullanıcı indeksleri
            CREATE INDEX IF NOT EXISTS idx_user_email ON accounts_user(email);
            CREATE INDEX IF NOT EXISTS idx_user_role ON accounts_user(role);
            
            -- Genel indeksler
            CREATE INDEX IF NOT EXISTS idx_created_at ON accounting_invoice(created_at);
            CREATE INDEX IF NOT EXISTS idx_updated_at ON accounting_invoice(updated_at);
            CREATE INDEX IF NOT EXISTS idx_is_active ON accounting_invoice(is_active);
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS idx_invoice_number;
            DROP INDEX IF EXISTS idx_invoice_date;
            DROP INDEX IF EXISTS idx_invoice_status;
            DROP INDEX IF EXISTS idx_invoice_customer;
            DROP INDEX IF EXISTS idx_invoice_created_at;
            DROP INDEX IF EXISTS idx_customer_name;
            DROP INDEX IF EXISTS idx_customer_email;
            DROP INDEX IF EXISTS idx_customer_tax_number;
            DROP INDEX IF EXISTS idx_user_email;
            DROP INDEX IF EXISTS idx_user_role;
            DROP INDEX IF EXISTS idx_created_at;
            DROP INDEX IF EXISTS idx_updated_at;
            DROP INDEX IF EXISTS idx_is_active;
            """
        ),
    ] 