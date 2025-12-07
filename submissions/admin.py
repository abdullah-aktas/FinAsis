from django.contrib import admin, messages
from .models import (
    Declaration,
    Submission,
    SubmissionLog,
    SubmissionTemplate,
    SubmissionAttachment,
    SubmissionApproval,
)
from .services import send_submission_to_gib


@admin.register(Declaration)
class DeclarationAdmin(admin.ModelAdmin):
    list_display = ("code", "period", "taxpayer_vkn_tckn", "created_at")
    search_fields = ("code", "period", "taxpayer_vkn_tckn")


class SubmissionLogInline(admin.TabularInline):
    model = SubmissionLog
    extra = 0
    readonly_fields = ("level", "message", "context", "created_at")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "declaration", "target", "status", "submitted_at")
    list_filter = ("target", "status")
    inlines = [SubmissionLogInline]
    actions = ["send_to_gib_action"]

    def send_to_gib_action(self, request, queryset):
        sent = 0
        errors = 0
        for sub in queryset:
            try:
                tracking, status = send_submission_to_gib(sub)
                sent += 1
            except Exception:  # safety net, logs already recorded via SubmissionLog
                errors += 1
        if sent:
            messages.success(request, f"{sent} gönderim başlatıldı.")
        if errors:
            messages.error(
                request, f"{errors} gönderimde hata oluştu (detaylar loglarda)."
            )

    send_to_gib_action.short_description = "Seçilenleri GİB'e gönder"


@admin.register(SubmissionLog)
class SubmissionLogAdmin(admin.ModelAdmin):
    list_display = ("submission", "level", "created_at")
    list_filter = ("level",)
    search_fields = ("message",)


@admin.register(SubmissionTemplate)
class SubmissionTemplateAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "version", "is_active", "created_by", "created_at")
    search_fields = ("code", "name", "description")
    list_filter = ("code", "is_active", "created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SubmissionAttachment)
class SubmissionAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "submission",
        "file_name",
        "file_type",
        "file_size",
        "uploaded_by",
        "uploaded_at",
    )
    search_fields = ("file_name", "description")
    list_filter = ("file_type", "uploaded_at")
    readonly_fields = ("uploaded_at",)


@admin.register(SubmissionApproval)
class SubmissionApprovalAdmin(admin.ModelAdmin):
    list_display = ("submission", "approver", "status", "requested_at", "responded_at")
    search_fields = ("comments", "revision_notes")
    list_filter = ("status", "requested_at")
    readonly_fields = ("requested_at",)
    actions = ["approve_submissions", "reject_submissions"]

    def approve_submissions(self, request, queryset):
        from django.utils import timezone

        updated = queryset.filter(status="PENDING").update(
            status="APPROVED", responded_at=timezone.now()
        )
        self.message_user(request, f"{updated} beyan onaylandı.")

    approve_submissions.short_description = "Seçili beyanları onayla"

    def reject_submissions(self, request, queryset):
        from django.utils import timezone

        updated = queryset.filter(status="PENDING").update(
            status="REJECTED", responded_at=timezone.now()
        )
        self.message_user(request, f"{updated} beyan reddedildi.")

    reject_submissions.short_description = "Seçili beyanları reddet"
