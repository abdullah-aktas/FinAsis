from django.contrib import admin
from .models import SecurityPolicy, SecurityIncident, IPWhitelist, IPBlacklist


@admin.register(SecurityPolicy)
class SecurityPolicyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "policy_type",
        "is_active",
        "is_enforced",
        "priority",
        "created_by",
        "created_at",
    )
    search_fields = ("name", "description")
    list_filter = ("policy_type", "is_active", "is_enforced", "created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SecurityIncident)
class SecurityIncidentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "incident_type",
        "severity",
        "source_ip",
        "affected_user",
        "is_resolved",
        "detected_at",
    )
    search_fields = ("title", "description", "source_ip")
    list_filter = ("incident_type", "severity", "is_resolved", "detected_at")
    date_hierarchy = "detected_at"
    readonly_fields = ("detected_at",)
    actions = ["mark_as_resolved"]

    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(
            is_resolved=True, resolved_at=timezone.now(), resolved_by=request.user
        )
        self.message_user(
            request, f"{updated} güvenlik olayı çözüldü olarak işaretlendi."
        )

    mark_as_resolved.short_description = "Çözüldü olarak işaretle"


@admin.register(IPWhitelist)
class IPWhitelistAdmin(admin.ModelAdmin):
    list_display = (
        "ip_address",
        "description",
        "user",
        "is_active",
        "usage_count",
        "last_used_at",
        "valid_until",
    )
    search_fields = ("ip_address", "description")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("usage_count", "last_used_at", "created_at")


@admin.register(IPBlacklist)
class IPBlacklistAdmin(admin.ModelAdmin):
    list_display = (
        "ip_address",
        "reason",
        "blocked_attempts",
        "is_active",
        "first_blocked_at",
        "auto_unblock_at",
    )
    search_fields = ("ip_address", "description")
    list_filter = ("reason", "is_active", "first_blocked_at")
    readonly_fields = ("first_blocked_at", "created_at")
    actions = ["activate_blacklist", "deactivate_blacklist"]

    def activate_blacklist(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} IP adresi aktif edildi.")

    activate_blacklist.short_description = "Engellemeyi aktif et"

    def deactivate_blacklist(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} IP adresi engeli kaldırıldı.")

    deactivate_blacklist.short_description = "Engellemeyi kaldır"
