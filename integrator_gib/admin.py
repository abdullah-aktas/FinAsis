from django.contrib import admin
from .models import IntegratorConfig, AccessToken, GIBSubmissionLog, GIBCertificate


@admin.register(IntegratorConfig)
class IntegratorConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "base_url", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "base_url")


@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ("integrator", "expires_at", "created_at")
    autocomplete_fields = ("integrator",)


@admin.register(GIBSubmissionLog)
class GIBSubmissionLogAdmin(admin.ModelAdmin):
    list_display = (
        "submission_id",
        "declaration_code",
        "period",
        "taxpayer_vkn",
        "status",
        "gib_reference_number",
        "submitted_at",
    )
    search_fields = (
        "submission_id",
        "taxpayer_vkn",
        "gib_reference_number",
        "gib_tracking_id",
    )
    list_filter = ("status", "declaration_code", "submitted_at")
    date_hierarchy = "submitted_at"
    readonly_fields = ("submitted_at", "processed_at")


@admin.register(GIBCertificate)
class GIBCertificateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "certificate_type",
        "serial_number",
        "valid_from",
        "valid_until",
        "is_active",
        "usage_count",
    )
    search_fields = ("name", "serial_number", "alias")
    list_filter = ("certificate_type", "is_active", "valid_until")
    date_hierarchy = "valid_until"
    readonly_fields = ("usage_count", "last_used_at", "created_at")
