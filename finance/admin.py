from django.contrib import admin
from .models import (
    Transaction,
    Account,
    Budget,
    Tax,
    CashFlow,
    IncomeStatement,
    BankAccount,
    Invoice,
    FinancialReport,
    EInvoice,
    EInvoiceItem,
    Employee,
    Voucher,
    InvoiceRecord,
    CreditCardStatus,
    InvestmentAsset,
    AIConfig,
)

admin.site.register(Transaction)
admin.site.register(Account)
admin.site.register(Budget)
admin.site.register(Tax)
admin.site.register(CashFlow)
admin.site.register(IncomeStatement)
# BankAccount ve Invoice accounting modülünde yönetiliyor, burada kaldırıldı
# admin.site.register(BankAccount)  # accounting.BankAccount kullanılıyor
# admin.site.register(Invoice)  # accounting.Invoice kullanılıyor
admin.site.register(FinancialReport)
admin.site.register(EInvoice)
admin.site.register(EInvoiceItem)
admin.site.register(Employee)
admin.site.register(Voucher)


@admin.register(InvoiceRecord)
class InvoiceRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "month", "amount", "created_at")
    list_filter = ("month",)
    search_fields = ("user__username",)


@admin.register(CreditCardStatus)
class CreditCardStatusAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "debt", "limit", "usage_percent", "created_at")
    list_filter = ("name",)
    search_fields = ("user__username", "name")


@admin.register(InvestmentAsset)
class InvestmentAssetAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "return_amount", "created_at")
    list_filter = ("name",)
    search_fields = ("user__username", "name")


@admin.register(AIConfig)
class AIConfigAdmin(admin.ModelAdmin):
    list_display = ("key", "active", "created_at")
    list_filter = ("active",)
