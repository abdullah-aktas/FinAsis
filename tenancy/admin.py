from django.contrib import admin
from .models import (
    Tenant,
    Company,
    UserTenantRole,
    TenantSettings,
    TenantUsage,
    TenantBilling,
    TenantAudit,
)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "created_at")
    search_fields = ("code", "name")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("tenant", "is_active", "created_at")
    readonly_fields = ("created_at",)


@admin.register(UserTenantRole)
class UserTenantRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "tenant", "role", "created_at")
    search_fields = ("user__username",)
    list_filter = ("role", "tenant", "created_at")
    readonly_fields = ("created_at",)


@admin.register(TenantSettings)
class TenantSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "tenant",
        "max_users",
        "max_storage_mb",
        "language",
        "timezone",
        "require_2fa",
    )
    search_fields = ("tenant__name", "contact_email")
    list_filter = ("require_2fa", "language")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TenantUsage)
class TenantUsageAdmin(admin.ModelAdmin):
    list_display = (
        "tenant",
        "date",
        "active_users",
        "storage_used_mb",
        "api_calls",
        "invoices_created",
        "reports_generated",
    )
    search_fields = ("tenant__name",)
    list_filter = ("date",)
    date_hierarchy = "date"
    readonly_fields = ("created_at",)


@admin.register(TenantBilling)
class TenantBillingAdmin(admin.ModelAdmin):
    list_display = (
        "tenant",
        "invoice_number",
        "billing_period_start",
        "billing_period_end",
        "total_amount",
        "status",
        "due_date",
    )
    search_fields = ("tenant__name", "invoice_number")
    list_filter = ("status", "due_date", "created_at")
    readonly_fields = ("created_at",)


@admin.register(TenantAudit)
class TenantAuditAdmin(admin.ModelAdmin):
    list_display = ("tenant", "action", "field_name", "user", "created_at")
    search_fields = ("tenant__name", "field_name")
    list_filter = ("action", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)
