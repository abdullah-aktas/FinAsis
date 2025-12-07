from __future__ import annotations

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from . import models, services


@admin.register(models.PartnerCategory)
class PartnerCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "sort_order")
    search_fields = ("name", "code")
    ordering = ("sort_order", "name")


@admin.register(models.PartnerProfile)
class PartnerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "status",
        "is_featured",
        "sort_order",
        "updated_at",
    )
    list_filter = ("status", "category", "is_featured")
    search_fields = ("name", "slug", "headline", "description")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category",)
    ordering = ("sort_order", "name")


@admin.register(models.PartnerApplication)
class PartnerApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "partner_type",
        "status",
        "contact_name",
        "contact_email",
        "created_at",
    )
    list_filter = ("status", "partner_type", "created_at")
    search_fields = (
        "company_name",
        "contact_name",
        "contact_email",
        "integration_focus",
        "regions",
    )
    readonly_fields = ("created_at", "updated_at", "reviewed_at")
    fieldsets = (
        (
            _("Başvuru Bilgileri"),
            {
                "fields": (
                    "company_name",
                    "partner_type",
                    "integration_focus",
                    "target_customer_segments",
                    "regions",
                    "go_to_market_plan",
                )
            },
        ),
        (
            _("İletişim"),
            {
                "fields": (
                    "contact_name",
                    "contact_email",
                    "contact_phone",
                    "website_url",
                    "sandbox_url",
                )
            },
        ),
        (
            _("Uyumluluk ve Notlar"),
            {"fields": ("compliance_notes", "additional_notes", "metadata")},
        ),
        (
            _("Durum"),
            {
                "fields": (
                    "status",
                    "submitted_by",
                    "reviewed_by",
                    "reviewed_at",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    autocomplete_fields = ("submitted_by", "reviewed_by")
    actions = (
        "mark_as_reviewing",
        "mark_as_approved",
        "mark_as_rejected",
        "approve_and_publish",
    )

    @admin.action(description=_("Seçili başvuruları incelemeye al"))
    def mark_as_reviewing(self, request, queryset):
        updated = 0
        for application in queryset:
            if services.transition_application(
                application,
                status=models.PartnerApplication.Status.REVIEWING,
                reviewer=request.user,
            ):
                updated += 1
        if updated:
            self.message_user(
                request,
                _("{} başvuru incelemeye alındı.").format(updated),
                level=messages.SUCCESS,
            )

    @admin.action(description=_("Seçili başvuruları onayla (taslak profil oluştur)"))
    def mark_as_approved(self, request, queryset):
        created_profiles = 0
        for application in queryset:
            result = services.approve_application(
                application,
                reviewer=request.user,
                publish=False,
            )
            if result.profile_created:
                created_profiles += 1
        if created_profiles:
            self.message_user(
                request,
                _("{} başvuru için taslak partner profili oluşturuldu.").format(
                    created_profiles
                ),
                level=messages.SUCCESS,
            )

    @admin.action(description=_("Seçili başvuruları reddet"))
    def mark_as_rejected(self, request, queryset):
        rejected = 0
        for application in queryset:
            if services.reject_application(
                application,
                reviewer=request.user,
            ):
                rejected += 1
        if rejected:
            self.message_user(
                request,
                _("{} başvuru reddedildi.").format(rejected),
                level=messages.WARNING,
            )

    @admin.action(description=_("Seçili başvuruları onayla ve yayınla"))
    def approve_and_publish(self, request, queryset):
        published = 0
        for application in queryset:
            result = services.approve_application(
                application,
                reviewer=request.user,
                publish=True,
            )
            if (
                result.profile_created
                and result.profile.status == models.PartnerProfile.Status.PUBLISHED
            ):
                published += 1
        if published:
            self.message_user(
                request,
                _("{} partner profili yayınlandı.").format(published),
                level=messages.SUCCESS,
            )
