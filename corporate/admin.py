from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    ContactMessage,
    InvestorDocument,
    PartnerApplication,
    PartnerApplicationEvent,
    PartnerCategory,
    PartnerListing,
    PressRelease,
    TeamMember,
)


@admin.register(PressRelease)
class PressReleaseAdmin(admin.ModelAdmin):
    list_display = ("title", "date")
    search_fields = ("title",)
    list_filter = ("date",)


@admin.register(InvestorDocument)
class InvestorDocumentAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "published_at")
    list_filter = ("kind",)
    search_fields = ("name",)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "department")
    list_filter = ("department",)
    search_fields = ("name", "role")


@admin.register(PartnerCategory)
class PartnerCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "priority")
    list_editable = ("is_active", "priority")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")
    list_filter = ("is_active",)


@admin.register(PartnerListing)
class PartnerListingAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "status",
        "is_featured",
        "feature_order",
        "updated_at",
    )
    list_filter = ("status", "is_featured", "category")
    search_fields = ("name", "slug", "summary")
    list_editable = ("is_featured", "feature_order", "status")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category",)
    fieldsets = (
        (
            _("Genel Bilgiler"),
            {"fields": ("name", "slug", "tagline", "summary", "description")},
        ),
        (_("Kategori ve Etiket"), {"fields": ("category", "badge_label")}),
        (
            _("İçerik"),
            {
                "fields": (
                    "website",
                    "contact_email",
                    "logo_url",
                    "capabilities",
                    "integrations",
                    "regions",
                )
            },
        ),
        (_("CTA"), {"fields": ("cta_label", "cta_url")}),
        (_("Durum"), {"fields": ("status", "is_featured", "feature_order")}),
    )


class PartnerApplicationEventInline(admin.TabularInline):
    model = PartnerApplicationEvent
    extra = 0
    readonly_fields = (
        "action",
        "notes",
        "from_status",
        "to_status",
        "actor",
        "created_at",
    )


@admin.register(PartnerApplication)
class PartnerApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "contact_name",
        "status",
        "created_at",
        "assigned_to",
    )
    list_filter = ("status", "created_at", "primary_category", "categories")
    search_fields = ("company_name", "contact_name", "contact_email")
    autocomplete_fields = ("primary_category", "categories", "assigned_to")
    readonly_fields = ("created_at", "updated_at", "reviewed_at")
    inlines = (PartnerApplicationEventInline,)
    fieldsets = (
        (
            _("Şirket"),
            {
                "fields": (
                    "company_name",
                    "brand_name",
                    "website",
                    "country",
                    "city",
                    "team_size",
                )
            },
        ),
        (
            _("İletişim"),
            {"fields": ("contact_name", "contact_email", "contact_phone", "job_title")},
        ),
        (
            _("Uyum ve Entegrasyon"),
            {"fields": ("primary_category", "categories", "integration_focus")},
        ),
        (
            _("Detaylar"),
            {
                "fields": (
                    "product_notes",
                    "message",
                    "go_live_timeline",
                    "revenue_model",
                    "sandbox_needs",
                )
            },
        ),
        (
            _("Durum"),
            {"fields": ("status", "assigned_to", "decision_notes", "reviewed_at")},
        ),
        (_("Zaman Damgaları"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(PartnerApplicationEvent)
class PartnerApplicationEventAdmin(admin.ModelAdmin):
    list_display = (
        "application",
        "action",
        "from_status",
        "to_status",
        "actor",
        "created_at",
    )
    list_filter = ("action", "from_status", "to_status", "created_at")
    search_fields = ("application__company_name", "notes")
    autocomplete_fields = ("application", "actor")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "subject",
        "company",
        "phone",
        "created_at",
        "is_resolved",
        "handled_by",
    )
    list_filter = ("subject", "is_resolved", "created_at", "consent_gdpr")
    search_fields = ("name", "email", "company", "phone", "message")
    readonly_fields = (
        "name",
        "email",
        "company",
        "phone",
        "subject",
        "message",
        "created_at",
    )
    autocomplete_fields = ("handled_by",)
    fieldsets = (
        (
            _("Gönderen"),
            {"fields": ("name", "email", "company", "phone", "source", "created_at")},
        ),
        (_("Mesaj"), {"fields": ("subject", "message", "consent_gdpr")}),
        (
            _("İç takip"),
            {"fields": ("is_resolved", "handled_by", "handled_at", "notes")},
        ),
    )
