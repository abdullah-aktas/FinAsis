# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import (
    ChartOfAccounts, Account, Invoice, InvoiceLine,
    Transaction, TransactionLine, CashBox, Bank, Stock, StockTransaction
)

@admin.register(ChartOfAccounts)
class ChartOfAccountsAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'type', 'level', 'is_leaf')
    list_filter = ('type', 'level', 'is_leaf')
    search_fields = ('code', 'name')
    ordering = ('code',)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'type', 'balance')
    list_filter = ('type',)
    search_fields = ('code', 'name', 'tax_number')
    ordering = ('code',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'account', 'type', 'grand_total')
    list_filter = ('type', 'date')
    search_fields = ('number', 'account__name')
    ordering = ('-date',)

@admin.register(InvoiceLine)
class InvoiceLineAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'product', 'quantity', 'unit_price', 'total')
    list_filter = ('invoice__type',)
    search_fields = ('product', 'invoice__number')
    ordering = ('-invoice__date',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'description')
    list_filter = ('date',)
    search_fields = ('number', 'description')
    ordering = ('-date',)

@admin.register(TransactionLine)
class TransactionLineAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'account_code', 'debit', 'credit')
    list_filter = ('transaction__date',)
    search_fields = ('account_code', 'description')
    ordering = ('-transaction__date',)

@admin.register(CashBox)
class CashBoxAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'balance')
    search_fields = ('code', 'name')
    ordering = ('code',)

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'account_number', 'balance')
    search_fields = ('code', 'name', 'account_number', 'iban')
    ordering = ('code',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'unit', 'quantity', 'unit_price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('stock', 'date', 'type', 'quantity', 'created_at')
    list_filter = ('type', 'date', 'stock')
    search_fields = ('stock__code', 'stock__name', 'description')
    date_hierarchy = 'date'

"""
Muhasebe modülü admin arayüzü ayarları burada tanımlanır.
"""

# class AccountAdmin(admin.ModelAdmin):
#     """Hesap modeli için admin arayüzü ayarları."""
#     list_display = ('id', 'hesap_adi')
# admin.site.register(Account, AccountAdmin)
