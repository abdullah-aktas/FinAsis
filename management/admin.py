from django.contrib import admin
from .models import ActionLog, Notification, HelpContent


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "timestamp")
    search_fields = ("user__username", "action", "detail")
    list_filter = ("action", "timestamp")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "created_at", "is_read")
    search_fields = ("user__username", "message")
    list_filter = ("is_read", "created_at")


@admin.register(HelpContent)
class HelpContentAdmin(admin.ModelAdmin):
    list_display = ("title", "role", "page_key", "updated_at")
    search_fields = ("title", "content", "role", "page_key")
    list_filter = ("role", "updated_at")


# ============================================================================
# YENİ YÖNETİM MODELLERİ - ADMIN KAYITLARI
# ============================================================================

from .models import (
    SystemHealth,
    PerformanceMetric,
    ErrorLog,
    BackupLog,
    SystemAudit,
    MaintenanceWindow,
    UsageStatistics,
    DatabaseSnapshot,
    FeatureFlag,
)


@admin.register(SystemHealth)
class SystemHealthAdmin(admin.ModelAdmin):
    list_display = (
        "checked_at",
        "overall_status",
        "cpu_usage",
        "memory_usage",
        "disk_usage",
        "active_users",
        "error_count",
    )
    list_filter = ("overall_status", "checked_at")
    readonly_fields = ("checked_at",)
    date_hierarchy = "checked_at"


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = (
        "metric_name",
        "metric_type",
        "value",
        "unit",
        "module",
        "is_healthy",
        "recorded_at",
    )
    search_fields = ("metric_name", "endpoint", "module")
    list_filter = ("metric_type", "is_healthy", "module", "recorded_at")
    date_hierarchy = "recorded_at"
    readonly_fields = ("recorded_at",)


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = (
        "severity",
        "error_type",
        "module",
        "user",
        "is_resolved",
        "occurred_at",
    )
    search_fields = ("error_type", "error_message", "module", "function")
    list_filter = ("severity", "is_resolved", "module", "occurred_at")
    date_hierarchy = "occurred_at"
    readonly_fields = ("occurred_at",)
    actions = ["mark_as_resolved"]

    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(
            is_resolved=True, resolved_at=timezone.now(), resolved_by=request.user
        )
        self.message_user(request, f"{updated} hata çözüldü olarak işaretlendi.")

    mark_as_resolved.short_description = "Seçili hataları çözüldü olarak işaretle"


@admin.register(BackupLog)
class BackupLogAdmin(admin.ModelAdmin):
    list_display = (
        "backup_name",
        "backup_type",
        "status",
        "file_size_mb",
        "duration_seconds",
        "started_at",
        "completed_at",
    )
    search_fields = ("backup_name", "file_path")
    list_filter = ("backup_type", "status", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)


@admin.register(SystemAudit)
class SystemAuditAdmin(admin.ModelAdmin):
    list_display = (
        "audit_name",
        "audit_type",
        "status",
        "compliance_score",
        "issues_found",
        "audit_date",
        "audited_by",
    )
    search_fields = ("audit_name", "description")
    list_filter = ("audit_type", "status", "audit_date")
    date_hierarchy = "audit_date"
    readonly_fields = ("created_at",)


@admin.register(MaintenanceWindow)
class MaintenanceWindowAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "start_time",
        "end_time",
        "estimated_duration_minutes",
        "notification_sent",
    )
    search_fields = ("title", "description")
    list_filter = ("status", "notify_users", "notification_sent", "start_time")
    date_hierarchy = "start_time"
    readonly_fields = ("created_at",)


@admin.register(UsageStatistics)
class UsageStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        "period_date",
        "period_type",
        "total_users",
        "active_users",
        "new_users",
        "total_sessions",
        "api_calls",
    )
    list_filter = ("period_type", "period_date")
    date_hierarchy = "period_date"
    readonly_fields = ("created_at",)


@admin.register(DatabaseSnapshot)
class DatabaseSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "snapshot_date",
        "total_size_mb",
        "table_count",
        "total_rows",
        "avg_query_time_ms",
        "optimization_needed",
    )
    list_filter = ("optimization_needed", "snapshot_date")
    date_hierarchy = "snapshot_date"
    readonly_fields = ("created_at",)


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "key",
        "module",
        "is_enabled",
        "enabled_for_all",
        "rollout_percentage",
        "created_by",
    )
    search_fields = ("name", "key", "description")
    list_filter = ("is_enabled", "enabled_for_all", "module", "created_at")
    filter_horizontal = ("enabled_for_users",)
    prepopulated_fields = {"key": ("name",)}
    readonly_fields = ("created_at", "updated_at")
