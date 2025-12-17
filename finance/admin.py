from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Transaction,
    Account,
    Budget,
    Tax,
    CashFlow,
    IncomeStatement,
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

# BankAccount ve Invoice accounting modülünde yönetiliyor, burada kaldırıldı
# admin.site.register(BankAccount)  # accounting.BankAccount kullanılıyor
# admin.site.register(Invoice)  # accounting.Invoice kullanılıyor


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "amount", "transaction_type", "date", "description_short", "balance_after")
    list_filter = ("transaction_type", "date", "account")
    search_fields = ("description", "account__name", "reference")
    date_hierarchy = "date"
    readonly_fields = ("balance_after", "created_at", "updated_at")
    ordering = ("-date",)
    
    fieldsets = (
        (_("Temel Bilgiler"), {
            "fields": ("account", "amount", "transaction_type", "date")
        }),
        (_("Detaylar"), {
            "fields": ("description", "reference", "category")
        }),
        (_("Bilgiler"), {
            "fields": ("balance_after", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def description_short(self, obj):
        return obj.description[:50] + "..." if obj.description and len(obj.description) > 50 else obj.description or "-"
    description_short.short_description = "Açıklama"


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "account_type", "balance", "currency", "is_active", "created_at")
    list_filter = ("account_type", "currency", "is_active", "created_at")
    search_fields = ("name", "account_number", "description")
    readonly_fields = ("balance", "created_at", "updated_at")
    
    fieldsets = (
        (_("Temel Bilgiler"), {
            "fields": ("name", "account_type", "account_number", "currency")
        }),
        (_("Durum"), {
            "fields": ("balance", "is_active")
        }),
        (_("Detaylar"), {
            "fields": ("description", "bank_name", "bank_branch")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "amount", "period", "spent_amount", "remaining", "status")
    list_filter = ("period", "category", "status", "start_date")
    search_fields = ("name", "category", "description")
    date_hierarchy = "start_date"
    readonly_fields = ("spent_amount", "remaining", "created_at", "updated_at")
    
    fieldsets = (
        (_("Temel Bilgiler"), {
            "fields": ("name", "category", "description")
        }),
        (_("Bütçe Bilgileri"), {
            "fields": ("amount", "period", "start_date", "end_date")
        }),
        (_("Durum"), {
            "fields": ("status", "spent_amount", "remaining")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def remaining(self, obj):
        return obj.amount - obj.spent_amount
    remaining.short_description = "Kalan"


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("name", "tax_type", "rate", "amount", "due_date", "status", "paid_date")
    list_filter = ("tax_type", "status", "due_date")
    search_fields = ("name", "description", "reference")
    date_hierarchy = "due_date"
    readonly_fields = ("paid_date", "created_at", "updated_at")
    
    fieldsets = (
        (_("Temel Bilgiler"), {
            "fields": ("name", "tax_type", "description")
        }),
        (_("Vergi Bilgileri"), {
            "fields": ("rate", "amount", "taxable_amount")
        }),
        (_("Tarihler"), {
            "fields": ("due_date", "paid_date", "status")
        }),
        (_("Referans"), {
            "fields": ("reference", "invoice_number")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
    list_display = ("period", "opening_balance", "total_inflow", "total_outflow", "closing_balance", "created_at")
    list_filter = ("period", "created_at")
    search_fields = ("period", "description")
    date_hierarchy = "period"
    readonly_fields = ("opening_balance", "closing_balance", "created_at", "updated_at")
    
    fieldsets = (
        (_("Dönem Bilgileri"), {
            "fields": ("period", "description")
        }),
        (_("Nakit Akışı"), {
            "fields": ("opening_balance", "total_inflow", "total_outflow", "closing_balance")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(IncomeStatement)
class IncomeStatementAdmin(admin.ModelAdmin):
    list_display = ("period", "total_revenue", "total_expenses", "net_income", "created_at")
    list_filter = ("period", "created_at")
    search_fields = ("period", "description")
    date_hierarchy = "period"
    readonly_fields = ("net_income", "created_at", "updated_at")
    
    fieldsets = (
        (_("Dönem Bilgileri"), {
            "fields": ("period", "description")
        }),
        (_("Gelir Tablosu"), {
            "fields": ("total_revenue", "total_expenses", "net_income")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ("name", "report_type", "period", "generated_at", "status")
    list_filter = ("report_type", "status", "generated_at")
    search_fields = ("name", "description", "period")
    date_hierarchy = "generated_at"
    readonly_fields = ("generated_at", "created_at", "updated_at")
    
    fieldsets = (
        (_("Temel Bilgiler"), {
            "fields": ("name", "report_type", "description")
        }),
        (_("Dönem"), {
            "fields": ("period", "start_date", "end_date")
        }),
        (_("Durum"), {
            "fields": ("status", "generated_at")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(EInvoice)
class EInvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "invoice_date", "total_amount", "status", "customer_name", "created_at")
    list_filter = ("status", "invoice_date", "created_at")
    search_fields = ("invoice_number", "customer_name", "customer_tax_id")
    date_hierarchy = "invoice_date"
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        (_("Fatura Bilgileri"), {
            "fields": ("invoice_number", "invoice_date", "due_date", "status")
        }),
        (_("Müşteri"), {
            "fields": ("customer_name", "customer_tax_id", "customer_address")
        }),
        (_("Tutar"), {
            "fields": ("subtotal", "tax_amount", "total_amount")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(EInvoiceItem)
class EInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "product_name", "quantity", "unit_price", "total", "line_number")
    list_filter = ("invoice",)
    search_fields = ("product_name", "invoice__invoice_number")
    readonly_fields = ("total", "created_at")
    
    fieldsets = (
        (_("Fatura"), {
            "fields": ("invoice", "line_number")
        }),
        (_("Ürün/Hizmet"), {
            "fields": ("product_name", "description")
        }),
        (_("Miktar ve Fiyat"), {
            "fields": ("quantity", "unit_price", "total")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "employee_id", "department", "position", "salary", "hire_date", "is_active")
    list_filter = ("department", "position", "is_active", "hire_date")
    search_fields = ("name", "employee_id", "email", "phone")
    date_hierarchy = "hire_date"
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        (_("Kişisel Bilgiler"), {
            "fields": ("name", "employee_id", "email", "phone", "address")
        }),
        (_("İş Bilgileri"), {
            "fields": ("department", "position", "hire_date", "is_active")
        }),
        (_("Maaş"), {
            "fields": ("salary", "salary_currency")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ("voucher_number", "voucher_date", "voucher_type", "amount", "status", "created_at")
    list_filter = ("voucher_type", "status", "voucher_date")
    search_fields = ("voucher_number", "description", "reference")
    date_hierarchy = "voucher_date"
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        (_("Fiş Bilgileri"), {
            "fields": ("voucher_number", "voucher_date", "voucher_type", "status")
        }),
        (_("Tutar ve Detaylar"), {
            "fields": ("amount", "description", "reference")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


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
