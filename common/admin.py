from django.contrib import admin
from django.utils import timezone
from .models import (
    AuditLog,
    ApprovalRequest,
    SystemSetting,
    FileUpload,
    EmailTemplate,
    EmailLog,
    APIKey,
    Webhook,
    WebhookLog,
    ScheduledTask,
    BetaCampaign,
)

# Import Error Tracking Admin
from .admin_error_tracking import ErrorLogAdmin  # noqa: F401


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "content_type", "ip_address", "created_at")
    search_fields = ("action", "user__username", "ip_address")
    list_filter = ("action", "content_type", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = (
        "content_type",
        "status",
        "requested_by",
        "decided_by",
        "created_at",
    )
    search_fields = ("requested_by__username", "decided_by__username", "comment")
    list_filter = ("status", "created_at", "decided_at")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)
    actions = ["approve_requests", "reject_requests"]

    def approve_requests(self, request, queryset):
        for obj in queryset.filter(status="PENDING"):
            obj.approve(request.user, "Toplu onay")
        self.message_user(request, f"{queryset.count()} onay talebi onaylandı.")

    approve_requests.short_description = "Seçili talepleri onayla"

    def reject_requests(self, request, queryset):
        for obj in queryset.filter(status="PENDING"):
            obj.reject(request.user, "Toplu red")
        self.message_user(request, f"{queryset.count()} onay talebi reddedildi.")

    reject_requests.short_description = "Seçili talepleri reddet"


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "value",
        "value_type",
        "category",
        "is_public",
        "is_editable",
        "updated_at",
    )
    search_fields = ("key", "value", "description")
    list_filter = ("value_type", "category", "is_public", "is_editable")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Temel Bilgiler", {
            "fields": ("key", "value", "value_type", "description", "category")
        }),
        ("Ayarlar", {
            "fields": ("is_public", "is_editable")
        }),
        ("Metadata", {
            "fields": ("updated_by", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Kaydetme sırasında updated_by'ı set et"""
        if change:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = (
        "original_filename",
        "category",
        "file_size",
        "uploaded_by",
        "is_scanned",
        "is_safe",
        "is_public",
        "uploaded_at",
    )
    search_fields = ("original_filename", "description", "uploaded_by__username")
    list_filter = ("category", "is_scanned", "is_safe", "is_public", "uploaded_at")
    date_hierarchy = "uploaded_at"
    readonly_fields = ("uploaded_at", "access_count")


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "subject", "category", "is_active", "created_at")
    search_fields = ("name", "code", "subject")
    list_filter = ("category", "is_active", "created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = (
        "to_email",
        "subject",
        "status",
        "template",
        "sent_at",
        "opened_at",
        "created_at",
    )
    search_fields = ("to_email", "subject", "body")
    list_filter = ("status", "sent_at", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "sent_at", "opened_at", "clicked_at")


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "key",
        "is_active",
        "total_requests",
        "rate_limit",
        "last_used_at",
        "expires_at",
    )
    search_fields = ("name", "user__username", "key")
    list_filter = ("is_active", "created_at", "expires_at")
    readonly_fields = ("created_at", "total_requests", "last_used_at")
    actions = ["deactivate_keys"]

    def deactivate_keys(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} API anahtarı deaktif edildi.")

    deactivate_keys.short_description = "Seçili anahtarları deaktif et"


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "event_type",
        "url",
        "is_active",
        "user",
        "total_calls",
        "success_count",
        "failure_count",
        "last_called_at",
    )
    search_fields = ("name", "url", "user__username")
    list_filter = ("event_type", "is_active", "created_at")
    readonly_fields = (
        "total_calls",
        "success_count",
        "failure_count",
        "last_called_at",
        "created_at",
    )


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = (
        "webhook",
        "is_success",
        "response_status",
        "response_time_ms",
        "retry_count",
        "created_at",
    )
    search_fields = ("webhook__name", "error_message")
    list_filter = ("is_success", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)


@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "task_type",
        "status",
        "scheduled_at",
        "is_recurring",
        "created_by",
        "started_at",
        "completed_at",
    )
    search_fields = ("name", "result", "error_message")
    list_filter = ("task_type", "status", "is_recurring", "scheduled_at")
    date_hierarchy = "scheduled_at"
    readonly_fields = ("created_at", "started_at", "completed_at", "execution_time_ms")


@admin.register(BetaCampaign)
class BetaCampaignAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        "is_active",
        "discount_percent",
        "free_months",
        "company_shares",
        "publish_at",
        "start_date",
        "end_date",
        "show_on_homepage",
        "show_on_plans",
        "show_on_registration",
        "created_at",
    )
    list_filter = (
        "status",
        "is_active",
        "show_on_homepage",
        "show_on_plans",
        "show_on_registration",
        "publish_at",
        "start_date",
        "end_date",
        "created_at",
    )
    search_fields = ("name", "title", "description", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Temel Bilgiler", {
            "fields": ("name", "slug", "title", "description", "short_description")
        }),
        ("Kampanya Detayları", {
            "fields": (
                "discount_percent",
                "free_months",
                "company_shares",
                "includes_badge",
            )
        }),
        ("Zamanlama", {
            "fields": (
                "status",
                "is_active",
                "publish_at",
                "start_date",
                "end_date",
            ),
            "description": "publish_at: Kampanyanın yayınlanacağı tarih (zamanlanmış yayınlama)<br>"
                         "start_date: Kampanyanın başlayacağı tarih<br>"
                         "end_date: Kampanyanın biteceği tarih"
        }),
        ("Görünürlük", {
            "fields": (
                "show_on_homepage",
                "show_on_plans",
                "show_on_registration",
            )
        }),
        ("Metadata", {
            "fields": ("created_by", "updated_by", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Kaydetme sırasında created_by ve updated_by'ı set et"""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        
        # Status'u otomatik güncelle
        now = timezone.now()
        if obj.publish_at and now < obj.publish_at:
            obj.status = "scheduled"
        elif obj.status == "scheduled" and obj.publish_at and now >= obj.publish_at:
            obj.status = "active"
        elif obj.end_date and now > obj.end_date:
            obj.status = "ended"
        
        super().save_model(request, obj, form, change)
    
    actions = ["activate_campaigns", "deactivate_campaigns", "publish_now"]
    
    def activate_campaigns(self, request, queryset):
        """Seçili kampanyaları aktif et"""
        updated = queryset.update(status="active", is_active=True)
        self.message_user(request, f"{updated} kampanya aktif edildi.")
    activate_campaigns.short_description = "Seçili kampanyaları aktif et"
    
    def deactivate_campaigns(self, request, queryset):
        """Seçili kampanyaları deaktif et"""
        updated = queryset.update(status="paused", is_active=False)
        self.message_user(request, f"{updated} kampanya deaktif edildi.")
    deactivate_campaigns.short_description = "Seçili kampanyaları deaktif et"
    
    def publish_now(self, request, queryset):
        """Seçili kampanyaları hemen yayınla"""
        from django.utils import timezone
        updated = queryset.update(
            status="active",
            is_active=True,
            publish_at=timezone.now()
        )
        self.message_user(request, f"{updated} kampanya hemen yayınlandı.")
    publish_now.short_description = "Seçili kampanyaları hemen yayınla"
