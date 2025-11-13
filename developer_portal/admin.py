from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from developer_portal.models import (
    APIKeyUsageLog,
    DeveloperAPIKey,
    DeveloperPortalAuditLog,
    WebhookTestLog,
)


@admin.register(DeveloperAPIKey)
class DeveloperAPIKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "organization", "rate_limit_plan", "status", "created_at")
    list_filter = ("status", "rate_limit_plan", "organization")
    search_fields = ("name", "owner__email", "owner__username", "prefix")
    readonly_fields = ("prefix", "masked_key", "created_at", "updated_at", "last_used_at")
    fieldsets = (
        (_("Genel"), {"fields": ("name", "description", "owner", "organization")}),
        (
            _("Anahtar Bilgisi"),
            {
                "fields": (
                    "prefix",
                    "masked_key",
                    "rate_limit_plan",
                    "allowed_ips",
                    "status",
                    "expires_at",
                    "last_used_at",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def masked_key(self, obj: DeveloperAPIKey) -> str:
        return format_html("<code>{}</code>", obj.masked_key)


@admin.register(APIKeyUsageLog)
class APIKeyUsageLogAdmin(admin.ModelAdmin):
    list_display = ("api_key", "path", "method", "response_code", "duration_ms", "timestamp")
    list_filter = ("method", "response_code")
    search_fields = ("api_key__name", "path", "client_ip")
    date_hierarchy = "timestamp"


@admin.register(DeveloperPortalAuditLog)
class DeveloperPortalAuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "api_key", "created_at")
    search_fields = ("action", "actor__email", "api_key__name")
    date_hierarchy = "created_at"


@admin.register(WebhookTestLog)
class WebhookTestLogAdmin(admin.ModelAdmin):
    list_display = ("event_type", "target_url", "response_status", "duration_ms", "created_at")
    search_fields = ("event_type", "target_url", "error")
    list_filter = ("event_type", "response_status")
    date_hierarchy = "created_at"

