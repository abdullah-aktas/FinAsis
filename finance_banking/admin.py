from django.contrib import admin
from .models import (
    BankTransaction, BankStatement, PaymentMethod,
    BankTransfer, CheckTransaction, DirectDebit
)


@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'bank_account', 'transaction_type', 'amount', 'balance_after', 'status', 'is_reconciled')
    search_fields = ('description', 'reference_number', 'sender_name', 'recipient_name')
    list_filter = ('transaction_type', 'status', 'is_reconciled', 'transaction_date')
    date_hierarchy = 'transaction_date'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BankStatement)
class BankStatementAdmin(admin.ModelAdmin):
    list_display = ('bank_account', 'statement_date', 'period_start', 'period_end', 'opening_balance', 'closing_balance', 'transaction_count', 'is_reconciled')
    search_fields = ('bank_account__account_name', 'notes')
    list_filter = ('is_reconciled', 'statement_date')
    date_hierarchy = 'statement_date'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'method_type', 'bank_account', 'fees', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('method_type', 'is_active')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BankTransfer)
class BankTransferAdmin(admin.ModelAdmin):
    list_display = ('transfer_date', 'sender_account', 'recipient_name', 'amount', 'currency', 'transfer_type', 'status', 'initiated_by')
    search_fields = ('recipient_name', 'recipient_iban', 'reference_number', 'description')
    list_filter = ('transfer_type', 'status', 'transfer_date', 'currency')
    date_hierarchy = 'transfer_date'
    readonly_fields = ('total_amount', 'created_at', 'updated_at')


@admin.register(CheckTransaction)
class CheckTransactionAdmin(admin.ModelAdmin):
    list_display = ('check_number', 'check_type', 'drawer_name', 'payee_name', 'amount', 'due_date', 'status')
    search_fields = ('check_number', 'drawer_name', 'payee_name')
    list_filter = ('check_type', 'status', 'due_date')
    date_hierarchy = 'due_date'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DirectDebit)
class DirectDebitAdmin(admin.ModelAdmin):
    list_display = ('payee_name', 'bank_account', 'amount', 'frequency', 'next_execution_date', 'is_active')
    search_fields = ('payee_name', 'payee_account', 'description')
    list_filter = ('frequency', 'is_active', 'next_execution_date')
    readonly_fields = ('created_at', 'updated_at')

