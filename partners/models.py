from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class PartnerCategory(models.Model):
    code = models.SlugField(_("Kategori Kodu"), max_length=50, unique=True)
    name = models.CharField(_("Kategori Adı"), max_length=150)
    description = models.TextField(_("Açıklama"), blank=True)
    icon = models.CharField(_("Simge"), max_length=100, blank=True)
    sort_order = models.PositiveIntegerField(_("Sıra"), default=0)

    class Meta:
        ordering = ("sort_order", "name")
        verbose_name = _("Partner Kategorisi")
        verbose_name_plural = _("Partner Kategorileri")

    def __str__(self) -> str:
        return self.name


class PartnerProfile(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Taslak")
        REVIEW = "review", _("İncelemede")
        PUBLISHED = "published", _("Yayında")
        ARCHIVED = "archived", _("Arşivlendi")

    category = models.ForeignKey(
        PartnerCategory,
        on_delete=models.PROTECT,
        related_name="partners",
        verbose_name=_("Kategori"),
    )
    name = models.CharField(_("Partner Adı"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=200, unique=True)
    headline = models.CharField(_("Kısa Başlık"), max_length=200, blank=True)
    description = models.TextField(_("Açıklama"))
    integration_focus = models.CharField(
        _("Entegrasyon Odağı"), max_length=200, blank=True
    )
    website_url = models.URLField(_("Web Sitesi"), blank=True)
    contact_email = models.EmailField(_("İletişim E-postası"), blank=True)
    badge_label = models.CharField(_("Rozet"), max_length=100, blank=True)
    regions = models.CharField(_("Hizmet Bölgeleri"), max_length=200, blank=True)
    status = models.CharField(
        _("Durum"), max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    is_featured = models.BooleanField(_("Öne Çıkan"), default=False)
    sort_order = models.PositiveIntegerField(_("Sıra"), default=0)
    created_at = models.DateTimeField(_("Oluşturma"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncelleme"), auto_now=True)

    class Meta:
        ordering = ("sort_order", "name")
        verbose_name = _("Partner Profili")
        verbose_name_plural = _("Partner Profilleri")

    def __str__(self) -> str:
        return self.name


def default_metadata() -> dict[str, str]:
    return {}


class PartnerApplication(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "received", _("Alındı")
        REVIEWING = "reviewing", _("İnceleniyor")
        APPROVED = "approved", _("Onaylandı")
        REJECTED = "rejected", _("Reddedildi")

    PARTNER_TYPES = (
        ("erp", _("ERP Entegratörü")),
        ("crm", _("CRM / Satış Otomasyonu")),
        ("compliance", _("Uyumluluk / RegTech")),
        ("education", _("Eğitim / LMS")),
        ("payment", _("Ödeme / FinTech")),
        ("consulting", _("Danışmanlık")),
        ("other", _("Diğer")),
    )

    company_name = models.CharField(_("Şirket Adı"), max_length=200)
    contact_name = models.CharField(_("İletişim Kişisi"), max_length=120)
    contact_email = models.EmailField(_("E-posta"))
    contact_phone = models.CharField(_("Telefon"), max_length=50, blank=True)
    website_url = models.URLField(_("Web Sitesi"), blank=True)
    partner_type = models.CharField(
        _("Partner Tipi"), max_length=20, choices=PARTNER_TYPES
    )
    integration_focus = models.CharField(
        _("Entegrasyon Odağı"),
        max_length=200,
        help_text=_("Örn. e-Fatura, muhasebe, eğitim içeriği"),
    )
    target_customer_segments = models.CharField(
        _("Hedef Müşteri Segmentleri"), max_length=200, blank=True
    )
    regions = models.CharField(_("Hizmet Verilen Bölgeler"), max_length=200, blank=True)
    sandbox_url = models.URLField(_("Sandbox / Demo URL"), blank=True)
    compliance_notes = models.TextField(
        _("Uyumluluk Notları"),
        blank=True,
        help_text=_("Sertifikalar, KVKK uyumluluğu, güvenlik uygulamaları"),
    )
    go_to_market_plan = models.TextField(
        _("Pazara Giriş Planı"), blank=True, help_text=_("Ortak kampanyalar, hedefler")
    )
    additional_notes = models.TextField(_("Ek Notlar"), blank=True)
    status = models.CharField(
        _("Durum"), max_length=20, choices=Status.choices, default=Status.RECEIVED
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="partner_portal_submissions",
        verbose_name=_("Gönderen Kullanıcı"),
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="partner_portal_reviews",
        verbose_name=_("İnceleyen"),
    )
    reviewed_at = models.DateTimeField(_("İnceleme Tarihi"), null=True, blank=True)
    metadata = models.JSONField(_("Ek Veriler"), default=default_metadata, blank=True)
    created_at = models.DateTimeField(_("Gönderim Tarihi"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Güncelleme Tarihi"), auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Partner Başvurusu")
        verbose_name_plural = _("Partner Başvuruları")
        indexes = [
            models.Index(fields=("status", "created_at")),
            models.Index(fields=("partner_type",)),
        ]

    def __str__(self) -> str:
        return f"{self.company_name} · {self.contact_name}"

    def mark_reviewed(self, *, reviewer, status: str, notes: str | None = None) -> None:
        self.status = status
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        if notes:
            self.metadata.setdefault("review_notes", notes)
        self.save(update_fields=["status", "reviewed_by", "reviewed_at", "metadata"])
