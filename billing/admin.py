from django.contrib import admin
from .models import (
    Plan,
    Price,
    Module,
    PlanModule,
    SubscriptionProfile,
    Transaction,
    BankTransfer,
    EnterpriseInquiry,
    Invoice,
    PaymentGateway,
    Discount,
    DiscountUsage,
    PaymentAttempt,
)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "audience", "is_active")
    list_filter = ("audience", "is_active")


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ("plan", "period", "amount", "currency", "is_active")
    list_filter = ("period", "currency", "is_active", "plan")
    search_fields = ("plan__name", "plan__code")


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")


@admin.register(PlanModule)
class PlanModuleAdmin(admin.ModelAdmin):
    list_display = ("plan", "module")


@admin.register(SubscriptionProfile)
class SubscriptionProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "current_period_end", "provider")
    list_filter = ("status", "provider", "plan")
    search_fields = ("user__username", "user__email", "plan__name", "plan__code")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "amount",
        "currency",
        "method",
        "status",
        "created_at",
    )
    list_filter = ("method", "status", "currency", "plan")
    search_fields = ("user__username", "user__email", "external_id")


@admin.register(BankTransfer)
class BankTransferAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "amount",
        "currency",
        "reference_code",
        "is_confirmed",
        "created_at",
    )
    list_filter = ("is_confirmed", "currency", "plan")
    search_fields = ("user__username", "user__email", "reference_code")


@admin.register(EnterpriseInquiry)
class EnterpriseInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "plan", "created_at")
    search_fields = ("name", "email", "company")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "subscription",
        "invoice_date",
        "due_date",
        "total_amount",
        "status",
        "paid_at",
    )
    search_fields = ("invoice_number", "subscription__user__username")
    list_filter = ("status", "invoice_date", "due_date")
    date_hierarchy = "invoice_date"
    readonly_fields = ("created_at", "updated_at")


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "gateway_type",
        "is_test_mode",
        "is_active",
        "total_transactions",
        "successful_transactions",
        "failed_transactions",
    )
    search_fields = ("name", "merchant_id")
    list_filter = ("gateway_type", "is_test_mode", "is_active")
    readonly_fields = (
        "total_transactions",
        "successful_transactions",
        "failed_transactions",
        "created_at",
        "updated_at",
    )


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "discount_type",
        "discount_value",
        "valid_from",
        "valid_until",
        "times_used",
        "is_active",
    )
    search_fields = ("code", "name")
    list_filter = ("discount_type", "is_active", "valid_from")
    filter_horizontal = ("applicable_plans",)
    readonly_fields = ("times_used", "created_at")


@admin.register(DiscountUsage)
class DiscountUsageAdmin(admin.ModelAdmin):
    list_display = (
        "discount",
        "user",
        "original_amount",
        "discount_amount",
        "final_amount",
        "used_at",
    )
    search_fields = ("discount__code", "user__username")
    list_filter = ("discount", "used_at")
    date_hierarchy = "used_at"
    readonly_fields = ("used_at",)


@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "transaction",
        "attempt_number",
        "status",
        "gateway",
        "response_code",
        "attempted_at",
    )
    search_fields = ("transaction__user__username", "error_message")
    list_filter = ("status", "gateway", "attempted_at")
    date_hierarchy = "attempted_at"
    readonly_fields = ("attempted_at",)
