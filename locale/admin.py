from django.contrib import admin
from .models import (
    Language,
    TranslationString,
    Translation,
    LocalizedContent,
    TranslationMemory,
    UserLanguagePreference,
    TranslationJob,
    LocaleAuditLog,
    MissingTranslation,
)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "native_name",
        "flag_emoji",
        "is_rtl",
        "is_active",
        "is_default",
        "translation_completeness",
        "order",
    )
    search_fields = ("code", "name", "native_name")
    list_filter = ("is_rtl", "is_active", "is_default")
    readonly_fields = ("translation_completeness", "created_at", "updated_at")
    actions = ["set_as_default"]

    def set_as_default(self, request, queryset):
        if queryset.count() == 1:
            lang = queryset.first()
            lang.is_default = True
            lang.save()
            self.message_user(request, f"{lang.name} varsayılan dil olarak ayarlandı.")
        else:
            self.message_user(request, "Sadece bir dil seçin.", level="error")

    set_as_default.short_description = "Varsayılan dil olarak ayarla"


@admin.register(TranslationString)
class TranslationStringAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "context",
        "module",
        "is_translated",
        "requires_review",
        "usage_count",
        "created_at",
    )
    search_fields = ("key", "source_text", "module")
    list_filter = ("context", "module", "is_translated", "requires_review")
    readonly_fields = ("usage_count", "last_used_at", "created_at", "updated_at")


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = (
        "translation_string",
        "language",
        "status",
        "is_machine_translated",
        "confidence_score",
        "translated_by",
        "reviewed_by",
    )
    search_fields = ("translation_string__key", "translated_text")
    list_filter = ("language", "status", "is_machine_translated", "reviewed_at")
    readonly_fields = ("created_at", "updated_at")
    actions = ["approve_translations", "mark_for_review"]

    def approve_translations(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(
            status="APPROVED", reviewed_by=request.user, reviewed_at=timezone.now()
        )
        self.message_user(request, f"{updated} çeviri onaylandı.")

    approve_translations.short_description = "Seçili çevirileri onayla"

    def mark_for_review(self, request, queryset):
        updated = queryset.update(status="REVIEW")
        self.message_user(request, f"{updated} çeviri incelemeye alındı.")

    mark_for_review.short_description = "İnceleme için işaretle"


@admin.register(LocalizedContent)
class LocalizedContentAdmin(admin.ModelAdmin):
    list_display = (
        "content_type",
        "object_id",
        "language",
        "field_name",
        "is_published",
        "updated_at",
    )
    search_fields = ("translated_value",)
    list_filter = ("language", "is_published", "content_type")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TranslationMemory)
class TranslationMemoryAdmin(admin.ModelAdmin):
    list_display = (
        "source_language",
        "target_language",
        "source_text_preview",
        "usage_count",
        "quality_score",
        "is_verified",
    )
    search_fields = ("source_text", "target_text")
    list_filter = ("source_language", "target_language", "is_verified", "domain")
    readonly_fields = ("usage_count", "last_used_at", "created_at")

    def source_text_preview(self, obj):
        return (
            obj.source_text[:50] + "..."
            if len(obj.source_text) > 50
            else obj.source_text
        )

    source_text_preview.short_description = "Kaynak Metin"


@admin.register(UserLanguagePreference)
class UserLanguagePreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "preferred_language",
        "timezone",
        "date_format",
        "auto_translate",
        "updated_at",
    )
    search_fields = ("user__username",)
    list_filter = ("preferred_language", "auto_translate", "timezone")
    readonly_fields = ("updated_at",)


@admin.register(TranslationJob)
class TranslationJobAdmin(admin.ModelAdmin):
    list_display = (
        "job_name",
        "source_language",
        "status",
        "progress_percentage",
        "total_items",
        "completed_items",
        "assigned_to",
        "created_at",
    )
    search_fields = ("job_name", "description")
    list_filter = ("status", "source_language", "created_at")
    filter_horizontal = ("target_languages",)
    readonly_fields = ("created_at", "started_at", "completed_at")


@admin.register(LocaleAuditLog)
class LocaleAuditLogAdmin(admin.ModelAdmin):
    list_display = ("translation", "action", "user", "created_at")
    search_fields = ("translation__translation_string__key", "comment")
    list_filter = ("action", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)


@admin.register(MissingTranslation)
class MissingTranslationAdmin(admin.ModelAdmin):
    list_display = (
        "translation_string",
        "language",
        "priority",
        "detected_in",
        "is_resolved",
        "detected_at",
    )
    search_fields = ("translation_string__key", "detected_in")
    list_filter = ("language", "priority", "is_resolved", "detected_at")
    date_hierarchy = "detected_at"
    actions = ["mark_as_resolved"]

    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(is_resolved=True, resolved_at=timezone.now())
        self.message_user(
            request, f"{updated} eksik çeviri çözüldü olarak işaretlendi."
        )

    mark_as_resolved.short_description = "Çözüldü olarak işaretle"
