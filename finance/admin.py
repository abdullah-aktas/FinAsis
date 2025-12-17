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
    list_display = (
        "id",
        "type",
        "amount",
        "status",
        "transaction_date",
        "description_short",
    )
    list_filter = ("type", "status", "transaction_date")
    search_fields = ("description",)
    date_hierarchy = "transaction_date"
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-transaction_date",)

    fieldsets = (
        (
            _("Temel Bilgiler"),
            {"fields": ("type", "amount", "status", "transaction_date")},
        ),
        (_("Detaylar"), {"fields": ("description",)}),
        (
            _("Bilgiler"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def description_short(self, obj):
        return (
            obj.description[:50] + "..."
            if obj.description and len(obj.description) > 50
            else obj.description or "-"
        )

    description_short.short_description = "Açıklama"


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "type",
        "balance",
        "currency",
        "is_active",
        "created_at",
    )
    list_filter = ("type", "currency", "is_active", "created_at")
    search_fields = ("name", "code", "description")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (_("Temel Bilgiler"), {"fields": ("name", "code", "type", "currency")}),
        (_("Durum"), {"fields": ("balance", "is_active")}),
        (_("Detaylar"), {"fields": ("description",)}),
        (
            _("Bilgiler"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "amount",
        "actual_amount",
        "remaining",
        "start_date",
        "end_date",
    )
    list_filter = ("category", "start_date", "end_date")
    search_fields = ("name", "category", "description")
    date_hierarchy = "start_date"
    readonly_fields = ("remaining", "created_at", "updated_at")

    fieldsets = (
        (_("Temel Bilgiler"), {"fields": ("name", "category", "description")}),
        (
            _("Bütçe Bilgileri"),
            {"fields": ("amount", "actual_amount", "start_date", "end_date")},
        ),
        (_("Durum"), {"fields": ("remaining", "is_active")}),
        (
            _("Bilgiler"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def remaining(self, obj):
        return obj.amount - obj.actual_amount

    remaining.short_description = "Kalan"


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "type", "rate", "is_active", "created_at")
    list_filter = ("type", "is_active", "created_at")
    search_fields = ("name", "code", "description")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (_("Temel Bilgiler"), {"fields": ("name", "code", "type", "description")}),
        (_("Vergi Bilgileri"), {"fields": ("rate",)}),
        (_("Durum"), {"fields": ("is_active",)}),
        (
            _("Bilgiler"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
    list_display = (
        "period",
        "start_date",
        "end_date",
        "opening_balance",
        "total_income",
        "total_expense",
        "closing_balance",
        "net_cash_flow",
    )
    list_filter = ("period", "start_date", "end_date", "created_at")
    search_fields = ("period",)
    date_hierarchy = "start_date"
    readonly_fields = ("net_cash_flow", "created_at", "updated_at")

    fieldsets = (
        (_("Dönem Bilgileri"), {"fields": ("period", "start_date", "end_date")}),
        (
            _("Nakit Akışı"),
            {
                "fields": (
                    "opening_balance",
                    "total_income",
                    "total_expense",
                    "closing_balance",
                    "net_cash_flow",
                )
            },
        ),
        (
            _("Bilgiler"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(IncomeStatement)
class IncomeStatementAdmin(admin.ModelAdmin):
    list_display = (
        "period",
        "start_date",
        "end_date",
        "revenue",
        "operating_expenses",
        "net_income",
        "created_at",
    )
    list_filter = ("period", "start_date", "end_date", "created_at")
    search_fields = ("period",)
    date_hierarchy = "start_date"
    readonly_fields = (
        "gross_profit",
        "operating_income",
        "net_income",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (_("Dönem Bilgileri"), {"fields": ("period", "start_date", "end_date")}),
        (
            _("Gelir Tablosu"),
            {
                "fields": (
                    "revenue",
                    "cost_of_goods_sold",
                    "gross_profit",
                    "operating_expenses",
                    "operating_income",
                    "other_income",
                    "other_expenses",
                    "net_income",
                )
            },
        ),
        (
            _("Bilgiler"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "start_date", "end_date", "status", "created_at")
    list_filter = ("type", "status", "start_date", "end_date", "created_at")
    search_fields = ("name",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (_("Temel Bilgiler"), {"fields": ("name", "type", "status")}),
        (_("Dönem"), {"fields": ("start_date", "end_date")}),
        (_("Parametreler"), {"fields": ("parameters",)}),
        (
            _("Bilgiler"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(EInvoice)
class EInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "invoice_type",
        "issue_date",
        "due_date",
        "total",
        "status",
        "customer",
        "created_at",
    )
    list_filter = ("status", "invoice_type", "issue_date", "due_date", "created_at")
    search_fields = ("invoice_number", "customer__name")
    date_hierarchy = "issue_date"
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            _("Fatura Bilgileri"),
            {
                "fields": (
                    "invoice_number",
                    "invoice_type",
                    "issue_date",
                    "due_date",
                    "status",
                )
            },
        ),
        (_("Müşteri"), {"fields": ("customer",)}),
        (_("Tutar"), {"fields": ("subtotal", "tax_total", "total", "currency")}),
        (_("Ek Bilgiler"), {"fields": ("note", "uuid", "sent_at", "accepted_at")}),
        (
            _("Bilgiler"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(EInvoiceItem)
class EInvoiceItemAdmin(admin.ModelAdmin):
    list_display = (
        "invoice",
        "description",
        "quantity",
        "unit",
        "unit_price",
        "tax_rate",
        "line_total",
        "tax_amount",
    )
    list_filter = ("invoice",)
    search_fields = ("description", "invoice__invoice_number")
    readonly_fields = ("line_total", "tax_amount", "created_at", "updated_at")

    fieldsets = (
        (_("Fatura"), {"fields": ("invoice",)}),
        (_("Ürün/Hizmet"), {"fields": ("description",)}),
        (
            _("Miktar ve Fiyat"),
            {
                "fields": (
                    "quantity",
                    "unit",
                    "unit_price",
                    "tax_rate",
                    "line_total",
                    "tax_amount",
                )
            },
        ),
        (
            _("Bilgiler"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("user", "employee_id", "department")
    list_filter = ("department",)
    search_fields = (
        "employee_id",
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )

    fieldsets = (
        (_("Kullanıcı"), {"fields": ("user",)}),
        (_("İş Bilgileri"), {"fields": ("employee_id", "department")}),
    )


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ("employee", "amount", "description", "created_at", "tenant")
    list_filter = ("tenant", "created_at")
    search_fields = ("employee__user__username", "description", "amount")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)

    fieldsets = (
        (
            _("Fiş Bilgileri"),
            {"fields": ("employee", "amount", "description", "tenant")},
        ),
        (_("Bilgiler"), {"fields": ("created_at",), "classes": ("collapse",)}),
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
