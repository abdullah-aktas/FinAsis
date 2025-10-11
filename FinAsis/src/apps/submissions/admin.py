from django.contrib import admin, messages
from .models import Declaration, Submission, SubmissionLog
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
            except Exception as e:  # safety net, logs already recorded via SubmissionLog
                errors += 1
        if sent:
            messages.success(request, f"{sent} gönderim başlatıldı.")
        if errors:
            messages.error(request, f"{errors} gönderimde hata oluştu (detaylar loglarda).")
    send_to_gib_action.short_description = "Seçilenleri GİB'e gönder"


@admin.register(SubmissionLog)
class SubmissionLogAdmin(admin.ModelAdmin):
    list_display = ("submission", "level", "created_at")
    list_filter = ("level",)
    search_fields = ("message",)
