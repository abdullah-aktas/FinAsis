# Generated migration to fix TrialBalanceSnapshot created_by reference
from django.conf import settings
from django.db import migrations, models, connection
import django.db.models.deletion


def migrate_data_forward(apps, schema_editor):
    """
    SQLite doesn't support ALTER COLUMN directly for foreign keys.
    We need to recreate the table with correct schema.
    """
    if connection.vendor == 'sqlite':
        # Get the data
        with connection.cursor() as cursor:
            # Step 1: Create a temporary table with correct schema
            cursor.execute("""
                CREATE TABLE "finance_trialbalancesnapshot_new" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "as_of_date" date NOT NULL,
                    "created_at" datetime NOT NULL,
                    "account_balances" text NOT NULL CHECK ((JSON_VALID("account_balances") OR "account_balances" IS NULL)),
                    "total_debits" decimal NOT NULL,
                    "total_credits" decimal NOT NULL,
                    "company_id" bigint NOT NULL REFERENCES "accounting_company" ("id") DEFERRABLE INITIALLY DEFERRED,
                    "created_by_id" bigint NULL REFERENCES "accounts_customuser" ("id") DEFERRABLE INITIALLY DEFERRED,
                    "fiscal_period_id" bigint NOT NULL REFERENCES "finance_fiscalperiod" ("id") DEFERRABLE INITIALLY DEFERRED
                )
            """)
            
            # Step 2: Copy data from old table
            cursor.execute("""
                INSERT INTO "finance_trialbalancesnapshot_new" 
                (id, as_of_date, created_at, account_balances, total_debits, total_credits, company_id, created_by_id, fiscal_period_id)
                SELECT id, as_of_date, created_at, account_balances, total_debits, total_credits, company_id, created_by_id, fiscal_period_id
                FROM "finance_trialbalancesnapshot"
            """)
            
            # Step 3: Drop old table
            cursor.execute('DROP TABLE "finance_trialbalancesnapshot"')
            
            # Step 4: Rename new table
            cursor.execute('ALTER TABLE "finance_trialbalancesnapshot_new" RENAME TO "finance_trialbalancesnapshot"')
            
            # Step 5: Recreate indexes
            cursor.execute("""
                CREATE INDEX "finance_tri_compan_f37d85_idx" 
                ON "finance_trialbalancesnapshot" ("company_id", "as_of_date")
            """)
            
            cursor.execute("""
                CREATE INDEX "finance_trialbalancesnapshot_company_id_idx" 
                ON "finance_trialbalancesnapshot" ("company_id")
            """)
            
            cursor.execute("""
                CREATE INDEX "finance_trialbalancesnapshot_fiscal_period_id_idx" 
                ON "finance_trialbalancesnapshot" ("fiscal_period_id")
            """)
            
            cursor.execute("""
                CREATE INDEX "finance_trialbalancesnapshot_created_by_id_idx" 
                ON "finance_trialbalancesnapshot" ("created_by_id")
            """)


def migrate_data_backward(apps, schema_editor):
    """Backward migration if needed"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0013_rename_finance_aud_company_idx_001_finance_aud_company_caa4a3_idx_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(migrate_data_forward, migrate_data_backward),
    ]

