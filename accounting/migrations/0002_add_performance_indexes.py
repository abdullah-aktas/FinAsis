"""
Performance-critical database indexes - Phase 1 (P0 Critical)
Generated: 2024
Estimated performance gain: 60-90% on indexed queries
Disk overhead: ~15-20% of table sizes
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),  # Adjust to your latest migration
    ]

    operations = [
        # ============================================================================
        # COMPANY MODEL INDEXES
        # ============================================================================
        migrations.AddIndex(
            model_name='company',
            index=models.Index(
                fields=['is_active'],
                name='acc_company_is_active_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='company',
            index=models.Index(
                fields=['is_active', 'created_at'],
                name='acc_company_active_created_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='company',
            index=models.Index(
                fields=['created_at'],
                name='acc_company_created_idx'
            ),
        ),
        
        # ============================================================================
        # CUSTOMER MODEL INDEXES
        # ============================================================================
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(
                fields=['tax_number'],
                name='acc_customer_tax_number_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(
                fields=['company', 'is_active'],
                name='acc_customer_company_active_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(
                fields=['company', 'email'],
                name='acc_customer_company_email_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(
                fields=['email'],
                name='acc_customer_email_idx'
            ),
        ),
        
        # ============================================================================
        # INVOICE MODEL INDEXES
        # ============================================================================
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(
                fields=['issue_date'],
                name='acc_invoice_issue_date_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(
                fields=['company', 'issue_date'],
                name='acc_invoice_company_date_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(
                fields=['customer', 'issue_date'],
                name='acc_invoice_customer_date_idx'
            ),
        ),
        
        # ============================================================================
        # BANKTRANSACTION MODEL INDEXES
        # ============================================================================
        migrations.AddIndex(
            model_name='banktransaction',
            index=models.Index(
                fields=['date'],
                name='acc_banktxn_date_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='banktransaction',
            index=models.Index(
                fields=['account', 'date'],
                name='acc_banktxn_account_date_idx'
            ),
        ),
        
        # ============================================================================
        # PAYMENT MODEL INDEXES
        # ============================================================================
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(
                fields=['payment_date'],
                name='acc_payment_date_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(
                fields=['company', 'payment_date'],
                name='acc_payment_company_date_idx'
            ),
        ),
        
        # ============================================================================
        # EXPENSE MODEL INDEXES
        # ============================================================================
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(
                fields=['expense_date'],
                name='acc_expense_date_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(
                fields=['company', 'expense_date'],
                name='acc_expense_company_date_idx'
            ),
        ),
        
        # ============================================================================
        # SALE MODEL INDEXES
        # ============================================================================
        migrations.AddIndex(
            model_name='sale',
            index=models.Index(
                fields=['sale_date'],
                name='acc_sale_date_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='sale',
            index=models.Index(
                fields=['company', 'sale_date'],
                name='acc_sale_company_date_idx'
            ),
        ),
        
        # ============================================================================
        # PRODUCT MODEL INDEXES
        # ============================================================================
        migrations.AddIndex(
            model_name='product',
            index=models.Index(
                fields=['company', 'is_active'],
                name='acc_product_company_active_idx'
            ),
        ),
        
        # ============================================================================
        # EDEFTER MODEL INDEXES
        # ============================================================================
        migrations.AddIndex(
            model_name='edefter',
            index=models.Index(
                fields=['company', 'year', 'month'],
                name='acc_edefter_period_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='edefter',
            index=models.Index(
                fields=['year', 'month'],
                name='acc_edefter_year_month_idx'
            ),
        ),
    ]
